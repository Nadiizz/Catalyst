from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Avg, Count, Q
from datetime import datetime, timedelta
from apps.catalyst_app.models.marketing import EmailCampaign, MarketingAutomation, Lead, LeadScoringRule
import json
import random

@login_required
def campanas_marketing(request):
    """Vista principal de campañas de marketing"""
    campanas = EmailCampaign.objects.all()
    
    # Filtros
    status = request.GET.get('status', '')
    if status:
        campanas = campanas.filter(status=status)
    
    # Estadísticas generales
    stats = {
        'total_campaigns': EmailCampaign.objects.count(),
        'active_campaigns': EmailCampaign.objects.filter(status__in=['sending', 'scheduled']).count(),
        'avg_open_rate': EmailCampaign.objects.aggregate(Avg('open_rate'))['open_rate__avg'] or 0,
        'avg_click_rate': EmailCampaign.objects.aggregate(Avg('click_rate'))['click_rate__avg'] or 0,
        'total_leads': Lead.objects.count(),
        'qualified_leads': Lead.objects.filter(status='qualified').count(),
    }
    
    context = {
        'campanas': campanas[:50],
        'stats': stats,
        'statuses': EmailCampaign.STATUS_CHOICES,
    }
    
    return render(request, 'campanas.html', context)


@login_required
def campana_detail(request, id):
    """Vista de detalle de campaña"""
    campana = get_object_or_404(EmailCampaign, id=id)
    
    # Datos para gráficos
    chart_data = {
        'sent': campana.sent_count,
        'opened': campana.opened_count,
        'clicked': campana.clicked_count,
        'converted': campana.converted_count,
    }
    
    context = {
        'campana': campana,
        'chart_data': json.dumps(chart_data),
    }
    
    return render(request, 'campana_detail.html', context)


@login_required
def leads_management(request):
    """Vista para gestión de leads"""
    leads = Lead.objects.all()
    
    # Filtros
    source = request.GET.get('source', '')
    status = request.GET.get('status', '')
    
    if source:
        leads = leads.filter(source=source)
    if status:
        leads = leads.filter(status=status)
    
    # Estadísticas
    stats = {
        'total_leads': Lead.objects.count(),
        'new_leads': Lead.objects.filter(status='new').count(),
        'qualified_leads': Lead.objects.filter(status='qualified').count(),
        'converted_leads': Lead.objects.filter(status='converted').count(),
        'unqualified_leads': Lead.objects.filter(status='unqualified').count(),
        'avg_lead_score': Lead.objects.aggregate(Avg('lead_score'))['lead_score__avg'] or 0,
    }
    
    # Leads por fuente
    sources = Lead.objects.values('source').annotate(count=Count('id')).order_by('-count')
    
    context = {
        'leads': leads[:100],
        'stats': stats,
        'sources': sources,
        'sources_list': dict(Lead.SOURCE_CHOICES),
    }
    
    return render(request, 'leads.html', context)


@login_required
def automaciones(request):
    """Vista para automatizaciones de marketing"""
    automaciones = MarketingAutomation.objects.all()
    
    # Filtros
    status = request.GET.get('status', '')
    if status:
        automaciones = automaciones.filter(status=status)
    
    # Estadísticas
    stats = {
        'total_automations': MarketingAutomation.objects.count(),
        'active_automations': MarketingAutomation.objects.filter(status='active').count(),
        'total_triggers': MarketingAutomation.objects.aggregate(Sum('trigger_count'))['trigger_count__sum'] or 0,
    }
    
    context = {
        'automaciones': automaciones,
        'stats': stats,
        'statuses': MarketingAutomation.STATUS_CHOICES,
        'trigger_types': MarketingAutomation.TRIGGER_TYPES,
    }
    
    return render(request, 'automaciones.html', context)


# ============ APIs ============

@login_required
@require_POST
def api_crear_campana(request):
    """API para crear campaña"""
    try:
        data = json.loads(request.body)
        
        campana = EmailCampaign.objects.create(
            name=data.get('name', ''),
            subject=data.get('subject', ''),
            description=data.get('description', ''),
            html_content=data.get('html_content', ''),
            status='draft',
            target_segment=data.get('segment', ''),
            recipients_count=random.randint(50, 500),
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Campaña creada exitosamente',
            'campaign_id': campana.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@require_POST
def api_lanzar_campana(request, id):
    """API para lanzar campaña"""
    try:
        campana = get_object_or_404(EmailCampaign, id=id)
        
        campana.status = 'sending'
        campana.scheduled_at = datetime.now()
        
        # Simular métricas
        campana.sent_count = campana.recipients_count
        campana.opened_count = int(campana.recipients_count * random.uniform(0.15, 0.35))
        campana.clicked_count = int(campana.opened_count * random.uniform(0.2, 0.4))
        campana.converted_count = int(campana.clicked_count * random.uniform(0.05, 0.15))
        
        if campana.sent_count > 0:
            campana.open_rate = (campana.opened_count / campana.sent_count) * 100
            campana.click_rate = (campana.clicked_count / campana.sent_count) * 100
            campana.conversion_rate = (campana.converted_count / campana.sent_count) * 100
        
        campana.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Campaña enviada a {campana.sent_count} personas',
            'metrics': {
                'sent': campana.sent_count,
                'opened': campana.opened_count,
                'open_rate': f"{campana.open_rate:.1f}%",
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@require_POST
def api_crear_lead(request):
    """API para crear lead"""
    try:
        data = json.loads(request.body)
        
        lead = Lead.objects.create(
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            company=data.get('company', ''),
            job_title=data.get('job_title', ''),
            source=data.get('source', 'website'),
            lead_score=random.randint(0, 50),
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Lead creado exitosamente',
            'lead_id': lead.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@require_POST
def api_calificar_lead(request, id):
    """API para calificar lead"""
    try:
        lead = get_object_or_404(Lead, id=id)
        
        lead.status = 'qualified'
        lead.lead_score = min(100, lead.lead_score + random.randint(20, 40))
        lead.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Lead calificado',
            'new_score': lead.lead_score
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
def api_campanas_lista(request):
    """API para obtener lista de campañas"""
    campanas = EmailCampaign.objects.values(
        'id', 'name', 'status', 'sent_count', 'open_rate', 'click_rate', 'created_at'
    )
    
    return JsonResponse({
        'success': True,
        'data': list(campanas)
    })


@login_required
def api_leads_lista(request):
    """API para obtener lista de leads"""
    leads = Lead.objects.values(
        'id', 'first_name', 'last_name', 'email', 'company', 'source', 'status', 'lead_score'
    )
    
    return JsonResponse({
        'success': True,
        'data': list(leads)
    })
