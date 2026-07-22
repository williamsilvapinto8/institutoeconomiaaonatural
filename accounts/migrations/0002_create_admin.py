from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    
    # Puxa a senha do Coolify. Se a variável não existir, usa um fallback (útil para desenvolvimento local)
    admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'senha_padrao_local_123')
    
    if not User.objects.filter(username='admin').exists():
        User.objects.create(
            username='admin',
            email='admin@example.com',
            password=make_password(admin_password),
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
