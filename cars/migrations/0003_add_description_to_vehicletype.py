from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0002_add_missing_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicletype',
            name='description',
            field=models.TextField(blank=True),
        ),
    ] 