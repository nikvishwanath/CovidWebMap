# Generated by Django 4.1 on 2022-09-05 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_remove_data_latitude_remove_data_longitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='date_updated',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
