from django.shortcuts import get_object_or_404
from .serializers import CategorySerializer, MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .models import Category, MenuItem, Cart, Order, OrderItem
from .permissions import IsManagerOrReadOnly, ReadOnly, IsManager, IsDelivery, IsOrderPermission
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import permission_classes, api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status, permissions
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, EmptyPage
from decimal import Decimal
from datetime import date

class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsManagerOrReadOnly]

class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsManagerOrReadOnly]

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['featured','category','price']
    search_fields = ['title','category__slug']
    permission_classes = [IsManagerOrReadOnly]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]

class SingleDeliveryView(generics.RetrieveDestroyAPIView):
    queryset = User.objects.filter(groups=2)
    serializer_class = UserSerializer
    permission_class = [IsAuthenticated, IsManager]
 
@api_view(['GET', 'POST'])
@permission_classes([IsManager])
def managers(request):
    username = request.data['username']
    if request.method == 'GET':
        items = User.objects.filter(groups=1)
        serialized_item = UserSerializer(items, many=True, context={'request': request})
        return Response(serialized_item.data)
    elif username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name='Managers')
        managers.user_set.add(user)
        return Response({'message': 'Manager added'}, status.HTTP_201_CREATED)
    
    return Response({'message': 'error'}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsManager])
def delivery_crew(request):
    username = request.data['username']
    if request.method == 'GET':
        items = User.objects.filter(groups=2)
        serialized_item = UserSerializer(items, many=True, context={'request': request})
        return Response(serialized_item.data)
    elif username:
        user = get_object_or_404(User, username=username)
        delivery_crew = Group.objects.get(name='Delivery Crew')
        delivery_crew.user_set.add(user)
        return Response({'message': 'Delivery crew member added'}, status.HTTP_201_CREATED)
    
    return Response({'message': 'error'}, status.HTTP_400_BAD_REQUEST)

class SingleManagerView(generics.RetrieveDestroyAPIView):
    queryset = User.objects.filter(groups=1)
    serializer_class = UserSerializer
    permission_class = [IsAuthenticated, IsManager]
    
class SingleDeliveryView(generics.RetrieveDestroyAPIView):
    queryset = User.objects.filter(groups=2)
    serializer_class = UserSerializer
    permission_class = [IsAuthenticated, IsManager]


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart(request):
    #user = self.request.user
    if request.method == 'GET':
        cart = get_object_or_404(Cart, user=request.user)
        #items = Cart.objects.filter(pk=1)
        serialized_item = CartSerializer(cart)#, many=True, context={'request': request})
        return Response(serialized_item.data)
    elif request.method == 'POST':
        menu_item = MenuItem.objects.get(pk=request.data['menuitem_id'])
        new_cart = Cart.objects.update_or_create(
            user=request.user,
            menuitem=menu_item,
            menuitem_id=request.data['menuitem_id'],
            quantity=request.data['quantity'],
            unit_price=menu_item.price,
            price=menu_item.price * Decimal(request.data['quantity']),
        )
        return Response({'message': 'Menu item added'}, status.HTTP_200_OK)
    elif request.method == 'DELETE':
        cart = get_object_or_404(Cart, user=request.user)
        cart.delete()
        return Response({'message': 'Cart is empty'}, status.HTTP_200_OK)
    
    return Response({'message': 'error'}, status.HTTP_400_BAD_REQUEST)
        



class OrderView(generics.ListCreateAPIView):
    model = Order
    queryset = model.objects.all()
    serializer_class = OrderSerializer
    permissions = IsOrderPermission
    ordering = ['-date']
    
    # def check_permissions(self, request):
    #     if request.method in ['GET']:
    #         self.permission_classes=[IsAuthenticated | IsDelivery]
    #     elif request.method in ['POST']:
    #         self.permission_classes = [IsAuthenticated]
    #     else:
    #         self.permission_classes = [IsManager]
    #     return super().check_permissions(request)
    
    def get(self, request, *args, **kwargs):
        self.queryset = Order.objects.all()
        if request.user.groups.filter(name='Delivery Crew').exists():
            self.queryset = self.queryset.filter(delivery_crew=request.user)
        elif not request.user.groups.filter(name="Manager").exists():
            self.queryset = self.queryset.filter(user=request.user)
        # if request.user.groups.filter(name="Manager").exists():
        #     self.queryset = Order.objects.all()
        #     print(self.queryset)
        # elif request.user.groups.filter(name='Delivery Crew').exists():
        #     self.queryset = self.queryset.filter(delivery_crew=request.user)
        # else:
        #     self.queryset = self.queryset.filter(user=request.user)
        return super().get(request, *args, **kwargs)
    
    def post(self, request):
        existing_cart = Cart.objects.filter(user=request.user).exists()
        if existing_cart:
            cart = Cart.objects.get(user=request.user)
            serialized_item=CartSerializer(cart)
            serialized_data = serialized_item.data
            print('serialized cart', serialized_data)
            print('serialized data', serialized_data['menuitem']['id'])
            new_order = Order.objects.create(
                user=request.user,
                #delivery_crew=None,
                status=0,
                total=serialized_data['price'],
                date=date.today(),
            )
            print('new order created:', new_order)
            
            menu_item_id = serialized_data['menuitem']['id']
            menu_item = MenuItem.objects.get(id=menu_item_id)
            print('menu item:', menu_item)
            
            OrderItem.objects.create(
                order=new_order,
                menuitem=menu_item,
                quantity=serialized_data['quantity'],
                unit_price=serialized_data['unit_price'],
                price=serialized_data['price'],
            )
            cart.delete()
            serialized_item = OrderSerializer(new_order)
            return Response(serialized_item.data)
        else:
            return Response({'message': 'no shopping cart found'}, status.HTTP_404_NOT_FOUND)
        

# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def orders(request):
#     if request.method == 'GET':
#         if request.user.groups.filter(name="Manager").exists():
#             orders = Order.objects.all()
#             serialized_item = OrderSerializer(orders, many=True)
#             return Response(serialized_item.data)
#         # elif request.user.groups.filter(name='Delivery Crew').exists():
#         #     orders = Order.objects.filter(order__delivery_crew=request.user)
#         #     serialized_item = OrderSerializer(orders, many=True)
#         #     return Response(serialized_item.data)
#         # else:
#         #     orders = Order.objects.filter(user=request.user)
#         #     serialized_item = OrderSerializer(orders, many=True)
#         #     return Response(serialized_item.data)
        
        
#     if request.method == 'POST':
#         existing_cart = Cart.objects.filter(user=request.user).exists()
#         if existing_cart:
#             cart = Cart.objects.get(user=request.user)
#             serialized_item=CartSerializer(cart)
#             serialized_data = serialized_item.data
#             print('serialized cart', serialized_data)
#             print('serialized data', serialized_data['menuitem']['id'])
#             new_order = Order.objects.create(
#                 user=request.user,
#                 #delivery_crew=None,
#                 status=0,
#                 total=serialized_data['price'],
#                 date=date.today(),
#             )
#             print('new order created:', new_order)
            
#             menu_item_id = serialized_data['menuitem']['id']
#             menu_item = MenuItem.objects.get(id=menu_item_id)
#             print('menu item:', menu_item)
            
#             OrderItem.objects.create(
#                 order=new_order,
#                 menuitem=menu_item,
#                 quantity=serialized_data['quantity'],
#                 unit_price=serialized_data['unit_price'],
#                 price=serialized_data['price'],
#             )
#             cart.delete()
#             serialized_item = OrderSerializer(new_order)
#             return Response(serialized_item.data)
#         else:
#             return Response({'message': 'no shopping cart found'}, status.HTTP_404_NOT_FOUND)
    
    
    
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsOrderPermission])
def orderitems(request, pk):
    if request.method == 'GET':
        order_items = OrderItem.objects.filter(order__user=request.user, order__pk=pk)
        if order_items:
            serialized_item = OrderItemSerializer(order_items, many=True)
            return Response(serialized_item.data)
        else: 
            return Response({'message': 'No order found'}, status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        order = get_object_or_404(Order, pk=pk)
        serialized_item = OrderSerializer(
            order, data=request.data, context={'request':request}
        )
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data)
    if request.method == 'PATCH':
        order = get_object_or_404(Order, pk=pk)
        serialized_item = OrderSerializer(
            order, data = request.data, partial = True, context={'request': request}
        )
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data)
       
    if request.method == 'DELETE': 
        order = get_object_or_404(order, pk=pk)
        order.delete()
        return Response({'message': 'Order deleted'}, status.HTTP_200_OK)
    
# @api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
# def orderitems(request):
#     if request.method == 'PATCH':
#         order = OrderItem.objects.filter(pk=request.data['order_id'])
#         status = request.data['status']
#     return Response({'message': 'Delivery crew assigned'}, status.HTTP_200_OK)
   
# delivery_crew = request.data['delivery_crew']
#         status = request.data['status']
#         return Response({'message': 'Delivery crew assigned'}, status.HTTP_200_OK) 
    
    # @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsDelivery])
# def orders(request):
#     if request.method == 'GET':
#         assigned_orders = Order.objects.filter(delivery_crew != None)
#         serialized_item = OrderSerializer(assigned_orders, many=True)
#         return Response(serialized_item.data)

#     return Response({'message': 'error'}, status.HTTP_400_BAD_REQUEST)
    
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def orderitems(request):
#     if request.method == 'GET':
#         orders = Order.objects.filter(order_id=request.id)
#         serialized_item = OrderItemSerializer(orders, many=True)
#         return Response(serialized_item.data)
    
