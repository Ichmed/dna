# Generated by Django 2.2.3 on 2020-07-17 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rulebook', '0025_auto_20200716_1813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ability',
            name='DELETED',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='armor',
            name='DELETED',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='creature',
            name='DELETED',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='enchantment',
            name='DELETED',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='feature',
            name='DELETED',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='DELETED',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='race',
            name='DELETED',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='rule',
            name='DELETED',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='skill',
            name='DELETED',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='substance',
            name='DELETED',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weapon',
            name='DELETED',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
