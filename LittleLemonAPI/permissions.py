from rest_framework import permissions
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from django.contrib.auth.models import User, Group

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

class IsManager(BasePermission):
    def has_permissions(self, request, view):
        #Check if user is a manager
        return request.user.groups.filter(name='Manager').exists()
    
class IsDelivery(BasePermission):
    def has_permissions(self, request, view):
        return request.user.groups.filter(name='Delivery Crew').exists()

class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow managers to edit.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.groups.filter(name='Managers').exists() #in Group.objects.get(name='Managers'):
        
class IsOrderPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'POST']:
            return True
        elif request.method in ['PUT']:
            return request.user.groups.filter(name='Managers').exists()
        elif request.method in ['PATCH']:
            return request.user.groups.filter(name='Delivery Crew').exists()
        elif request.method in ['DELETE']:
            return request.user.groups.filter(name='Managers').exists()