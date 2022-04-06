# Generated by Django 3.2.4 on 2022-04-04 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_loadevent_min_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loadevent',
            name='max_id',
        ),
        migrations.RemoveField(
            model_name='loadevent',
            name='min_id',
        ),
        migrations.AddField(
            model_name='loadevent',
            name='n_records_origin',
            field=models.IntegerField(blank=True, null=True, verbose_name='Number of records to download'),
        ),
        migrations.AddField(
            model_name='loadevent',
            name='n_records_pulled',
            field=models.IntegerField(blank=True, null=True, verbose_name='Number of records to download'),
        ),
        migrations.AddField(
            model_name='loadevent',
            name='url_used',
            field=models.TextField(blank=True, null=True, verbose_name='List of succesully created local pages'),
        ),
    ]
