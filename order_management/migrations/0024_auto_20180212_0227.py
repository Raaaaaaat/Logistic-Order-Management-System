# Generated by Django 2.0 on 2018-02-12 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_management', '0023_auto_20180211_0436'),
    ]

    operations = [
        migrations.RenameField(
            model_name='log_trace',
            old_name='time',
            new_name='create_time',
        ),
        migrations.AddField(
            model_name='log_trace',
            name='create_user',
            field=models.CharField(max_length=100, null=True),
        ),
    ]