# Generated by Django 4.2.7 on 2025-07-09 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents_api', '0003_validationrule'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='sentiment',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
