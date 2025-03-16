from django.apps import AppConfig

class TechclaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'techCLA'

    def ready(self):
        import techCLA.signals