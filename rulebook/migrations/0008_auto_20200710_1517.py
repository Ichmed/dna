# Generated by Django 2.2.3 on 2020-07-10 13:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rulebook', '0007_auto_20200710_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='ability',
            name='expansion',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='rulebook.Expansion'),
        ),
        migrations.AddField(
            model_name='rule',
            name='expansion',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='rulebook.Expansion'),
        ),
    ]
