# Generated by Django 2.2.3 on 2020-07-07 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rulebook', '0003_auto_20200707_2100'),
    ]

    operations = [
        migrations.AddField(
            model_name='ability',
            name='index',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