#     return Response({'message': 'error'}, status.HTTP_400_BAD_REQUEST)    

# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsManager])
# def orders(request):
#     if request.method == 'GET':
#         orders = Order.objects.all()
#         serialized_item = OrderSerializer(orders, many=True)
#         return Response(serialized_item.data)

# order = get_object_or_404(Order, user=user)
#         serialized_item = OrderSerializer(order)
#         return Response(serialized_item.data)
    
#     return Response({'message': 'error'}, status.HTTP_400_BAD_REQUEST)

#order = get_object_or_404(Cart, user=request.user)
        # serialized_item = OrderItemSerializer(order)
        # order.save()
        # return Response({'message': 'Order submitted'}, status.HTTP_200_OK)
    
    
#@api_view()
    
# @api_view(['GET'])
#     if request.method == 'PUT' | 'PATCH':
#         delivery_crew = request.data['delivery_crew']
#         status = request.data['status']
#         return Response({'message': 'Delivery crew assigned'}, status.HTTP_200_OK)
#     if request.method == 'DELETE': 

        
    
# class CategoryView(viewsets.ModelViewSet):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer


# @api_view(['GET', 'POST', 'PUT', 'DELETE'])
# #@permission_classes([[permissions.IsAuthenticated], IsAuthenticated])
# def managers(request):
#     username = request.data['username']
#     if username:
#         user = get_object_or_404(User, username=username)
#         managers=Group.objects.get(name='Manager')
#         managers.user_set.add(user)
#         return Response({'message': 'ok'})
    
#     return Response({'message': 'error'}, status=status.HTTP_400_BAD_REQUEST)



# @api_view(['GET', 'POST', 'PUT', 'DELETE'])
# @permission_classes([IsAuthenticated])
# # def 

# class ManagerGroupView(generics.ListAPIView):
#     queryset = User.objects.filter(groups=1)
#     serializer_class = UserSerializer
#     permission_class = [IsAuthenticated, IsManager]

# class DeliveryGroupView(generics.ListAPIView):
#     queryset = User.objects.filter(groups=2)
#     serializer_class = UserSerializer
#     permission_class = [IsAuthenticated, IsManager]


# 
# if request.method == 'POST':
#         menu_item = MenuItem.objects.get(pk=request.data['menuitem_id'])
#         cart, created = Cart.objects.get_or_create(
#             user=request.user,
#             menuitem=menu_item,
#             menuitem_id=request.data['menuitem_id'],
#             quantity=request.data['quantity'],
#             unit_price=menu_item.price,
#             price=menu_item.price * Decimal(request.data['quantity']),
#         )
#         if not created:
#             menu_item = MenuItem.objects.get(pk=request.data['menuitem_id'])
#             cart.quantity = request.data['quantity']
#             cart.price += menu_item.price
#             cart.save(menu_item)

# else: 
        #     return Response({'message': 'No order items found'}, status.HTTP_404_NOT_FOUND)
        
        # order_items = OrderItem.objects.all()
        # if not request.user.groups.filter(name="Manager").exists():
        #     order_items = order_items.filter(order__user=request.user)
        # if order_items.exists():
        #     serialized_item = OrderItemSerializer(order_items, many=True)
        #     return Response(serialized_item.data)
        # else:
        #     return Response({'message': 'No orders found'}, status.HTTP_404_NOT_FOUND)  
            
        # if request.user.groups.filter(name="Manager").exists():
        #     order_item = OrderItem.objects.all
        # elif request.user.groups.filter(name='Delivery Crew').exists():
        #     order_item = OrderItem.objects.filter(order__delivery_crew=request.user)
        # else: 
        #     order_item = OrderItem.objects.filter(order__user=request.user)
        # if order_item.exists():
        #     serialized_item = OrderItemSerializer(order_item, many=True)
        #     return Response(serialized_item.data)
        # else:
        #     return Response({'message': 'No orders found'}, status.HTTP_404_NOT_FOUND)
        
        
        # class OrderView(generics.ListCreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     ordering_fields = ['date','status']
#     search_fields = ['date','status']
    
# class OrderItemView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = OrderItem.objects.all()
#     serializer_class = MenuItemSerializer

        # order = request.data['menuitem']
        # cart = Cart.objects.all()
        # cart.order_set.add(order)
        #new_cart.save()
        
         # elif request.user.groups.filter(name='Delivery Crew').exists():
        #     order = Order.objects.filter(pk=pk)
        #     order.update(status=request.data['status'])
        #     serialized_item = OrderSerializer(order, many=True)
        #     return Response(serialized_item.data)
        # else:
        #     return Response({'message': 'forbidden'}, status.HTTP_403_FORBIDDEN)