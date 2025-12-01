from rest_framework import serializers
from django.db import models
from apps.catalyst_app.models import Branch, Inventory, InventoryMovement


class InventoryMovementSerializer(serializers.ModelSerializer):
    """Serializador para movimientos de inventario"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    product_name = serializers.CharField(source='inventory.product.name', read_only=True)
    branch_name = serializers.CharField(source='inventory.branch.name', read_only=True)
    
    class Meta:
        model = InventoryMovement
        fields = ['id', 'inventory', 'movement_type', 'quantity', 'reference', 'notes', 
                  'user', 'user_name', 'product_name', 'branch_name', 'created_at']
        read_only_fields = ['id', 'user', 'user_name', 'product_name', 'branch_name', 'created_at']


class InventorySerializer(serializers.ModelSerializer):
    """Serializador para inventario"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.sku', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = Inventory
        fields = ['id', 'product', 'product_name', 'product_code', 'branch', 'branch_name', 'stock', 
                  'reorder_point', 'last_counted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BranchSerializer(serializers.ModelSerializer):
    """Serializador para sucursales"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True, allow_null=True)
    inventory_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Branch
        fields = ['id', 'company', 'company_name', 'name', 'address', 'phone', 'email', 
                  'manager', 'manager_name', 'is_active', 'inventory_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'company', 'created_at', 'updated_at', 'manager_name']
    
    def get_inventory_count(self, obj):
        """Retorna cantidad de items en inventario"""
        return obj.inventory.count()


class BranchDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de sucursal con inventarios"""
    company = serializers.StringRelatedField(read_only=True)
    inventory = InventorySerializer(read_only=True, many=True)
    manager = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Branch
        fields = '__all__'
