from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CustomUser, Store
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    StoreSerializer
)
from .permissions import IsAdmin, IsStoreManager


class UserRegistrationView(generics.CreateAPIView):
    """
    Public endpoint for user registration.
    Suppliers and customers require admin approval before accessing the system.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update authenticated user's profile
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class StoreViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for stores/warehouses (admin and managers only)
    """
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsStoreManager]
    filterset_fields = ['store_type', 'is_active']
    search_fields = ['name', 'code', 'address']
    ordering_fields = ['name', 'created_at']


class UserListView(generics.ListAPIView):
    """
    List all users (admin and managers only)
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsStoreManager]
    filterset_fields = ['role', 'is_approved', 'is_active', 'store']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined']


class UserApprovalView(generics.UpdateAPIView):
    """
    Approve or reject user (admin only)
    """
    queryset = CustomUser.objects.all()
    permission_classes = [IsAdmin]
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        is_approved = request.data.get('is_approved', False)
        
        user.is_approved = is_approved
        user.save()
        
        serializer = UserSerializer(user)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current authenticated user details"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
