"""
Custom permissions for Smart Rental Tracking System backend.
"""
from rest_framework.permissions import BasePermission
from apps.accounts.models import User


class IsAdmin(BasePermission):
    """Only admins can access."""
    message = "Only admins have access to this resource."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.ROLE_ADMIN


class IsManager(BasePermission):
    """Only managers and admins can access."""
    message = "Only managers have access to this resource."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in [User.ROLE_ADMIN, User.ROLE_MANAGER]


class IsOperator(BasePermission):
    """Only operators and above can access."""
    message = "Only operators have access to this resource."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in [
            User.ROLE_ADMIN, User.ROLE_MANAGER, User.ROLE_OPERATOR
        ]


class IsViewer(BasePermission):
    """All authenticated users can view."""
    message = "You don't have permission to access this resource."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class CanManageEquipment(BasePermission):
    """Only admins and managers can manage equipment."""
    message = "You don't have permission to manage equipment."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in [User.ROLE_ADMIN, User.ROLE_MANAGER]


class CanManageSites(BasePermission):
    """Only admins and managers can manage sites."""
    message = "You don't have permission to manage sites."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in [User.ROLE_ADMIN, User.ROLE_MANAGER]


class CanManageOperators(BasePermission):
    """Only admins and managers can manage operators."""
    message = "You don't have permission to manage operators."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in [User.ROLE_ADMIN, User.ROLE_MANAGER]


class CanManageRentals(BasePermission):
    """Only admins, managers, and operators can manage rentals."""
    message = "You don't have permission to manage rentals."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in [
            User.ROLE_ADMIN, User.ROLE_MANAGER, User.ROLE_OPERATOR
        ]


class CanViewAnalytics(BasePermission):
    """Only admins and managers can view analytics."""
    message = "You don't have permission to view analytics."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in [User.ROLE_ADMIN, User.ROLE_MANAGER]
