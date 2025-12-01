from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    """
    Usuario personalizado con roles y campos específicos para TemucoSoft.
    """
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin (TemucoSoft)'),
        ('admin_cliente', 'Admin Cliente (Dueño)'),
        ('gerente', 'Gerente'),
        ('vendedor', 'Vendedor'),
        ('cliente_final', 'Cliente Final (E-commerce)'),
    )
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='cliente_final',
        help_text='Rol del usuario en el sistema'
    )
    
    rut = models.CharField(
        max_length=12, 
        unique=True,
        null=True,
        blank=True,
        validators=[MinLengthValidator(9)],
        help_text='RUT chileno sin puntos ni guion (ej: 123456789)'
    )
    
    company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text='Empresa/tenant a la que pertenece el usuario'
    )
    
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('tarjeta', 'Tarjeta Crédito'),
            ('paypal', 'PayPal'),
            ('transferencia', 'Transferencia Bancaria'),
            ('prueba', 'Prueba Gratis'),
        ],
        default='prueba',
        null=True,
        blank=True,
        help_text='Método de pago registrado del usuario'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si el usuario puede acceder al sistema'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['company']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def is_super_admin(self):
        """Verifica si es super admin de TemucoSoft"""
        return self.role == 'super_admin'
    
    def is_admin_cliente(self):
        """Verifica si es admin de cliente"""
        return self.role == 'admin_cliente'
    
    def is_gerente(self):
        """Verifica si es gerente"""
        return self.role == 'gerente'
    
    def is_vendedor(self):
        """Verifica si es vendedor"""
        return self.role == 'vendedor'


class Company(models.Model):
    """
    Representa a un cliente/tenant que se suscribe a la plataforma TemucoSoft.
    """
    name = models.CharField(
        max_length=255,
        help_text='Nombre del comercio/empresa cliente'
    )
    
    rut = models.CharField(
        max_length=12,
        unique=True,
        help_text='RUT de la empresa (sin puntos ni guion)'
    )
    
    email = models.EmailField(unique=True)
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        help_text='Dirección registrada de la empresa'
    )
    
    logo = models.ImageField(
        upload_to='company_logos/',
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si la empresa puede usar la plataforma'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Subscription(models.Model):
    """
    Modelo de suscripción/plan para cada cliente.
    Planes: Básico, Estándar, Premium
    """
    PLAN_CHOICES = (
        ('basico', 'Plan Básico'),
        ('estandar', 'Plan Estándar'),
        ('premium', 'Plan Premium'),
    )
    
    PLAN_FEATURES = {
        'basico': {
            'max_branches': 1,
            'max_users': 2,
            'has_basic_reports': False,
            'has_advanced_reports': False,
            'has_api_integration': False,
            'has_suppliers': False,
            'has_crm': False,
            'price': 9.99,
        },
        'estandar': {
            'max_branches': 5,
            'max_users': 10,
            'has_basic_reports': True,
            'has_advanced_reports': False,
            'has_api_integration': False,
            'has_suppliers': True,
            'has_crm': False,
            'price': 49.99,
        },
        'premium': {
            'max_branches': 999,
            'max_users': 999,
            'has_basic_reports': True,
            'has_advanced_reports': True,
            'has_api_integration': True,
            'has_suppliers': True,
            'has_crm': True,
            'price': 199.99,
        }
    }
    
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    
    plan_name = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        help_text='Plan contratado'
    )
    
    start_date = models.DateField(
        help_text='Fecha de inicio de la suscripción'
    )
    
    end_date = models.DateField(
        help_text='Fecha de término de la suscripción'
    )
    
    active = models.BooleanField(
        default=True,
        help_text='Indica si la suscripción está activa'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.company.name} - {self.get_plan_name_display()}"
    
    def get_max_branches(self):
        """Retorna el número máximo de sucursales según el plan"""
        return self.PLAN_FEATURES.get(self.plan_name, {}).get('max_branches', 1)
    
    def get_max_users(self):
        """Retorna el número máximo de usuarios según el plan"""
        return self.PLAN_FEATURES.get(self.plan_name, {}).get('max_users', 1)
    
    def has_basic_reports(self):
        """Verifica si tiene acceso a reportes básicos"""
        return self.PLAN_FEATURES.get(self.plan_name, {}).get('has_basic_reports', False)
    
    def has_advanced_reports(self):
        """Verifica si tiene acceso a reportes avanzados"""
        return self.PLAN_FEATURES.get(self.plan_name, {}).get('has_advanced_reports', False)
    
    def has_api_integration(self):
        """Verifica si tiene acceso a integración API"""
        return self.PLAN_FEATURES.get(self.plan_name, {}).get('has_api_integration', False)
    
    def has_suppliers_access(self):
        """Verifica si tiene acceso a gestión de proveedores"""
        return self.PLAN_FEATURES.get(self.plan_name, {}).get('has_suppliers', False)
    
    def has_crm_access(self):
        """Verifica si tiene acceso a CRM (Clientes, Marketing, Leads)"""
        return self.PLAN_FEATURES.get(self.plan_name, {}).get('has_crm', False)
