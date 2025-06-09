from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0003_add_description_to_vehicletype'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiclecategory',
            name='comparison_provider1_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='vehiclecategory',
            name='comparison_provider1_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='vehiclecategory',
            name='comparison_provider2_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='vehiclecategory',
            name='comparison_provider2_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
    ] 