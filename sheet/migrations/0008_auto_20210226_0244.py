# Generated by Django 2.2.3 on 2021-02-26 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sheet', '0007_auto_20210226_0243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='amount',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete='Cascade', related_name='inventory', to='sheet.Character'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='weight',
            field=models.IntegerField(default=0),
        ),
    ]
