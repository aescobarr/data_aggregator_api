# Generated by Django 3.2.4 on 2022-04-06 07:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_dataproject_stats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stats',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.region'),
        ),
    ]
