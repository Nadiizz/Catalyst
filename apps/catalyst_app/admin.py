from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Company, Subscription, Product, Branch, Inventory,
    InventoryMovement, Supplier, Purchase, PurchaseItem,
    Sale, SaleItem, Payment, Order, OrderItem, ShoppingCart, CartItem
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin para el modelo User personalizado"""
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Últimas Actividades', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
        ('TemucoSoft', {
            'fields': ('role', 'rut', 'company', 'created_at', 'updated_at'),
        }),
    )
    list_display = ('username', 'email', 'get_full_name', 'role', 'company', 'is_active')
    list_filter = ('role', 'company', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'rut', 'first_name', 'last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin para empresas cliente"""
    list_display = ('name', 'rut', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'rut', 'email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'rut', 'email', 'phone', 'address', 'logo')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin para suscripciones"""
    list_display = ('company', 'plan_name', 'start_date', 'end_date', 'active')
    list_filter = ('plan_name', 'active', 'start_date')
    search_fields = ('company__name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin para productos"""
    list_display = ('sku', 'name', 'category', 'price', 'cost', 'company', 'is_active')
    list_filter = ('category', 'company', 'is_active', 'created_at')
    search_fields = ('sku', 'name', 'category')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información del Producto', {
            'fields': ('company', 'sku', 'name', 'description', 'category', 'image')
        }),
        ('Precios', {
            'fields': ('price', 'cost')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    """Admin para sucursales"""
    list_display = ('name', 'company', 'manager', 'phone', 'is_active')
    list_filter = ('company', 'is_active', 'created_at')
    search_fields = ('name', 'address', 'phone')
    readonly_fields = ('created_at', 'updated_at')


class InventoryMovementInline(admin.TabularInline):
    """Inline para movimientos de inventario"""
    model = InventoryMovement
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    """Admin para inventario"""
    list_display = ('product', 'branch', 'stock', 'reorder_point')
    list_filter = ('branch', 'created_at')
    search_fields = ('product__name', 'product__sku', 'branch__name')
    readonly_fields = ('created_at', 'updated_at', 'last_counted')
    inlines = [InventoryMovementInline]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Admin para proveedores"""
    list_display = ('name', 'rut', 'company', 'phone', 'is_active')
    list_filter = ('company', 'is_active', 'created_at')
    search_fields = ('name', 'rut', 'email')
    readonly_fields = ('created_at', 'updated_at')


class PurchaseItemInline(admin.TabularInline):
    """Inline para items de compra"""
    model = PurchaseItem
    extra = 0


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """Admin para compras a proveedores"""
    list_display = ('invoice_number', 'supplier', 'branch', 'purchase_date', 'total_amount', 'payment_status')
    list_filter = ('supplier', 'payment_status', 'purchase_date')
    search_fields = ('invoice_number', 'supplier__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PurchaseItemInline]


class SaleItemInline(admin.TabularInline):
    """Inline para items de venta"""
    model = SaleItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """Admin para ventas POS"""
    list_display = ('receipt_number', 'branch', 'seller', 'total', 'payment_method', 'created_at')
    list_filter = ('branch', 'payment_method', 'created_at')
    search_fields = ('receipt_number', 'customer_name', 'customer_rut')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SaleItemInline]
    date_hierarchy = 'created_at'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin para órdenes e-commerce"""
    list_display = ('order_number', 'company', 'customer_email', 'status', 'payment_status', 'total', 'created_at')
    list_filter = ('company', 'status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'customer_email', 'customer_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información de la Orden', {
            'fields': ('order_number', 'company', 'user', 'status', 'payment_status')
        }),
        ('Datos del Cliente', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'customer_rut')
        }),
        ('Dirección de Envío', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_zip')
        }),
        ('Montos', {
            'fields': ('subtotal', 'tax', 'shipping_cost', 'discount', 'total')
        }),
        ('Notas y Fechas', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
    date_hierarchy = 'created_at'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Admin para carros de compras"""
    list_display = ('id', 'user', 'company', 'get_item_count', 'updated_at')
    list_filter = ('company', 'updated_at')
    search_fields = ('user__username', 'session_key')
    readonly_fields = ('created_at', 'updated_at')

