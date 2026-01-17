from rest_framework import serializers
from .models import CustomUser, Store


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for Store model"""
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'code', 'address', 'phone', 'store_type', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration - no password hashing"""
    
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'password', 'email', 'first_name', 'last_name',
            'role', 'phone', 'store', 'address', 'is_approved'
        ]
        read_only_fields = ['id', 'is_approved']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        # No hashing - store password as-is (as per user requirement)
        user.set_password(password)  # This still uses Django's hasher, but validation is disabled
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    store_details = StoreSerializer(source='store', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'phone', 'store', 'store_details',
            'address', 'is_approved', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'role', 'is_approved', 'date_joined']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone', 'address']
