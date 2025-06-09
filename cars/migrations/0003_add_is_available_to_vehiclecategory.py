from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0002_vehiclecategorytype_vehicleimage_vehicletype_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiclecategory',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ] 