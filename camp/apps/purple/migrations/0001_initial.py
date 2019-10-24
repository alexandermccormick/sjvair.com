# Generated by Django 2.2.4 on 2019-10-24 09:53

import camp.utils.validators
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django_smalluuid.models
import resticus.encoders


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', django_smalluuid.models.SmallUUIDField(db_index=True, default=django_smalluuid.models.UUIDDefault(), editable=False, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('position', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('location', models.CharField(choices=[('inside', 'inside'), ('outside', 'outside')], max_length=10)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(default=list, encoder=resticus.encoders.JSONEncoder)),
                ('celcius', models.DecimalField(decimal_places=1, max_digits=4, null=True)),
                ('fahrenheit', models.DecimalField(decimal_places=1, max_digits=4, null=True)),
                ('humidity', models.DecimalField(decimal_places=1, max_digits=4, null=True)),
                ('pressure', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('pm2_a', django.contrib.postgres.fields.jsonb.JSONField(encoder=resticus.encoders.JSONEncoder, null=True, validators=[camp.utils.validators.JSONSchemaValidator({'properties': {'pm100_env': {'type': 'number'}, 'pm10_env': {'type': 'number'}, 'pm25_env': {'type': 'number'}, 'pm25_standard': {'type': 'number'}}, 'required': ['pm25_standard', 'pm10_env', 'pm25_env', 'pm100_env'], 'type': 'object'})])),
                ('pm2_b', django.contrib.postgres.fields.jsonb.JSONField(encoder=resticus.encoders.JSONEncoder, null=True, validators=[camp.utils.validators.JSONSchemaValidator({'properties': {'pm100_env': {'type': 'number'}, 'pm10_env': {'type': 'number'}, 'pm25_env': {'type': 'number'}, 'pm25_standard': {'type': 'number'}}, 'required': ['pm25_standard', 'pm10_env', 'pm25_env', 'pm100_env'], 'type': 'object'})])),
            ],
        ),
        migrations.CreateModel(
            name='PurpleAir',
            fields=[
                ('id', django_smalluuid.models.SmallUUIDField(db_index=True, default=django_smalluuid.models.UUIDDefault(), editable=False, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('purple_id', models.IntegerField(unique=True)),
                ('label', models.CharField(max_length=250)),
                ('position', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('location', models.CharField(choices=[('inside', 'inside'), ('outside', 'outside')], max_length=10)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(default=list, encoder=resticus.encoders.JSONEncoder)),
                ('latest', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='device_latest', to='purple.Entry')),
            ],
            options={
                'ordering': ['label'],
            },
        ),
        migrations.AddField(
            model_name='entry',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='purple.PurpleAir'),
        ),
    ]
