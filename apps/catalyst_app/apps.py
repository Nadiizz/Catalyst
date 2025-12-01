from django.apps import AppConfig


class CatalystAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.catalyst_app'
    verbose_name = 'TemucoSoft - Aplicación Principal'
    
    def ready(self):
        """Importar signals cuando la app está lista"""
        import apps.catalyst_app.signals

