# Generated by Django 3.1.7 on 2021-03-14 14:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sheet', '0018_auto_20210314_1541'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventoryitem',
            name='owner',
        ),
        migrations.CreateModel(
            name='InventorySlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('S', 'Single'), ('M', 'Multi')], max_length=1)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inventory', to='sheet.character')),
            ],
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='slot',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item', to='sheet.inventoryslot'),
        ),
    ]
