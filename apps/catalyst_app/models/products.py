from django.db import models
from django.core.validators import MinValueValidator


class Product(models.Model):
    """
    Modelo de Producto para el catálogo del comercio.
    Pertenece a una empresa específica.
    """
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='products',
        help_text='Empresa propietaria del producto'
    )
    
    sku = models.CharField(
        max_length=100,
        help_text='Código único del producto'
    )
    
    name = models.CharField(
        max_length=255,
        help_text='Nombre del producto'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción detallada del producto'
    )
    
    category = models.CharField(
        max_length=100,
        help_text='Categoría del producto'
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Precio de venta'
    )
    
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Costo del producto'
    )
    
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si el producto está disponible'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ('company', 'sku')
        indexes = [
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def get_margin(self):
        """Calcula el margen de ganancia"""
        if self.cost == 0:
            return 0
        return ((self.price - self.cost) / self.price) * 100 if self.price > 0 else 0
