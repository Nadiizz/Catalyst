from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.catalyst_app.models import Branch, Inventory, Product
from apps.catalyst_app.serializers.inventory_serializers import (
    BranchSerializer, BranchDetailSerializer, InventorySerializer
)


class BranchViewSet(viewsets.ModelViewSet):
    """ViewSet para sucursales"""
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BranchDetailSerializer
        return BranchSerializer
    
    def get_queryset(self):
        """Filtrar sucursales por company del usuario"""
        user = self.request.user
        if user.is_super_admin():
            return Branch.objects.all()
        if user.company:
            return Branch.objects.filter(company=user.company)
        return Branch.objects.none()
    
    def perform_create(self, serializer):
        """Asignar company automáticamente y validar límite de sucursales"""
        user = self.request.user
        
        # Obtener máximo de sucursales según el plan
        try:
            max_branches = user.company.subscription.get_max_branches()
            current_branches = user.company.branches.count()
        except AttributeError:
            max_branches = 1
            current_branches = user.company.branches.count() if user.company else 0
        
        # Validar que no se supere el límite
        if current_branches >= max_branches:
            raise ValidationError(
                f"Has alcanzado el límite de {max_branches} sucursales para tu plan. "
                f"Por favor, mejora tu suscripción para agregar más sucursales."
            )
        
        serializer.save(company=user.company)


class InventoryViewSet(viewsets.ModelViewSet):
    """ViewSet para inventario"""
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name', 'branch__name']
    ordering_fields = ['stock', 'product__name']
    ordering = ['product__name']
    
    def get_queryset(self):
        """Filtrar inventarios por company del usuario"""
        user = self.request.user
        if user.is_super_admin():
            return Inventory.objects.all()
        if user.company:
            return Inventory.objects.filter(branch__company=user.company)
        return Inventory.objects.none()
    
    @action(detail=False, methods=['post'])
    def sync_inventory(self, request):
        """
        Sincroniza el inventario creando registros faltantes para todos los productos
        que no tienen inventario en todas las sucursales
        """
        user = request.user
        
        # Obtener company del usuario
        if not user.company:
            return Response(
                {'error': 'Usuario sin compañía asignada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener todas las sucursales y productos de la company
        branches = Branch.objects.filter(company=user.company)
        products = Product.objects.filter(company=user.company)
        
        if not branches.exists():
            return Response(
                {'error': 'No hay sucursales configuradas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_count = 0
        
        # Para cada producto, crear inventario en todas las sucursales que falten
        for product in products:
            for branch in branches:
                inventory, created = Inventory.objects.get_or_create(
                    product=product,
                    branch=branch,
                    defaults={
                        'stock': 0,
                        'reorder_point': 10
                    }
                )
                if created:
                    created_count += 1
        
        return Response({
            'message': f'Sincronización completada',
            'inventories_created': created_count,
            'total_branches': branches.count(),
            'total_products': products.count()
        }, status=status.HTTP_200_OK)
