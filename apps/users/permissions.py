from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Only admin/owner can access"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


class IsStoreManager(permissions.BasePermission):
    """Admin or store manager can access"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['ADMIN', 'STORE_MANAGER']
        )


class IsSalesStaff(permissions.BasePermission):
    """Admin, manager, or sales staff can access"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['ADMIN', 'STORE_MANAGER', 'SALES_STAFF']
        )


class IsSupplier(permissions.BasePermission):
    """Only approved suppliers can access"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'SUPPLIER' and
            request.user.is_approved
        )


class IsCustomer(permissions.BasePermission):
    """Only approved customers can access"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'CUSTOMER' and
            request.user.is_approved
        )


class IsApproved(permissions.BasePermission):
    """User must be approved (for suppliers and customers)"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin, managers, and staff are auto-approved
        if request.user.role in ['ADMIN', 'STORE_MANAGER', 'SALES_STAFF']:
            return True
        
        # Suppliers and customers must be explicitly approved
        return request.user.is_approved
