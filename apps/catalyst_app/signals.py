"""
SIGNALS.PY - Señales para manejo de eventos automáticos
Crea automáticamente inventarios cuando se crean productos o sucursales
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from apps.catalyst_app.models import Product, Inventory, Branch
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Product)
def create_inventory_for_product(sender, instance, created, **kwargs):
    """
    Cuando se crea un nuevo producto, crea automáticamente registros
    de inventario para todas las sucursales de la empresa.
    También se ejecuta para productos existentes para asegurar cobertura completa.
    """
    try:
        # Obtener todas las sucursales de la empresa
        branches = Branch.objects.filter(company=instance.company)
        
        if not branches.exists():
            logger.warning(f'No branches found for company {instance.company.id}')
            return
        
        # Crear un registro de inventario para cada sucursal si no existe
        for branch in branches:
            try:
                inventory, created_inv = Inventory.objects.get_or_create(
                    product=instance,
                    branch=branch,
                    defaults={
                        'stock': 0,
                        'reorder_point': 10
                    }
                )
                if created_inv:
                    logger.info(f'Inventory created for product {instance.id} ({instance.sku}) in branch {branch.id}')
            except Exception as e:
                logger.error(f'Error creating inventory for product {instance.id} in branch {branch.id}: {str(e)}')
                
    except Exception as e:
        logger.error(f'Error in create_inventory_for_product signal: {str(e)}')


@receiver(post_save, sender=Branch)
def create_inventory_for_branch(sender, instance, created, **kwargs):
    """
    Cuando se crea una nueva sucursal, crea automáticamente registros
    de inventario para todos los productos existentes en la empresa
    """
    if created:
        try:
            # Obtener todos los productos de la empresa
            products = Product.objects.filter(company=instance.company)
            
            if not products.exists():
                logger.info(f'No products found for company {instance.company.id}')
                return
            
            # Crear un registro de inventario para cada producto
            for product in products:
                try:
                    inventory, created_inv = Inventory.objects.get_or_create(
                        product=product,
                        branch=instance,
                        defaults={
                            'stock': 0,
                            'reorder_point': 10
                        }
                    )
                    if created_inv:
                        logger.info(f'Inventory created for branch {instance.id} ({instance.name}) with product {product.id}')
                except Exception as e:
                    logger.error(f'Error creating inventory for branch {instance.id} with product {product.id}: {str(e)}')
                    
        except Exception as e:
            logger.error(f'Error in create_inventory_for_branch signal: {str(e)}')
