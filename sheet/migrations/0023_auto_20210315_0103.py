# Generated by Django 3.1.7 on 2021-03-15 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sheet', '0022_auto_20210315_0101'),
    ]

    operations = [
        migrations.AddField(
            model_name='weaponinstance',
            name='dice_damage',
            field=models.CharField(blank=True, default='', max_length=2),
        ),
        migrations.AddField(
            model_name='weaponinstance',
            name='flat_damage',
            field=models.CharField(blank=True, default='', max_length=2),
        ),
    ]