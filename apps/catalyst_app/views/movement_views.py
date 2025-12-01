"""
MOVEMENT_VIEWS.PY - ViewSet para movimientos de inventario
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction

from apps.catalyst_app.models import InventoryMovement, Inventory
from apps.catalyst_app.serializers.inventory_serializers import InventoryMovementSerializer


class InventoryMovementViewSet(viewsets.ModelViewSet):
    """ViewSet para registrar movimientos de inventario"""
    queryset = InventoryMovement.objects.all()
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar movimientos por company del usuario"""
        user = self.request.user
        if user.is_super_admin():
            return InventoryMovement.objects.all()
        if user.company:
            return InventoryMovement.objects.filter(
                inventory__branch__company=user.company
            )
        return InventoryMovement.objects.none()
    
    @transaction.atomic
    def perform_create(self, serializer):
        """
        Crear movimiento y actualizar el stock del inventario
        """
        user = self.request.user
        movement = serializer.save(user=user)
        
        # Obtener el inventario relacionado
        inventory = movement.inventory
        
        # Actualizar stock según el tipo de movimiento
        if movement.movement_type in ['entrada', 'devolucion']:
            # Sumar al stock
            inventory.stock += movement.quantity
        elif movement.movement_type in ['salida']:
            # Restar del stock
            if inventory.stock < movement.quantity:
                raise ValueError('Stock insuficiente para realizar esta salida')
            inventory.stock -= movement.quantity
        elif movement.movement_type == 'ajuste':
            # Para ajustes, la cantidad se interpreta como el nuevo stock
            # (o cambio si es positivo/negativo)
            # Aquí mantenemos la cantidad como cambio
            inventory.stock += movement.quantity
        
        inventory.save()
