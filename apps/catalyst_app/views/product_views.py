from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from apps.catalyst_app.models import Product
from apps.catalyst_app.serializers.product_serializers import (
    ProductSerializer, ProductListSerializer, ProductDetailSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet para productos del catálogo"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sku', 'category', 'description']
    ordering_fields = ['name', 'price', 'cost', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    def get_queryset(self):
        """Filtrar productos por company del usuario"""
        user = self.request.user
        if user.is_super_admin():
            return Product.objects.all()
        if user.company:
            return Product.objects.filter(company=user.company)
        return Product.objects.none()
    
    def perform_create(self, serializer):
        """Asignar company automáticamente"""
        serializer.save(company=self.request.user.company)
    
    def perform_update(self, serializer):
        """Validar que el producto pertenezca a la company del usuario antes de actualizar"""
        product = self.get_object()
        user = self.request.user
        
        # Validar permisos
        if not user.is_super_admin() and product.company != user.company:
            raise PermissionDenied('No tienes permiso para editar este producto')
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Validar que el producto pertenezca a la company del usuario antes de eliminar"""
        user = self.request.user
        
        # Validar permisos
        if not user.is_super_admin() and instance.company != user.company:
            raise PermissionDenied('No tienes permiso para eliminar este producto')
        
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Retorna productos agrupados por categoría"""
        category = request.query_params.get('category')
        if not category:
            return Response({'error': 'Categoría requerida'}, status=status.HTTP_400_BAD_REQUEST)
        
        products = self.get_queryset().filter(category=category)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Retorna solo productos activos"""
        products = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
