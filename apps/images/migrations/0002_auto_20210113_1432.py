# Generated by Django 3.1.5 on 2021-01-13 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='photo',
            field=models.ImageField(upload_to=''),
        ),
        migrations.AlterField(
            model_name='image',
            name='title',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]