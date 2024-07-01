# Generated by Django 5.0.6 on 2024-07-01 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HexaCafe', '0005_cart_cartitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('hot', 'Hot Drinks'), ('cold', 'Cold Drinks'), ('cakes', 'Cakes'), ('breakfasts', 'Breakfasts')], max_length=50),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]