# Generated by Django 5.2.3 on 2025-07-03 14:26

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents_api', '0002_workflow_alter_document_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ValidationRule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('document_type', models.CharField(max_length=50)),
                ('field_name', models.CharField(max_length=100)),
                ('rule_type', models.CharField(choices=[('regex', 'Regular Expression'), ('data_type', 'Data Type'), ('required', 'Required Field'), ('range', 'Value Range'), ('enum', 'Enumeration')], max_length=20)),
                ('rule_pattern', models.CharField(help_text='Regex pattern, data type name, or other validation criteria', max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
