"""
Views for accounts app.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User
from .serializers import (
    UserSerializer, UserCreateSerializer, UserLoginSerializer,
    TokenSerializer, RefreshTokenSerializer, ChangePasswordSerializer
)
from common.responses import APIResponse


class AuthViewSet(viewsets.GenericViewSet):
    """ViewSet for authentication endpoints."""
    permission_classes = []
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register a new user."""
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return APIResponse.created(
                data={
                    'user': UserSerializer(user).data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                message='User registered successfully'
            )
        return APIResponse.error(
            code='VALIDATION_ERROR',
            message='Registration failed',
            details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Login user and return JWT tokens."""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Update last_login
            user.last_login = user.get_utc_now() if hasattr(user, 'get_utc_now') else None
            user.save(update_fields=['last_login'])
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return APIResponse.success(
                data={
                    'user': UserSerializer(user).data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                message='Login successful'
            )
        return APIResponse.error(
            code='AUTHENTICATION_FAILED',
            message='Login failed',
            details=serializer.errors,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout user."""
        # In a real application, you might blacklist the token here
        return APIResponse.success(
            message='Logout successful'
        )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh(self, request):
        """Refresh access token."""
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh = RefreshToken(serializer.validated_data['refresh'])
                return APIResponse.success(
                    data={
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    },
                    message='Token refreshed successfully'
                )
            except TokenError:
                return APIResponse.error(
                    code='INVALID_TOKEN',
                    message='Invalid refresh token',
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
        return APIResponse.error(
            code='VALIDATION_ERROR',
            message='Token refresh failed',
            details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile."""
        serializer = UserSerializer(request.user)
        return APIResponse.success(
            data=serializer.data,
            message='User profile retrieved successfully'
        )
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return APIResponse.error(
                    code='INVALID_PASSWORD',
                    message='Current password is incorrect',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return APIResponse.success(
                message='Password changed successfully'
            )
        return APIResponse.error(
            code='VALIDATION_ERROR',
            message='Password change failed',
            details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for reading user information (admin only)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only admins can list users."""
        if self.request.user.role != User.ROLE_ADMIN:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()
