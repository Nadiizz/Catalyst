from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Sale(models.Model):
    """
    Representa una venta POS (punto de venta).
    """
    PAYMENT_METHOD_CHOICES = (
        ('efectivo', 'Efectivo'),
        ('tarjeta_debito', 'Tarjeta Débito'),
        ('tarjeta_credito', 'Tarjeta Crédito'),
        ('transferencia', 'Transferencia'),
        ('cheque', 'Cheque'),
        ('otro', 'Otro'),
    )
    
    branch = models.ForeignKey(
        'catalyst_app.Branch',
        on_delete=models.PROTECT,
        related_name='sales',
        help_text='Sucursal donde se realiza la venta'
    )
    
    seller = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales',
        limit_choices_to={'role': 'vendedor'},
        help_text='Vendedor que realiza la venta'
    )
    
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Número de comprobante/boleta'
    )
    
    customer_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Nombre del cliente (opcional)'
    )
    
    customer_rut = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        help_text='RUT del cliente (opcional)'
    )
    
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
        help_text='Total de la venta'
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        help_text='Método de pago utilizado'
    )
    
    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Referencia del pago (nº transacción, cheque, etc.)'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Notas adicionales de la venta'
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha y hora de la venta'
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['branch', '-created_at']),
            models.Index(fields=['seller', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Venta #{self.receipt_number} - ${self.total}"
    
    def calculate_totals(self):
        """Recalcula los totales basados en los items"""
        items = self.items.all()
        self.subtotal = sum(item.subtotal for item in items)
        self.tax = self.subtotal * 0.19  # IVA chileno 19%
        self.total = self.subtotal + self.tax - self.discount
        return self


class SaleItem(models.Model):
    """
    Item individual dentro de una venta.
    """
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    product = models.ForeignKey(
        'Product',
        on_delete=models.PROTECT,
        related_name='sale_items'
    )
    
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Cantidad vendida'
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Precio unitario al momento de la venta'
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


class Payment(models.Model):
    """
    Registro de pagos recibidos en una venta.
    Permite pagos parciales o múltiples métodos de pago.
    """
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Monto del pago'
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=Sale.PAYMENT_METHOD_CHOICES
    )
    
    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Referencia de pago (nº transacción, etc.)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pago ${self.amount} - Venta #{self.sale.receipt_number}"
