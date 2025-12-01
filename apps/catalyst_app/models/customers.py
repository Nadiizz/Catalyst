from django.db import models
from django.utils import timezone

class Customer(models.Model):
    """Modelo para gestionar clientes/contactos"""
    CUSTOMER_TYPES = [
        ('individual', 'Individual'),
        ('empresa', 'Empresa'),
        ('gobierno', 'Gobierno'),
    ]
    
    STATUS_CHOICES = [
        ('prospect', 'Prospecto'),
        ('lead', 'Lead Calificado'),
        ('cliente', 'Cliente Activo'),
        ('inactivo', 'Inactivo'),
    ]
    
    # Información básica
    name = models.CharField(max_length=200, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default='individual')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='prospect', db_index=True)
    
    # Información de empresa
    company = models.CharField(max_length=200, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    
    # Dirección
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Información de ventas
    lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_purchases = models.IntegerField(default=0)
    last_purchase_date = models.DateTimeField(null=True, blank=True)
    
    # Scoring y segmentación
    lead_score = models.IntegerField(default=0, help_text="Puntuación de 0-100")
    segment = models.CharField(max_length=50, blank=True, db_index=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contacted = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['lead_score', '-created_at']),
        ]
    
    def __str__(self):
        return self.name


class Interaction(models.Model):
    """Modelo para registrar interacciones con clientes"""
    INTERACTION_TYPES = [
        ('email', 'Email'),
        ('llamada', 'Llamada'),
        ('reunion', 'Reunión'),
        ('chat', 'Chat'),
        ('compra', 'Compra'),
        ('comentario', 'Comentario'),
        ('otro', 'Otro'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    subject = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    outcome = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=200, default='Sistema')
    
    lead_score_impact = models.IntegerField(default=0, help_text="Impacto en el lead score")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.customer.name} - {self.get_interaction_type_display()}"


class ContactOpportunity(models.Model):
    """Modelo para oportunidades de venta"""
    STAGE_CHOICES = [
        ('prospecting', 'Prospección'),
        ('qualification', 'Calificación'),
        ('proposal', 'Propuesta'),
        ('negotiation', 'Negociación'),
        ('closed_won', 'Ganada'),
        ('closed_lost', 'Perdida'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='opportunities')
    title = models.CharField(max_length=200)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='prospecting', db_index=True)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    probability = models.IntegerField(default=0, help_text="Probabilidad 0-100")
    expected_close_date = models.DateField()
    
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'stage']),
        ]
    
    def __str__(self):
        return self.title
