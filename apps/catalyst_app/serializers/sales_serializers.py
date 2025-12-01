from rest_framework import serializers
from apps.catalyst_app.models import Sale, SaleItem


class SaleItemSerializer(serializers.ModelSerializer):
    """Serializador para items de venta"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = SaleItem
        fields = ['id', 'sale', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['id', 'subtotal']


class SaleSerializer(serializers.ModelSerializer):
    """Serializador para ventas"""
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Sale
        fields = ['id', 'branch', 'branch_name', 'seller', 'seller_name', 'receipt_number', 
                  'customer_name', 'customer_rut', 'subtotal', 'tax', 'discount', 'total',
                  'payment_method', 'payment_method_display', 'reference', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SaleDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de venta con items"""
    items = SaleItemSerializer(many=True, read_only=True)
    seller = serializers.StringRelatedField(read_only=True)
    branch = serializers.StringRelatedField(read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Sale
        fields = '__all__'
