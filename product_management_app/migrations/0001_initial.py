# Generated by Django 5.1.5 on 2025-02-12 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, max_length=10)),
                ('stock_availability', models.PositiveIntegerField(default=0)),
                ('tags', models.CharField(max_length=100)),
                ('images', models.ImageField(blank=True, null=True, upload_to='product_images/')),
            ],
        ),
    ]
