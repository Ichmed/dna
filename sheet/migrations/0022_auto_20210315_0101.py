# Generated by Django 3.1.7 on 2021-03-15 00:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sheet', '0021_inventoryitem_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='slot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='sheet.inventoryslot'),
        ),
        migrations.AlterField(
            model_name='weaponinstance',
            name='cost',
            field=models.CharField(blank=True, default='', max_length=2),
        ),
        migrations.AlterField(
            model_name='weaponinstance',
            name='force',
            field=models.CharField(blank=True, default='', max_length=2),
        ),
        migrations.AlterField(
            model_name='weaponinstance',
            name='hit',
            field=models.CharField(blank=True, default='', max_length=2),
        ),
        migrations.AlterField(
            model_name='weaponinstance',
            name='parry',
            field=models.CharField(blank=True, default='', max_length=2),
        ),
        migrations.AlterField(
            model_name='weaponinstance',
            name='range',
            field=models.CharField(blank=True, default='', max_length=2),
        ),
    ]