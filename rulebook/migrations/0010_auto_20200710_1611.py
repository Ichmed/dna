# Generated by Django 2.2.3 on 2020-07-10 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rulebook', '0009_auto_20200710_1524'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ability',
            name='requires',
        ),
        migrations.AddField(
            model_name='ability',
            name='requires',
            field=models.ManyToManyField(blank=True, related_name='_ability_requires_+', to='rulebook.Ability'),
        ),
        migrations.AlterField(
            model_name='ability',
            name='requires_raw',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
