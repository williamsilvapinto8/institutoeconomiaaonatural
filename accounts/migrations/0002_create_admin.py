from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_superuser(apps, schema_editor):
    User = apps.get_model('accounts', 'Benegnado')
    if not User.objects.filter(username='admin').exists():
        User.objects.create(
            username='admin',
            email='admin@example.com',
            password=make_password('admin'),
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
