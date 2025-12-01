from django.db import models
from django.core.validators import MinValueValidator


class Branch(models.Model):
    """
    Representa una sucursal de un comercio cliente.
    """
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='branches',
        help_text='Empresa propietaria de la sucursal'
    )
    
    name = models.CharField(
        max_length=255,
        help_text='Nombre de la sucursal'
    )
    
    address = models.TextField(
        help_text='Dirección de la sucursal'
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    email = models.EmailField(
        blank=True,
        null=True
    )
    
    manager = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_branches',
        limit_choices_to={'role': 'gerente'},
        help_text='Gerente responsable de la sucursal'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si la sucursal está operativa'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ('company', 'name')
        indexes = [
            models.Index(fields=['company', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"


class Inventory(models.Model):
    """
    Relación many-to-many entre Sucursal y Producto.
    Almacena el stock de cada producto en cada sucursal.
    """
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='inventory'
    )
    
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='inventory'
    )
    
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Cantidad actual de stock'
    )
    
    reorder_point = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text='Cantidad mínima antes de hacer reorden'
    )
    
    last_counted = models.DateTimeField(
        auto_now=True,
        help_text='Última vez que se contabilizó el stock'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('branch', 'product')
        ordering = ['product__name']
        indexes = [
            models.Index(fields=['branch', 'product']),
            models.Index(fields=['stock']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.branch.name} ({self.stock} unidades)"
    
    def needs_reorder(self):
        """Verifica si el stock está por debajo del punto de reorden"""
        return self.stock <= self.reorder_point


class InventoryMovement(models.Model):
    """
    Registra todos los movimientos de inventario (entradas y salidas).
    """
    MOVEMENT_TYPE_CHOICES = (
        ('entrada', 'Entrada (Compra a Proveedor)'),
        ('salida', 'Salida (Venta)'),
        ('ajuste', 'Ajuste'),
        ('devolucion', 'Devolución'),
    )
    
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='movements'
    )
    
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES,
        help_text='Tipo de movimiento'
    )
    
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Cantidad movida'
    )
    
    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Referencia (Nº de compra, venta, etc.)'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Notas adicionales del movimiento'
    )
    
    user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='inventory_movements'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inventory', '-created_at']),
            models.Index(fields=['movement_type']),
        ]
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.quantity} unidades"
