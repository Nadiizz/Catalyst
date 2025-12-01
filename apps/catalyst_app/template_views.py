"""
TEMPLATE VIEWS - Vistas para servir templates HTML del sistema
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.utils.timezone import now
from datetime import timedelta
from apps.catalyst_app.models import User, Company, Subscription


@login_required(login_url='catalyst_app:login')
@require_http_methods(["GET"])
def productos_view(request):
    """Vista para la página de gestión de productos"""
    return render(request, 'productos.html')


@login_required(login_url='catalyst_app:login')
@require_http_methods(["GET"])
def usuarios_view(request):
    """Vista para la página de gestión de usuarios - Plan Estándar y Premium"""
    # Solo super admin y admin_cliente pueden acceder
    if request.user.role not in ['super_admin', 'admin_cliente']:
        return render(request, 'error.html', {
            'error_code': 403,
            'error_message': 'No tienes permisos para acceder a esta página. Solo administradores pueden gestionar usuarios.'
        }, status=403)
    
    # Obtener información del plan (para mostrar límites de usuarios)
    try:
        plan = request.user.company.subscription.plan_name
        max_users = request.user.company.subscription.get_max_users()
        current_users = request.user.company.users.count()
    except AttributeError:
        plan = 'basico'
        max_users = 2
        current_users = request.user.company.users.count() if request.user.company else 0
    
    # Obtener disponibles roles para mostrar al admin
    available_roles = [
        ('gerente', 'Gerente'),
        ('vendedor', 'Vendedor'),
    ]
    
    context = {
        'max_users': max_users,
        'current_users': current_users,
        'plan': plan,
        'available_roles': available_roles,
    }
    
    return render(request, 'usuarios.html', context)


@login_required(login_url='catalyst_app:login')
@require_http_methods(["GET"])
def ventas_view(request):
    """Vista para la página de gestión de ventas"""
    return render(request, 'ventas.html')


@login_required(login_url='catalyst_app:login')
@require_http_methods(["GET"])
def ordenes_view(request):
    """Vista para la página de gestión de órdenes"""
    return render(request, 'ordenes.html')


@login_required(login_url='catalyst_app:login')
@require_http_methods(["GET"])
def inventario_view(request):
    """Vista para la página de control de inventario"""
    return render(request, 'inventario.html')


@login_required(login_url='catalyst_app:login')
@require_http_methods(["GET"])
def proveedores_view(request):
    """Vista para la página de gestión de proveedores - Plan Estándar y Premium"""
    # Solo admin puede acceder
    if request.user.role not in ['super_admin', 'admin_cliente']:
        return render(request, 'error.html', {
            'error_code': 403,
            'error_message': 'No tienes permisos para acceder a esta página'
        }, status=403)
    
    # Verificar si el plan permite proveedores (Estándar o Premium)
    try:
        plan = request.user.company.subscription.plan_name
    except AttributeError:
        plan = 'basico'
    
    if plan == 'basico':
        return render(request, 'error.html', {
            'error_code': 403,
            'error_message': 'La gestión de proveedores requiere Plan Estándar o superior'
        }, status=403)
    
    return render(request, 'proveedores.html')


@login_required(login_url='catalyst_app:login')
@require_http_methods(["GET"])
def sucursales_view(request):
    """Vista para la página de gestión de sucursales"""
    # Solo admin puede acceder
    if request.user.role not in ['super_admin', 'admin_cliente']:
        return render(request, 'error.html', {
            'error_code': 403,
            'error_message': 'No tienes permisos para acceder a esta página'
        }, status=403)
    
    # Obtener el plan del usuario
    try:
        max_branches = request.user.company.subscription.get_max_branches()
    except AttributeError:
        max_branches = 1  # Valor por defecto
    
    context = {
        'max_branches': max_branches,
        'current_branches': request.user.company.branches.count() if request.user.company else 0,
    }
    
    return render(request, 'sucursales.html', context)


@require_http_methods(["GET"])
def dashboard_view(request):
    """Vista para el dashboard principal"""
    if not request.user.is_authenticated:
        return redirect('catalyst_app:login')
    
    # Redirigir al dashboard según el rol
    if request.user.role == 'vendedor':
        return redirect('catalyst_app:dashboard-vendedor')
    elif request.user.role in ['gerente']:
        return redirect('catalyst_app:dashboard-gerente')
    elif request.user.role == 'super_admin' or request.user.role == 'admin_cliente':
        from django.db.models import Count, Sum, Q
        from datetime import timedelta
        from apps.catalyst_app.models import Product, Branch, Order
        from apps.catalyst_app.models.branch import Inventory
        
        company = request.user.company
        
        # Calcular métricas
        context = {
            'plan_name': company.subscription.plan_name if hasattr(company, 'subscription') else 'basico',
            'max_branches': company.subscription.get_max_branches() if hasattr(company, 'subscription') else 1,
            'max_users': company.subscription.get_max_users() if hasattr(company, 'subscription') else 2,
        }
        
        # Contar productos
        context['product_count'] = Product.objects.filter(company=company).count()
        
        # Contar usuarios
        context['user_count'] = User.objects.filter(company=company).count()
        
        # Contar sucursales
        context['branch_count'] = Branch.objects.filter(company=company).count()
        
        # Contar órdenes
        context['order_count'] = Order.objects.filter(company=company).count()
        context['pending_orders'] = Order.objects.filter(
            company=company,
            status__in=['pending', 'processing']
        ).count()
        
        # Total de ventas
        sales_total = Order.objects.filter(
            company=company,
            status='entregada'
        ).aggregate(total=Sum('total'))['total'] or 0
        context['total_sales'] = f"{sales_total:.2f}"
        
        # Total inventario
        inventory_total = Inventory.objects.filter(
            branch__company=company
        ).aggregate(total=Sum('stock'))['total'] or 0
        context['total_inventory'] = inventory_total
        
        # Gráfico de ventas (últimos 7 días)
        from django.utils.timezone import now
        seven_days_ago = now().date() - timedelta(days=7)
        sales_by_date = Order.objects.filter(
            company=company,
            status='entregada',
            created_at__date__gte=seven_days_ago
        ).extra(
            select={'date': 'DATE(created_at)'}
        ).values('date').annotate(
            amount=Sum('total')
        ).order_by('date')
        
        context['sales_data'] = []
        for item in sales_by_date:
            context['sales_data'].append({
                'date': item['date'].strftime('%a') if item['date'] else '',
                'amount': float(item['amount'] or 0)
            })
        context['sales_data'] = str(context['sales_data']).replace("'", '"')
        
        # Top 5 productos
        products_top = Product.objects.filter(
            company=company
        ).annotate(
            sales_count=Count('order_items')
        ).order_by('-sales_count')[:5]
        
        context['products_data'] = []
        for prod in products_top:
            context['products_data'].append({
                'name': prod.name,
                'sales': prod.sales_count
            })
        context['products_data'] = str(context['products_data']).replace("'", '"')
        
        # Estado de órdenes
        orders_status = Order.objects.filter(
            company=company
        ).values('status').annotate(count=Count('id'))
        
        context['orders_data'] = []
        status_map = {
            'pendiente': 'Pendientes',
            'confirmada': 'Confirmadas',
            'preparando': 'Preparando',
            'enviada': 'Enviadas',
            'entregada': 'Entregadas',
            'cancelada': 'Canceladas'
        }
        for status in orders_status:
            context['orders_data'].append({
                'status': status_map.get(status['status'], status['status']),
                'count': status['count']
            })
        context['orders_data'] = str(context['orders_data']).replace("'", '"')
        
        # Ingresos por sucursal (simplificado - top 5 sucursales por ID)
        context['branches_data'] = []
        top_branches = Branch.objects.filter(
            company=company,
            is_active=True
        ).order_by('-created_at')[:5]
        
        for branch in top_branches:
            context['branches_data'].append({
                'name': branch.name,
                'revenue': 0.0  # Simulado: sin órdenes asociadas directamente
            })
        context['branches_data'] = str(context['branches_data']).replace("'", '"')
        
        # Actividad reciente (simulada porque no tenemos modelo Activity)
        context['recent_activities'] = []
        
        return render(request, 'dashboard_admin.html', context)
    else:
        # Usuarios normales ven el mismo dashboard (versión simplificada del admin)
        return render(request, 'dashboard_admin.html', context)


@require_http_methods(["GET"])
def index_view(request):
    """Vista para la página de inicio/landing page"""
    return render(request, 'index.html')


@require_http_methods(["GET"])
def planes_view(request):
    """Vista para la página de planes y suscripciones"""
    return render(request, 'planes.html')


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vista para el login"""
    if request.user.is_authenticated:
        return redirect('catalyst_app:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('catalyst_app:dashboard')
        else:
            return render(request, 'login.html', {
                'error': 'Usuario o contraseña inválidos'
            })
    
    return render(request, 'login.html')


@csrf_protect
@require_http_methods(["GET", "POST"])
def register_view(request):
    """Vista para el registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('catalyst_app:dashboard')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obtener datos del formulario
                first_name = request.POST.get('first_name', '').strip()
                last_name = request.POST.get('last_name', '').strip()
                email = request.POST.get('email', '').strip().lower()
                username = request.POST.get('username', '').strip()
                password = request.POST.get('password', '').strip()
                password_confirm = request.POST.get('password_confirm', '').strip()
                company_name = request.POST.get('company_name', '').strip()
                plan = request.POST.get('plan', 'basico').strip()
                payment_method = request.POST.get('payment_method', 'prueba').strip()
                
                # Debug: Print de POST raw
                print(f"\n{'='*60}")
                print(f"REQUEST.POST RECIBIDO:")
                for key, value in request.POST.items():
                    if key != 'csrfmiddlewaretoken':
                        print(f"  {key}: '{value}'")
                print(f"{'='*60}\n")
                
                # Debug: Log de datos procesados
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"Datos procesados: first_name='{first_name}' ({len(first_name)}), email='{email}' ({len(email)}), company_name='{company_name}' ({len(company_name)})")
                
                # Validaciones
                errors = {}
                
                # Validar cada campo individualmente
                if not first_name:
                    errors['first_name'] = 'El nombre es obligatorio'
                
                if not last_name:
                    errors['last_name'] = 'El apellido es obligatorio'
                
                if not email:
                    errors['email_required'] = 'El email es obligatorio'
                
                if not username:
                    errors['username_required'] = 'El nombre de usuario es obligatorio'
                
                if not password:
                    errors['password_required'] = 'La contraseña es obligatoria'
                
                if not password_confirm:
                    errors['password_confirm_required'] = 'Confirma tu contraseña'
                
                if not company_name:
                    errors['company_name_required'] = 'El nombre de empresa es obligatorio'
                
                # Validaciones adicionales solo si los campos básicos están llenos
                if first_name and last_name and email and username and password and company_name:
                    
                    if len(password) < 8:
                        errors['password_length'] = 'La contraseña debe tener al menos 8 caracteres'
                    
                    if password_confirm and password != password_confirm:
                        errors['password_match'] = 'Las contraseñas no coinciden'
                    
                    if User.objects.filter(username=username).exists():
                        errors['username_duplicate'] = 'Este usuario ya existe'
                    
                    if User.objects.filter(email=email).exists():
                        errors['email_duplicate'] = 'Este email ya está registrado'
                    
                    if Company.objects.filter(email=email).exists():
                        errors['company_email_duplicate'] = 'Este email de empresa ya está registrado'
                
                if plan not in ['basico', 'estandar', 'premium']:
                    errors['plan_invalid'] = 'Por favor selecciona un plan válido'
                
                if not payment_method or payment_method not in ['tarjeta', 'paypal', 'transferencia', 'prueba']:
                    errors['payment_invalid'] = 'Por favor selecciona un método de pago válido'
                
                if errors:
                    print(f"\n{'='*60}")
                    print(f"ERRORES DE VALIDACIÓN:")
                    for key, msg in errors.items():
                        print(f"  {key}: {msg}")
                    print(f"{'='*60}\n")
                    return render(request, 'register.html', {'errors': errors})
                
                # Generar RUT único para la empresa
                import random
                unique_rut = False
                rut_base = random.randint(100000000, 999999999)
                while not unique_rut:
                    rut_candidate = str(rut_base)
                    if not Company.objects.filter(rut=rut_candidate).exists():
                        unique_rut = True
                        rut = rut_candidate
                    else:
                        rut_base = random.randint(100000000, 999999999)
                
                # Crear empresa con email
                company = Company.objects.create(
                    name=company_name,
                    email=email,
                    rut=rut  # RUT único generado
                )
                
                # Crear usuario
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    company=company,
                    role='admin_cliente'  # El primer admin de la empresa
                )
                
                # Crear suscripción con el plan seleccionado
                start_date = now().date()
                end_date = start_date + timedelta(days=30)  # 30 días de prueba
                
                subscription = Subscription.objects.create(
                    company=company,
                    plan_name=plan,
                    start_date=start_date,
                    end_date=end_date,
                    active=True
                )
                
                # Registrar método de pago (simulado)
                user.payment_method = payment_method
                user.save()
                
                # Autenticar e iniciar sesión
                login(request, user)
                return redirect('catalyst_app:dashboard')
                
        except Exception as e:
            return render(request, 'register.html', {
                'errors': {'general': f'Error al registrar: {str(e)}'}
            })
    
    return render(request, 'register.html')


@login_required(login_url='catalyst_app:login')
@require_http_methods(["POST"])
def logout_view(request):
    """Vista para logout"""
    logout(request)
    return redirect('catalyst_app:login')


@require_http_methods(["GET"])
def error_view(request, error_code=500):
    """Vista genérica para mostrar errores"""
    return render(request, 'error.html', {
        'error_code': error_code
    }, status=error_code)


@login_required(login_url='catalyst_app:login')
@require_http_methods(["GET"])
def clientes_view(request):
    """Vista para la página de gestión de clientes - Plan PREMIUM"""
    # Verificar si el usuario tiene acceso a CRM (Plan PREMIUM)
    try:
        plan = request.user.company.subscription.plan_name
    except AttributeError:
        plan = 'basico'
    
    if plan != 'premium':
        return render(request, 'error.html', {
            'error_code': 403,
            'error_message': 'Esta funcionalidad requiere Plan PREMIUM o superior'
        }, status=403)
    
    context = {
        'page_title': 'Gestión de Clientes',
        'plan_name': plan,
    }
    return render(request, 'clientes.html', context)


@login_required(login_url='catalyst_app:login')
@require_http_methods(["GET"])
def campanas_view(request):
    """Vista para la página de campañas marketing - Plan PREMIUM"""
    # Verificar si el usuario tiene acceso a Marketing (Plan PREMIUM)
    try:
        plan = request.user.company.subscription.plan_name
    except AttributeError:
        plan = 'basico'
    
    if plan != 'premium':
        return render(request, 'error.html', {
            'error_code': 403,
            'error_message': 'Esta funcionalidad requiere Plan PREMIUM o superior'
        }, status=403)
    
    context = {
        'page_title': 'Marketing Automation',
        'plan_name': plan,
    }
    return render(request, 'campanas.html', context)


@login_required(login_url='catalyst_app:login')
@require_http_methods(["GET"])
def leads_view(request):
    """Vista para la página de gestión de leads - Plan PREMIUM"""
    # Verificar si el usuario tiene acceso a Leads (Plan PREMIUM)
    try:
        plan = request.user.company.subscription.plan_name
    except AttributeError:
        plan = 'basico'
    
    if plan != 'premium':
        return render(request, 'error.html', {
            'error_code': 403,
            'error_message': 'Esta funcionalidad requiere Plan PREMIUM o superior'
        }, status=403)
    
    context = {
        'page_title': 'Gestión de Leads',
        'plan_name': plan,
    }
    return render(request, 'leads.html', context)


@login_required(login_url='catalyst_app:login')
@require_http_methods(["GET"])
def dashboard_vendedor_view(request):
    """Vista para el dashboard de vendedores"""
    if request.user.role != 'vendedor':
        return render(request, 'error.html', {
            'error_code': 403,
            'error_message': 'No tienes permisos para acceder a esta página'
        }, status=403)
    
    context = {
        'page_title': 'Mi Desempeño',
        'user_name': request.user.get_full_name()
    }
    return render(request, 'dashboard_vendedor.html', context)


@login_required(login_url='catalyst_app:login')
@require_http_methods(["GET"])
def dashboard_gerente_view(request):
    """Vista para el dashboard de gerentes"""
    if request.user.role not in ['gerente', 'admin_cliente']:
        return render(request, 'error.html', {
            'error_code': 403,
            'error_message': 'No tienes permisos para acceder a esta página'
        }, status=403)
    
    context = {
        'page_title': 'Gestión de Equipo',
        'user_name': request.user.get_full_name()
    }
    return render(request, 'dashboard_gerente.html', context)


# Manejadores de errores 404 y 500
def handler404(request, exception=None):
    """Manejador para error 404"""
    return render(request, 'error.html', {
        'error_code': 404,
        'error_message': 'Página no encontrada'
    }, status=404)


def handler500(request):
    """Manejador para error 500"""
    return render(request, 'error.html', {
        'error_code': 500,
        'error_message': 'Error interno del servidor'
    }, status=500)


def handler403(request, exception=None):
    """Manejador para error 403"""
    return render(request, 'error.html', {
        'error_code': 403,
        'error_message': 'Acceso denegado'
    }, status=403)
