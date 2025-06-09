from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0004_add_comparison_fields_to_vehiclecategory'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleCategoryLocations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehiclecategory', models.ForeignKey(on_delete=models.CASCADE, to='cars.vehiclecategory')),
                ('location', models.ForeignKey(on_delete=models.CASCADE, to='locations.location')),
            ],
            options={
                'db_table': 'app_vehiclecategory_locations',
            },
        ),
        migrations.AddField(
            model_name='vehiclecategory',
            name='locations',
            field=models.ManyToManyField(through='cars.VehicleCategoryLocations', to='locations.location'),
        ),
    ] 