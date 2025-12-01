from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Sum, Avg, Count
from datetime import datetime, timedelta
from apps.catalyst_app.models.customers import Customer, Interaction, ContactOpportunity
import json

@login_required
def clientes(request):
    """Vista principal de gestión de clientes"""
    clientes = Customer.objects.filter(is_active=True)
    
    # Filtros
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    segment = request.GET.get('segment', '')
    
    if search:
        clientes = clientes.filter(Q(name__icontains=search) | Q(email__icontains=search))
    if status:
        clientes = clientes.filter(status=status)
    if segment:
        clientes = clientes.filter(segment=segment)
    
    # Estadísticas
    stats = {
        'total': Customer.objects.filter(is_active=True).count(),
        'prospects': Customer.objects.filter(status='prospect').count(),
        'leads': Customer.objects.filter(status='lead').count(),
        'clients': Customer.objects.filter(status='cliente').count(),
        'avg_lifetime_value': Customer.objects.aggregate(Avg('lifetime_value'))['lifetime_value__avg'] or 0,
    }
    
    context = {
        'clientes': clientes[:100],  # Limitar para demo
        'stats': stats,
        'statuses': Customer.STATUS_CHOICES,
        'segments': ['Premium', 'Estándar', 'Económico', 'VIP'],
    }
    
    return render(request, 'clientes.html', context)


@login_required
def cliente_detail(request, id):
    """Vista de detalle de cliente"""
    cliente = get_object_or_404(Customer, id=id)
    interactions = cliente.interactions.all()[:10]
    opportunities = cliente.opportunities.all()
    
    context = {
        'cliente': cliente,
        'interactions': interactions,
        'opportunities': opportunities,
    }
    
    return render(request, 'cliente_detail.html', context)


@login_required
@require_POST
def api_clientes_crear(request):
    """API para crear cliente"""
    try:
        data = json.loads(request.body)
        
        cliente = Customer.objects.create(
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            company=data.get('company', ''),
            status=data.get('status', 'prospect'),
            segment=data.get('segment', ''),
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Cliente creado exitosamente',
            'cliente_id': cliente.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_POST
def api_clientes_actualizar(request, id):
    """API para actualizar cliente"""
    try:
        cliente = get_object_or_404(Customer, id=id)
        data = json.loads(request.body)
        
        for field, value in data.items():
            if hasattr(cliente, field):
                setattr(cliente, field, value)
        
        cliente.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cliente actualizado exitosamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_POST
def api_clientes_eliminar(request, id):
    """API para eliminar cliente (soft delete)"""
    try:
        cliente = get_object_or_404(Customer, id=id)
        cliente.is_active = False
        cliente.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cliente eliminado exitosamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
def api_clientes_lista(request):
    """API para obtener lista de clientes (JSON)"""
    clientes = Customer.objects.filter(is_active=True).values(
        'id', 'name', 'email', 'company', 'status', 'lead_score', 'lifetime_value', 'last_contacted'
    )
    
    return JsonResponse({
        'success': True,
        'data': list(clientes)
    })


@login_required
@require_POST
def api_registrar_interaccion(request, cliente_id):
    """API para registrar interacción con cliente"""
    try:
        cliente = get_object_or_404(Customer, id=cliente_id)
        data = json.loads(request.body)
        
        interaction = Interaction.objects.create(
            customer=cliente,
            interaction_type=data.get('type', 'otro'),
            subject=data.get('subject', ''),
            description=data.get('description', ''),
            outcome=data.get('outcome', ''),
            lead_score_impact=data.get('lead_score_impact', 0),
        )
        
        # Actualizar lead score
        cliente.lead_score += interaction.lead_score_impact
        cliente.last_contacted = datetime.now()
        cliente.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Interacción registrada',
            'interaction_id': interaction.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
