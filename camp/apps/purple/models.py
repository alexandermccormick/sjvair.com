from decimal import Decimal

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import JSONField
from django.utils.functional import cached_property

from django_smalluuid.models import SmallUUIDField, uuid_default
from model_utils import Choices
from resticus.encoders import JSONEncoder

from camp.utils.validators import JSONSchemaValidator

from . import api
from .schemas import PM2_SCHEMA


class PurpleAir(models.Model):
    LOCATION = Choices('inside', 'outside')

    id = SmallUUIDField(
        default=uuid_default(),
        primary_key=True,
        db_index=True,
        editable=False,
        verbose_name='ID'
    )

    purple_id = models.IntegerField()
    label = models.CharField(max_length=250)
    position = models.PointField(null=True)
    location = models.CharField(max_length=10, choices=LOCATION)

    data = JSONField(
        encoder=JSONEncoder,
        default=list
    )

    latest = models.ForeignKey('purple.Entry',
        related_name='device_latest',
        null=True,
        on_delete=models.SET_NULL
    )

    @cached_property
    def devices(self):
        self.data = api.get_devices(self.purple_id)
        self.label = self.data[0]['Label']
        self.position = Point(
            float(self.data[0]['Lon']),
            float(self.data[0]['Lat'])
        )
        self.location = self.data[0]['DEVICE_LOCATIONTYPE']
        return self.data

    @cached_property
    def channels(self):
        return api.get_channels(self.devices)

    def feed(self, **options):
        return api.get_correlated_feed(self.channels, **options)


class Entry(models.Model):
    id = SmallUUIDField(
        default=uuid_default(),
        primary_key=True,
        db_index=True,
        editable=False,
        verbose_name='ID'
    )
    device = models.ForeignKey('purple.PurpleAir',
        related_name='entries',
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField()
    position = models.PointField(null=True)
    location = models.CharField(max_length=10, choices=PurpleAir.LOCATION)

    data = JSONField(
        encoder=JSONEncoder,
        default=list
    )

    celcius = models.DecimalField(max_digits=4, decimal_places=1, null=True)
    fahrenheit = models.DecimalField(max_digits=4, decimal_places=1, null=True)
    humidity = models.DecimalField(max_digits=4, decimal_places=1, null=True)
    pressure = models.DecimalField(max_digits=6, decimal_places=2, null=True)

    pm2_a = JSONField(null=True, encoder=JSONEncoder, validators=[
        JSONSchemaValidator(PM2_SCHEMA)
    ])
    pm2_b = JSONField(null=True, encoder=JSONEncoder, validators=[
        JSONSchemaValidator(PM2_SCHEMA)
    ])

    def save(self, *args, **kwargs):
        # Temperature adjustments
        if self.fahrenheit is None and self.celcius is not None:
            self.fahrenheit = (Decimal(self.celcius) * (Decimal(9) / Decimal(5))) + 32
        if self.celcius is None and self.fahrenheit is not None:
            self.celcius = (Decimal(self.fahrenheit) - 32) * (Decimal(5) / Decimal(9))

        return super().save(*args, **kwargs)

