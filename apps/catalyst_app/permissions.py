from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    Permiso para verificar si el usuario es Super Admin de TemucoSoft.
    """
    message = 'Solo Super Admins pueden acceder.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_super_admin())


class IsAdminCliente(permissions.BasePermission):
    """
    Permiso para verificar si el usuario es Admin de Cliente.
    """
    message = 'Solo Admins de Cliente pueden acceder.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_cliente())


class IsGerente(permissions.BasePermission):
    """
    Permiso para verificar si el usuario es Gerente.
    """
    message = 'Solo Gerentes pueden acceder.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_gerente())


class IsVendedor(permissions.BasePermission):
    """
    Permiso para verificar si el usuario es Vendedor.
    """
    message = 'Solo Vendedores pueden acceder.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_vendedor())


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite a los propietarios editar sus propios objetos.
    Solo lectura para otros.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsCompanyMember(permissions.BasePermission):
    """
    Permiso que verifica si el usuario pertenece a la misma compañía que el objeto.
    """
    message = 'Solo miembros de la compañía pueden acceder.'
    
    def has_object_permission(self, request, view, obj):
        # Si es super admin, permitir
        if request.user.is_super_admin():
            return True
        
        # Si no tiene company, denegar
        if not request.user.company:
            return False
        
        # Verificar si el objeto tiene company
        if hasattr(obj, 'company'):
            return obj.company == request.user.company
        elif hasattr(obj, 'branch') and hasattr(obj.branch, 'company'):
            return obj.branch.company == request.user.company
        elif hasattr(obj, 'supplier') and hasattr(obj.supplier, 'company'):
            return obj.supplier.company == request.user.company
        elif hasattr(obj, 'user') and hasattr(obj.user, 'company'):
            return obj.user.company == request.user.company
        
        return False


class CanManageSales(permissions.BasePermission):
    """
    Permiso para gestionar ventas.
    Solo vendedores, gerentes y admins pueden crear/editar.
    """
    message = 'No tienes permisos para gestionar ventas.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.is_vendedor() or request.user.is_gerente() or request.user.is_admin_cliente()


class CanManagePurchases(permissions.BasePermission):
    """
    Permiso para gestionar compras.
    Solo gerentes y admins pueden crear/editar.
    """
    message = 'No tienes permisos para gestionar compras.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.is_gerente() or request.user.is_admin_cliente()


class ReadOnly(permissions.BasePermission):
    """
    Permiso que solo permite métodos de lectura.
    """
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
