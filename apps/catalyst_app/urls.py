from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from apps.catalyst_app.views.user_views import UserViewSet, CompanyViewSet, SubscriptionViewSet
from apps.catalyst_app.views.product_views import ProductViewSet
from apps.catalyst_app.views.inventory_views import BranchViewSet, InventoryViewSet
from apps.catalyst_app.views.movement_views import InventoryMovementViewSet
from apps.catalyst_app.views.supplier_views import SupplierViewSet, PurchaseViewSet
from apps.catalyst_app.views.sales_views import SaleViewSet
from apps.catalyst_app.views.branch_views import OrderViewSet, ShoppingCartViewSet
from apps.catalyst_app.views.stats_views import vendor_stats, manager_stats
from apps.catalyst_app.template_views import (
    index_view, dashboard_view, login_view, register_view, logout_view, planes_view, error_view,
    productos_view, usuarios_view, ventas_view, ordenes_view,
    inventario_view, proveedores_view, sucursales_view, clientes_view, campanas_view, leads_view,
    dashboard_vendedor_view, dashboard_gerente_view
)

# Crear router de Django REST Framework
router = DefaultRouter()

# Registrar ViewSets
router.register(r'users', UserViewSet, basename='user')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'inventory-movements', InventoryMovementViewSet, basename='inventory-movement')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'purchases', PurchaseViewSet, basename='purchase')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'carts', ShoppingCartViewSet, basename='shopping-cart')

app_name = 'catalyst_app'

urlpatterns = [
    # API Documentation Routes
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='catalyst_app:schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='catalyst_app:schema'), name='redoc'),
    
    # API Routes
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    
    # Stats endpoints
    path('sales/vendor-stats/', vendor_stats, name='vendor-stats'),
    path('sales/manager-stats/', manager_stats, name='manager-stats'),
    
    # Template Routes (HTML Pages)
    path('', index_view, name='index'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard-vendedor/', dashboard_vendedor_view, name='dashboard-vendedor'),
    path('dashboard-gerente/', dashboard_gerente_view, name='dashboard-gerente'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('planes/', planes_view, name='planes'),
    path('logout/', logout_view, name='logout'),
    path('error/<int:error_code>/', error_view, name='error'),
    
    # CRUD Template Routes
    path('productos/', productos_view, name='productos'),
    path('usuarios/', usuarios_view, name='usuarios'),
    path('ventas/', ventas_view, name='ventas'),
    path('ordenes/', ordenes_view, name='ordenes'),
    path('inventario/', inventario_view, name='inventario'),
    path('proveedores/', proveedores_view, name='proveedores'),
    path('sucursales/', sucursales_view, name='sucursales'),
    
    # CRM Routes (Plan PRO)
    path('clientes/', clientes_view, name='clientes'),
    path('campanas/', campanas_view, name='campanas'),
    path('leads/', leads_view, name='leads'),
]
