# Generated by Django 3.1.7 on 2021-03-15 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sheet', '0023_auto_20210315_0103'),
    ]

    operations = [
        migrations.AddField(
            model_name='weaponinstance',
            name='damage_type',
            field=models.CharField(blank=True, default='', max_length=1),
        ),
    ]
