from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from apps.catalyst_app.models import Order, ShoppingCart
from apps.catalyst_app.serializers.branch_serializers import (
    OrderSerializer, OrderDetailSerializer, ShoppingCartSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet para órdenes de e-commerce"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_number', 'customer_name', 'customer_email']
    ordering_fields = ['created_at', 'total', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderSerializer
    
    def get_queryset(self):
        """Filtrar órdenes por company del usuario"""
        user = self.request.user
        if user.is_super_admin():
            return Order.objects.all()
        if user.company:
            return Order.objects.filter(company=user.company)
        return Order.objects.none()


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """ViewSet para carritos de compra"""
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar carritos del usuario actual o si es admin de su company"""
        user = self.request.user
        if user.is_super_admin():
            return ShoppingCart.objects.all()
        # Cada usuario ve solo su carrito
        return ShoppingCart.objects.filter(user=user)
