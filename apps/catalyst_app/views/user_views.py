from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.catalyst_app.models import User, Company, Subscription
from apps.catalyst_app.serializers.user_serializers import (
    UserSerializer, UserCreateSerializer, UserDetailSerializer, 
    CompanySerializer, SubscriptionSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para usuarios con autenticación y registro"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'rut']
    ordering_fields = ['created_at', 'username']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Permite registro sin autenticación, resto requiere autenticación"""
        if self.action == 'create' or self.action == 'login':
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny()])
    def login(self, request):
        """Login y obtener tokens JWT"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username y password requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retorna el usuario actual"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='change-role')
    def change_role(self, request, pk=None):
        """Cambiar el rol de un usuario (solo para admins)"""
        # Validar que quien hace la solicitud es admin
        if request.user.role not in ['super_admin', 'admin_cliente']:
            return Response(
                {'message': 'Solo administradores pueden cambiar roles'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener el usuario a modificar
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {'message': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validar que pertenece a la misma empresa
        if request.user.company != user.company:
            return Response(
                {'message': 'No puedes cambiar el rol de usuarios de otras empresas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener nuevo rol
        new_role = request.data.get('role')
        if not new_role:
            return Response(
                {'message': 'Se requiere especificar el nuevo rol'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que el rol es permitido (no permitir cambiar a admin_cliente desde aquí)
        allowed_roles = ['gerente', 'vendedor', 'admin_cliente']
        if new_role not in allowed_roles:
            return Response(
                {'message': f'Rol no permitido. Roles válidos: {", ".join(allowed_roles)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar el rol
        old_role = user.role
        user.role = new_role
        user.save()
        
        return Response({
            'success': True,
            'message': f'Rol cambiado de {old_role} a {new_role}',
            'user': UserSerializer(user).data
        })
    
    def perform_create(self, serializer):
        """Crear usuario validando límite del plan"""
        user = self.request.user
        
        # Obtener máximo de usuarios según el plan
        try:
            max_users = user.company.subscription.get_max_users()
            current_users = user.company.users.count()
        except AttributeError:
            max_users = 1
            current_users = user.company.users.count() if user.company else 0
        
        # Validar que no se supere el límite
        if current_users >= max_users:
            raise ValidationError(
                f"Has alcanzado el límite de {max_users} usuarios para tu plan. "
                f"Por favor, mejora tu suscripción para agregar más usuarios."
            )
        
        # Asignar la compañía del usuario autenticado
        serializer.save(company=user.company)
    
    def get_queryset(self):
        """Filtrar por company si no es super_admin, y opcionalmente por role"""
        user = self.request.user
        queryset = User.objects.all() if user.is_super_admin() else User.objects.filter(company=user.company)
        
        # Filtrar por role si se proporciona en query params
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet para empresas/clientes"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'rut', 'email']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtrar por acceso del usuario"""
        user = self.request.user
        if user.is_super_admin():
            return Company.objects.all()
        # Admin cliente solo ve su empresa
        if user.is_admin_cliente() and user.company:
            return Company.objects.filter(id=user.company.id)
        return Company.objects.none()


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet para suscripciones/planes"""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['start_date', 'end_date']
    ordering = ['-start_date']
    
    def get_queryset(self):
        """Filtrar por acceso del usuario"""
        user = self.request.user
        if user.is_super_admin():
            return Subscription.objects.all()
        if user.company:
            return Subscription.objects.filter(company=user.company)
        return Subscription.objects.none()
