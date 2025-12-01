from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from apps.catalyst_app.models import Supplier, Purchase
from apps.catalyst_app.serializers.supplier_serializers import (
    SupplierSerializer, PurchaseSerializer, PurchaseDetailSerializer
)


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet para proveedores"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'rut', 'email', 'contact_person']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Filtrar proveedores por company del usuario"""
        user = self.request.user
        if user.is_super_admin():
            return Supplier.objects.all()
        if user.company:
            return Supplier.objects.filter(company=user.company)
        return Supplier.objects.none()
    
    def perform_create(self, serializer):
        """Asignar company automáticamente"""
        serializer.save(company=self.request.user.company)


class PurchaseViewSet(viewsets.ModelViewSet):
    """ViewSet para compras a proveedores"""
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['supplier__name', 'invoice_number', 'branch__name']
    ordering_fields = ['purchase_date', 'total_amount']
    ordering = ['-purchase_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PurchaseDetailSerializer
        return PurchaseSerializer
    
    def get_queryset(self):
        """Filtrar compras por company del usuario"""
        user = self.request.user
        if user.is_super_admin():
            return Purchase.objects.all()
        if user.company:
            return Purchase.objects.filter(supplier__company=user.company)
        return Purchase.objects.none()
