# Generated by Django 3.2.9 on 2021-12-12 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='detail',
            field=models.TextField(null=True),
        ),
    ]
