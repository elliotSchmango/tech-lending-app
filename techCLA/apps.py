from django.apps import AppConfig
from django.contrib.auth.models import Group


class TechclaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'techCLA'

    def ready(self):
        import techCLA.signals

        Group.objects.get_or_create(name='Patron')
        Group.objects.get_or_create(name='Librarian')
        Group.objects.get_or_create(name='Admin')
