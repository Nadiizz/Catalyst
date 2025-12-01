from rest_framework import serializers
from django.db import models
from apps.catalyst_app.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializador para productos"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    margin = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'company', 'company_name', 'sku', 'name', 'description', 
                  'category', 'price', 'cost', 'margin', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']
    
    def get_margin(self, obj):
        """Calcula el margen de ganancia en porcentaje"""
        return obj.get_margin()


class ProductListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listado de productos"""
    stock = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'sku', 'name', 'category', 'price', 'stock', 'is_active']
        read_only_fields = ['id']
    
    def get_stock(self, obj):
        """Suma el stock total de todos los inventarios del producto"""
        return obj.inventory.aggregate(total=models.Sum('stock'))['total'] or 0


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado con información de empresa"""
    company = serializers.StringRelatedField(read_only=True)
    margin = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def get_margin(self, obj):
        """Calcula el margen de ganancia"""
        return obj.get_margin()
