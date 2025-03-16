from django.db import migrations

def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')

    group_names = ["Admin", "Patron", "Anonymous", "Librarian"]
    for group_name in group_names:
        Group.objects.get_or_create(name=group_name)

class Migration(migrations.Migration):

    dependencies = [
        ('techCLA', '0001_initial'),  # Replace with the last migration file
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]
