# Generated by Django 5.1.2 on 2024-11-17 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ceramiapp', '0012_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]
