from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from .models import Category, MenuItem, Cart, Order, OrderItem
from decimal import Decimal
#from markupsafe import escape
from django.contrib.auth.models import User, Group


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )
    def validate(self, attrs):
        #attrs['title'] = escape('title')
        if (attrs['price']<1): 
            raise serializers.ValidationError('Price should not be less than $1')
        return super().validate(attrs)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        extra_kwargs = {
            'title': {
                'validators' : [
                    UniqueValidator(
                        queryset=MenuItem.objects.all()
                    )
                ]
            }
        }
        depth = 1

class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['pk', 'username']

class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField( 
        queryset=User.objects.all(), 
        default=serializers.CurrentUserDefault() 
    )
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    # menuitem = serializers.PrimaryKeyRelatedField(
    #     queryset=MenuItem.objects.all()
    # )
    # price = serializers.SerializerMethodField()
    
    class Meta():
        model = Cart
        fields = ['id', 'user', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Cart.objects.all(),
        #         fields=['user', 'menuitem']
        #     )
        # ]
    # def get_price(self, product:Cart):
    #     return product.unit_price * product.quantity
    
    # def create(self, validated_data):
    #     price = validated_data['unit_price'] * validated_data['quantity']
    #     validated_data['price'] = price
    #     return Cart.objects.create(**validated_data)
    
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField( 
        queryset=User.objects.all(), 
        default=serializers.CurrentUserDefault() 
    )
    delivery_crew = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )
    status = serializers.BooleanField()
    class Meta():
        model = Order
        fields = ['pk', 'user', 'delivery_crew', 'status', 'total', 'date']
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['pk', 'order', 'menuitem', 'quantity', 'unit_price', 'price']