# Generated by Django 2.2.3 on 2021-02-27 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sheet', '0010_resistance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skillinstance',
            name='granted',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='skillinstance',
            name='level',
            field=models.IntegerField(default=1),
        ),
    ]
