from rest_framework import serializers
from apps.catalyst_app.models import Supplier, Purchase, PurchaseItem


class SupplierSerializer(serializers.ModelSerializer):
    """Serializador para proveedores"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Supplier
        fields = ['id', 'company', 'company_name', 'name', 'rut', 'contact_person', 'email', 
                  'phone', 'address', 'payment_terms', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']


class PurchaseItemSerializer(serializers.ModelSerializer):
    """Serializador para items de compra"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = PurchaseItem
        fields = ['id', 'purchase', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['id', 'subtotal']


class PurchaseSerializer(serializers.ModelSerializer):
    """Serializador para compras"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True, allow_null=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = Purchase
        fields = ['id', 'supplier', 'supplier_name', 'branch', 'branch_name', 'invoice_number',
                  'purchase_date', 'delivery_date', 'total_amount', 'payment_status', 
                  'payment_status_display', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PurchaseDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de compra con items"""
    items = PurchaseItemSerializer(many=True, read_only=True)
    supplier = SupplierSerializer(read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = Purchase
        fields = '__all__'
