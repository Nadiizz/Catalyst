from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.catalyst_app.models.sales import Sale
from apps.catalyst_app.models.users import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendor_stats(request):
    """
    Obtiene estadísticas de ventas para un vendedor
    """
    user = request.user
    
    # Si no es vendedor, denegar acceso
    if user.role not in ['vendedor']:
        return Response({'error': 'No autorizado'}, status=403)
    
    # Obtener mes actual
    today = timezone.now().date()
    first_day = today.replace(day=1)
    
    # Mes anterior
    if first_day.month == 1:
        prev_first = first_day.replace(year=first_day.year - 1, month=12)
    else:
        prev_first = first_day.replace(month=first_day.month - 1)
    
    if prev_first.month == 1:
        prev_last = prev_first.replace(year=prev_first.year - 1, month=12, day=31)
    else:
        prev_last = (prev_first.replace(day=1) - timedelta(days=1))
    
    # Ventas este mes
    current_sales = Sale.objects.filter(
        seller=user,
        created_at__date__gte=first_day
    )
    
    # Ventas mes anterior
    prev_sales = Sale.objects.filter(
        seller=user,
        created_at__date__gte=prev_first,
        created_at__date__lte=prev_last
    )
    
    total_current = current_sales.aggregate(Sum('total'))['total__sum'] or 0
    total_prev = prev_sales.aggregate(Sum('total'))['total__sum'] or 0
    
    # Calcular cambio porcentual
    sales_change = 0
    if total_prev > 0:
        sales_change = ((total_current - total_prev) / total_prev) * 100
    
    # Estadísticas básicas
    transaction_count = current_sales.count()
    avg_ticket = current_sales.aggregate(Avg('total'))['total__avg'] or 0
    estimated_commission = total_current * 0.05  # 5% de comisión
    
    # Ventas por día (últimos 30 días)
    daily_sales = []
    for i in range(30):
        day = today - timedelta(days=i)
        day_sales = Sale.objects.filter(
            seller=user,
            created_at__date=day
        ).aggregate(Sum('total'))['total__sum'] or 0
        daily_sales.append({
            'date': day.strftime('%d/%m'),
            'amount': float(day_sales)
        })
    daily_sales.reverse()
    
    # Métodos de pago
    payment_methods = current_sales.values('payment_method').annotate(
        total=Sum('total'),
        count=Count('id')
    )
    
    # Productos más vendidos
    from apps.catalyst_app.models.sales import SaleItem
    top_products = SaleItem.objects.filter(
        sale__seller=user,
        sale__created_at__date__gte=first_day
    ).values('product__name').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('subtotal'),
        ticket_count=Count('sale_id', distinct=True)
    ).order_by('-total_revenue')[:5]
    
    # Últimas 10 ventas
    recent_sales = current_sales.values(
        'id', 'receipt_number', 'customer_name', 'total',
        'payment_method', 'created_at'
    ).order_by('-created_at')[:10]
    
    # Mapear display de métodos de pago
    payment_display = {
        'efectivo': 'Efectivo',
        'tarjeta_debito': 'Débito',
        'tarjeta_credito': 'Crédito',
        'transferencia': 'Transferencia',
        'cheque': 'Cheque',
        'otro': 'Otro'
    }
    
    for sale in recent_sales:
        sale['payment_method_display'] = payment_display.get(sale['payment_method'], sale['payment_method'])
    
    return Response({
        'total_sales': float(total_current),
        'sales_change': sales_change,
        'transaction_count': transaction_count,
        'avg_ticket': float(avg_ticket),
        'estimated_commission': float(estimated_commission),
        'daily_sales': {
            'labels': [d['date'] for d in daily_sales],
            'values': [d['amount'] for d in daily_sales]
        },
        'payment_methods': {
            'labels': [payment_display.get(pm['payment_method'], pm['payment_method']) 
                      for pm in payment_methods],
            'values': [pm['count'] for pm in payment_methods]
        },
        'recent_sales': list(recent_sales),
        'top_products': list(top_products)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_stats(request):
    """
    Obtiene estadísticas de equipo para un gerente
    """
    user = request.user
    company = user.company
    
    # Si no es gerente, denegar acceso
    if user.role not in ['gerente', 'admin_cliente']:
        return Response({'error': 'No autorizado'}, status=403)
    
    # Obtener mes actual
    today = timezone.now().date()
    first_day = today.replace(day=1)
    
    # Mes anterior
    if first_day.month == 1:
        prev_first = first_day.replace(year=first_day.year - 1, month=12)
    else:
        prev_first = first_day.replace(month=first_day.month - 1)
    
    if prev_first.month == 1:
        prev_last = prev_first.replace(year=prev_first.year - 1, month=12, day=31)
    else:
        prev_last = (prev_first.replace(day=1) - timedelta(days=1))
    
    # Obtener vendedores del mismo equipo/sucursal del gerente
    vendors = User.objects.filter(
        company=company,
        role='vendedor'
    )
    
    # Ventas del equipo este mes
    current_team_sales = Sale.objects.filter(
        seller__in=vendors,
        created_at__date__gte=first_day
    )
    
    # Ventas del equipo mes anterior
    prev_team_sales = Sale.objects.filter(
        seller__in=vendors,
        created_at__date__gte=prev_first,
        created_at__date__lte=prev_last
    )
    
    total_current = current_team_sales.aggregate(Sum('total'))['total__sum'] or 0
    total_prev = prev_team_sales.aggregate(Sum('total'))['total__sum'] or 0
    
    # Calcular cambio porcentual
    sales_change = 0
    if total_prev > 0:
        sales_change = ((total_current - total_prev) / total_prev) * 100
    
    # Número de vendedores activos
    active_sellers = vendors.filter(is_active=True).count()
    
    # Ticket promedio del equipo
    team_avg_ticket = current_team_sales.aggregate(Avg('total'))['total__avg'] or 0
    
    # Mejor vendedor del mes
    top_seller = None
    top_seller_sales = Sale.objects.filter(
        seller__in=vendors,
        created_at__date__gte=first_day
    ).values('seller__first_name', 'seller__last_name').annotate(
        total_sales=Sum('total')
    ).order_by('-total_sales').first()
    
    if top_seller_sales:
        top_seller = {
            'name': f"{top_seller_sales['seller__first_name']} {top_seller_sales['seller__last_name']}",
            'sales': float(top_seller_sales['total_sales'])
        }
    
    # Desempeño de cada vendedor
    team_performance = []
    for vendor in vendors:
        vendor_sales = current_team_sales.filter(seller=vendor)
        vendor_prev_sales = prev_team_sales.filter(seller=vendor)
        
        vendor_total = vendor_sales.aggregate(Sum('total'))['total__sum'] or 0
        vendor_prev_total = vendor_prev_sales.aggregate(Sum('total'))['total__sum'] or 0
        
        vendor_change = 0
        if vendor_prev_total > 0:
            vendor_change = ((vendor_total - vendor_prev_total) / vendor_prev_total) * 100
        
        team_performance.append({
            'name': f"{vendor.first_name} {vendor.last_name}",
            'total_sales': float(vendor_total),
            'transaction_count': vendor_sales.count(),
            'avg_ticket': float(vendor_sales.aggregate(Avg('total'))['total__avg'] or 0),
            'commission': float(vendor_total * 0.05),
            'change_percentage': vendor_change,
            'status': 'active' if vendor.is_active else 'inactive'
        })
    
    # Ventas por día (últimos 7 días para desempeño semanal)
    weekly_sales = []
    for i in range(7):
        day = today - timedelta(days=i)
        day_sales = current_team_sales.filter(
            created_at__date=day
        ).aggregate(Sum('total'))['total__sum'] or 0
        weekly_sales.append({
            'date': day.strftime('%a'),
            'amount': float(day_sales)
        })
    weekly_sales.reverse()
    
    # Ventas por vendedor
    seller_sales = []
    for vendor in vendors:
        vendor_total = current_team_sales.filter(seller=vendor).aggregate(Sum('total'))['total__sum'] or 0
        seller_sales.append({
            'name': f"{vendor.first_name} {vendor.last_name}",
            'sales': float(vendor_total)
        })
    seller_sales.sort(key=lambda x: x['sales'], reverse=True)
    
    # Últimas transacciones del equipo
    payment_display = {
        'efectivo': 'Efectivo',
        'tarjeta_debito': 'Débito',
        'tarjeta_credito': 'Crédito',
        'transferencia': 'Transferencia',
        'cheque': 'Cheque',
        'otro': 'Otro'
    }
    
    recent_transactions = current_team_sales.values(
        'id', 'receipt_number', 'seller__first_name', 'seller__last_name',
        'customer_name', 'total', 'payment_method', 'created_at'
    ).order_by('-created_at')[:10]
    
    for trans in recent_transactions:
        trans['seller_name'] = f"{trans['seller__first_name']} {trans['seller__last_name']}"
        trans['payment_method_display'] = payment_display.get(trans['payment_method'], trans['payment_method'])
    
    return Response({
        'total_team_sales': float(total_current),
        'sales_change': sales_change,
        'active_sellers': active_sellers,
        'team_avg_ticket': float(team_avg_ticket),
        'top_seller': top_seller,
        'team_performance': team_performance,
        'seller_sales': {
            'labels': [s['name'] for s in seller_sales[:5]],
            'values': [s['sales'] for s in seller_sales[:5]]
        },
        'weekly_performance': {
            'labels': [d['date'] for d in weekly_sales],
            'values': [d['amount'] for d in weekly_sales]
        },
        'recent_transactions': list(recent_transactions)
    })
