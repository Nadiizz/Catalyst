from django.db import models
from django.core.validators import MinValueValidator


class Supplier(models.Model):
    """
    Representa a los proveedores de productos para la empresa.
    """
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='suppliers',
        help_text='Empresa propietaria del proveedor'
    )
    
    name = models.CharField(
        max_length=255,
        help_text='Nombre del proveedor'
    )
    
    rut = models.CharField(
        max_length=12,
        help_text='RUT del proveedor (sin puntos ni guion)'
    )
    
    email = models.EmailField(
        blank=True,
        null=True
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    contact_person = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Persona de contacto en el proveedor'
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        help_text='Dirección del proveedor'
    )
    
    payment_terms = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Términos de pago (ej: Contado, 30 días, etc.)'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si el proveedor está activo'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Notas adicionales sobre el proveedor'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ('company', 'rut')
        indexes = [
            models.Index(fields=['company', 'is_active']),
        ]
    
    def __str__(self):
        return self.name


class Purchase(models.Model):
    """
    Representa una compra a un proveedor.
    Genera movimiento de entrada en el inventario.
    """
    PAYMENT_STATUS_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('parcialmente_pagado', 'Parcialmente Pagado'),
    )
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='purchases',
        help_text='Proveedor'
    )
    
    branch = models.ForeignKey(
        'catalyst_app.Branch',
        on_delete=models.SET_NULL,
        null=True,
        related_name='purchases',
        help_text='Sucursal que recibe la compra'
    )
    
    invoice_number = models.CharField(
        max_length=100,
        help_text='Número de factura del proveedor'
    )
    
    purchase_date = models.DateField(
        help_text='Fecha de la compra'
    )
    
    delivery_date = models.DateField(
        blank=True,
        null=True,
        help_text='Fecha de entrega/recepción'
    )
    
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Monto total de la compra'
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pendiente'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Notas sobre la compra'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-purchase_date']
        indexes = [
            models.Index(fields=['supplier', '-purchase_date']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"Compra #{self.invoice_number} - {self.supplier.name}"


class PurchaseItem(models.Model):
    """
    Items individuales dentro de una compra.
    """
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    product = models.ForeignKey(
        'Product',
        on_delete=models.PROTECT,
        related_name='purchase_items'
    )
    
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Cantidad comprada'
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Precio unitario de compra'
    )
    
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Subtotal del item (cantidad x precio)'
    )
    
    class Meta:
        ordering = ['product__name']
        indexes = [
            models.Index(fields=['purchase']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} unidades"
