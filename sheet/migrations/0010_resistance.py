# Generated by Django 2.2.3 on 2021-02-27 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rulebook', '0028_damagetype'),
        ('sheet', '0009_inventoryitem_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resistance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0)),
                ('owner', models.ForeignKey(on_delete=models.CASCADE, related_name='resistances', to='sheet.Character')),
                ('type', models.ForeignKey(on_delete=models.CASCADE, to='rulebook.DamageType')),
            ],
        ),
    ]
