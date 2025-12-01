from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Order(models.Model):
    """
    Representa una orden de compra en línea (e-commerce).
    """
    ORDER_STATUS_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('preparando', 'Preparando'),
        ('enviada', 'Enviada'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pendiente', 'Pendiente de Pago'),
        ('pagado', 'Pagado'),
        ('reembolso', 'Reembolso'),
    )
    
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='orders',
        help_text='Tienda que recibe la orden'
    )
    
    order_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Número de orden único'
    )
    
    user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        help_text='Usuario autenticado (opcional para e-commerce anónimo)'
    )
    
    # Información del cliente para órdenes anónimas
    customer_name = models.CharField(
        max_length=255,
        help_text='Nombre del cliente'
    )
    
    customer_email = models.EmailField(
        help_text='Email del cliente'
    )
    
    customer_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    customer_rut = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        help_text='RUT del cliente (opcional)'
    )
    
    # Información de envío
    shipping_address = models.TextField(
        help_text='Dirección de envío'
    )
    
    shipping_city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    shipping_zip = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )
    
    # Montos
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Subtotal sin impuestos'
    )
    
    tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        help_text='Impuestos (IVA)'
    )
    
    shipping_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        help_text='Costo de envío'
    )
    
    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        help_text='Descuento aplicado'
    )
    
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Total de la orden'
    )
    
    # Estados
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pendiente'
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pendiente'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Notas adicionales de la orden'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"Orden #{self.order_number}"
    
    def calculate_totals(self):
        """Recalcula los totales basados en los items"""
        items = self.items.all()
        self.subtotal = sum(item.subtotal for item in items)
        self.tax = self.subtotal * 0.19  # IVA chileno 19%
        self.total = self.subtotal + self.tax + self.shipping_cost - self.discount
        return self


class OrderItem(models.Model):
    """
    Item individual dentro de una orden de e-commerce.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    product = models.ForeignKey(
        'Product',
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Cantidad solicitada'
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Precio unitario al momento de la orden'
    )
    
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Subtotal del item'
    )
    
    class Meta:
        ordering = ['product__name']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class ShoppingCart(models.Model):
    """
    Carro de compras para usuarios autenticados o sesiones.
    """
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        null=True,
        blank=True,
        help_text='Usuario autenticado (si aplica)'
    )
    
    session_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Session key para usuarios anónimos'
    )
    
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        help_text='Tienda del carro'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'company']),
        ]
    
    def __str__(self):
        if self.user:
            return f"Carro de {self.user.username}"
        return f"Carro (sesión: {self.session_key})"
    
    def get_total(self):
        """Calcula el total del carro"""
        return sum(item.subtotal for item in self.items.all())
    
    def get_item_count(self):
        """Retorna el número de items únicos en el carro"""
        return self.items.count()
    
    def clear(self):
        """Vacía el carro"""
        self.items.all().delete()


class CartItem(models.Model):
    """
    Item individual en el carro de compras.
    """
    cart = models.ForeignKey(
        ShoppingCart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        default=1,
        help_text='Cantidad en el carro'
    )
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def subtotal(self):
        """Calcula el subtotal del item"""
        return self.product.price * self.quantity
