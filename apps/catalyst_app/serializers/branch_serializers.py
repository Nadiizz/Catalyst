from rest_framework import serializers
from apps.catalyst_app.models import Order, OrderItem, ShoppingCart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """Serializador para items del carrito"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_name', 'product_price', 'quantity', 'added_at', 'updated_at']
        read_only_fields = ['id', 'added_at', 'updated_at']


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializador para carrito de compras"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ShoppingCart
        fields = ['id', 'user', 'user_name', 'items', 'total_items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        """Cantidad total de items en el carrito"""
        return sum(item.quantity for item in obj.items.all())


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializador para items de orden"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['id', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    """Serializador para órdenes"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    total_amount = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'company', 'order_number', 'user', 'user_name', 'customer_name', 
                  'customer_email', 'customer_phone', 'customer_rut', 'shipping_address',
                  'shipping_city', 'shipping_zip', 'subtotal', 'tax', 'shipping_cost', 'total',
                  'status', 'status_display', 'payment_status', 'payment_status_display',
                  'total_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_amount(self, obj):
        """Retorna el total de la orden"""
        return obj.total


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de orden con items"""
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True, allow_null=True)
    company = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
