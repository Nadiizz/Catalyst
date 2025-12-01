from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from apps.catalyst_app.models import Sale
from apps.catalyst_app.serializers.sales_serializers import (
    SaleSerializer, SaleDetailSerializer
)


class SaleViewSet(viewsets.ModelViewSet):
    """ViewSet para ventas POS"""
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['receipt_number', 'customer_name', 'branch__name']
    ordering_fields = ['created_at', 'total']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SaleDetailSerializer
        return SaleSerializer
    
    def get_queryset(self):
        """Filtrar ventas por company del usuario"""
        user = self.request.user
        if user.is_super_admin():
            return Sale.objects.all()
        if user.company:
            return Sale.objects.filter(branch__company=user.company)
        return Sale.objects.none()
    
    def perform_create(self, serializer):
        """Asignar seller automáticamente"""
        serializer.save(seller=self.request.user)
