# Generated by Django 5.0.4 on 2024-04-24 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myups', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package_tmp',
            name='del_time',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='package_tmp',
            name='ld_time',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='package_tmp',
            name='pkup_time',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]