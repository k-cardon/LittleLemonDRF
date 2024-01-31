from django.urls import path, include, re_path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('menu-items/<int:pk>',views.SingleMenuItemView.as_view()), #{'get':'retrieve'}
    path('category/<int:pk>',views.SingleCategoryView.as_view()), #{'get':'retrieve'}, name='category-detail'
    path('menu-items', views.MenuItemsView.as_view()), #{'get':'list'}
    path('category', views.CategoryView.as_view()), #{'get':'list'}
    path('cart/menu-items', views.cart),
    path('groups/manager/users',views.managers),
    path('groups/manager/users/<int:pk>',views.SingleManagerView.as_view()),
    path('groups/delivery-crew/users',views.delivery_crew),
    path('groups/delivery-crew/users/<int:pk>',views.SingleDeliveryView.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.orderitems),
    # path('api-token-auth/', obtain_auth_token),
    #path('groups/manager/users', views.managers)
]