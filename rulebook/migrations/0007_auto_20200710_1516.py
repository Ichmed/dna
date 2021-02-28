# Generated by Django 2.2.3 on 2020-07-10 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rulebook', '0006_rule'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expansion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='rule',
            name='tags',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]
