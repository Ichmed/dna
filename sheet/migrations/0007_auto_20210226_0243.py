# Generated by Django 2.2.3 on 2021-02-26 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sheet', '0006_auto_20210226_0242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='container',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, related_name='content', to='sheet.InventoryItem'),
        ),
    ]
