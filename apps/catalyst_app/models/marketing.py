from django.db import models
from django.utils import timezone
from apps.catalyst_app.models.customers import Customer

class EmailCampaign(models.Model):
    """Modelo para campañas de email marketing"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('scheduled', 'Programada'),
        ('sending', 'Enviando'),
        ('sent', 'Enviada'),
        ('paused', 'Pausada'),
        ('cancelled', 'Cancelada'),
    ]
    
    name = models.CharField(max_length=200, db_index=True)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Contenido
    html_content = models.TextField(blank=True)
    text_content = models.TextField(blank=True)
    
    # Configuración
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Segmentación
    target_segment = models.CharField(max_length=100, blank=True)
    recipients_count = models.IntegerField(default=0)
    
    # Métricas
    sent_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    converted_count = models.IntegerField(default=0)
    
    # Tasas
    open_rate = models.FloatField(default=0.0, help_text="Porcentaje de apertura")
    click_rate = models.FloatField(default=0.0, help_text="Porcentaje de clics")
    conversion_rate = models.FloatField(default=0.0, help_text="Porcentaje de conversión")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=200, default='Sistema')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return self.name


class MarketingAutomation(models.Model):
    """Modelo para flujos de automatización de marketing"""
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('paused', 'Pausada'),
        ('archived', 'Archivada'),
    ]
    
    TRIGGER_TYPES = [
        ('lead_created', 'Nuevo Lead Creado'),
        ('lead_scored', 'Lead Alcanza Puntuación'),
        ('abandoned_cart', 'Carrito Abandonado'),
        ('purchase', 'Compra Realizada'),
        ('inactivity', 'Inactividad'),
        ('date_based', 'Basado en Fecha'),
    ]
    
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    
    # Configuración
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True)
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES)
    
    # Acciones
    action_type = models.CharField(max_length=50, choices=[
        ('send_email', 'Enviar Email'),
        ('assign_to_user', 'Asignar a Usuario'),
        ('update_segment', 'Actualizar Segmento'),
        ('update_score', 'Actualizar Puntuación'),
    ])
    
    # Datos
    action_data = models.JSONField(default=dict, blank=True)
    
    # Activación
    trigger_count = models.IntegerField(default=0, help_text="Veces que se activó")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Lead(models.Model):
    """Modelo para leads generados por marketing"""
    SOURCE_CHOICES = [
        ('website', 'Sitio Web'),
        ('email', 'Email Campaign'),
        ('social_media', 'Redes Sociales'),
        ('referral', 'Referencia'),
        ('webinar', 'Webinar'),
        ('evento', 'Evento'),
        ('otro', 'Otro'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Nuevo'),
        ('qualified', 'Calificado'),
        ('unqualified', 'No Calificado'),
        ('converted', 'Convertido'),
    ]
    
    # Información básica
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Empresa
    company = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=200, blank=True)
    
    # Origen y seguimiento
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, db_index=True)
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Calificación
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', db_index=True)
    lead_score = models.IntegerField(default=0)
    
    # Conversión
    converted_customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contacted = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['source', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class LeadScoringRule(models.Model):
    """Reglas para calcular lead scores"""
    FIELD_CHOICES = [
        ('email_open', 'Apertura de Email'),
        ('email_click', 'Clic en Email'),
        ('website_visit', 'Visita a Sitio'),
        ('page_view', 'Visualización de Página'),
        ('form_submission', 'Envío de Formulario'),
        ('call_booked', 'Llamada Programada'),
    ]
    
    name = models.CharField(max_length=200)
    field = models.CharField(max_length=50, choices=FIELD_CHOICES)
    points = models.IntegerField(help_text="Puntos a agregar")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-points']
    
    def __str__(self):
        return f"{self.name} ({self.points} pts)"
