from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.template.defaultfilters import slugify

import reversion

from memoir.models import AbstractComment

class MinMaxFloat(models.FloatField):
    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        super(MinMaxFloat, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(MinMaxFloat, self).formfield(**defaults)    

@reversion.register()
class Fuel(models.Model):
    """
        Fuel Memo Requests
    """
    HIGH = 'High'
    MODERATE = 'Moderate'
    NORMAL = 'Normal'
    PRORITIES = (
        (HIGH, _('High')),
        (MODERATE, _('Moderate')),
        (NORMAL, _('Normal')),
    )
    PETROL = 'Petrol'
    DIESEL = 'Diesel'
    FUEL_TYPES = (
        (PETROL, _('Petrol')),
        (DIESEL, _('Diesel')),
    )

    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=PRORITIES,
        default=NORMAL
    )
    fuel_type = models.CharField(
        _('fuel type'),
        max_length=10,
        choices=FUEL_TYPES,
        default=PETROL
    )
    date_requested = models.DateTimeField(
        _('date requested'), 
        db_index=True, 
        default=timezone.now
    )
    date_required = models.DateTimeField(
        _('date of required'), 
        db_index=True, 
        default=timezone.now
    )
    city = models.ForeignKey(
        'profiles.City',
        related_name='fuel_requester_city',
        on_delete=models.PROTECT,
        default=''
    )
    office = models.ForeignKey(
        'profiles.Office',
        on_delete=models.PROTECT,
        default=''
    )
    department = models.ForeignKey(
        'profiles.Department',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        default=''
    )
    requester = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )
    amount = MinMaxFloat(
        min_value=0.0,
        max_value=1000.0
        )
    reason = models.TextField(
        _('reason'),
        max_length=255,
        default=''
    )
    registration = models.CharField(
        _('vehicle reg number'),
        max_length=255,
        null=True,
        blank=True,
        default='',
    )
    # origin = models.ForeignKey(
    #     'profiles.City',
    #     related_name='fuel_origin',
    #     on_delete=models.PROTECT,
    #     default=''
    # )
    origin = models.CharField(
        _('origin'),
        max_length=255
    )
    # destination = models.ForeignKey(
    #     'profiles.City',
    #     related_name='fuel_destination',
    #     on_delete=models.PROTECT,
    #     default=''
    # )
    destination = models.CharField(
        _('destination'),
        max_length=255
    )
    reference_number = models.CharField(
        _('reference number'),
        max_length=50,
        default=''
    )
    approver = models.ForeignKey(
        User,
        related_name='manger',
        blank=True,
        null=True,
        on_delete=models.PROTECT
    )
    assessor = models.ForeignKey(
        User,
        related_name='supervisor',
        blank=True,
        null=True,
        on_delete=models.PROTECT
    )
    is_open = models.BooleanField(
        _('is open'),
        default = True
    )
    accepted = models.BooleanField(
        _('accepted'),
        default = False
    )
    plus_vehicle = models.BooleanField(
        _('plus vehicle'),
        default = False
    )
    archived = models.BooleanField(
        _('archived'),
        default = False
    )

    def __str__(self):
        return self.fuel_type

    def get_absolute_url(self):
        return reverse(
            'fuel:fuel-detail', 
            kwargs={'fuel_id': self.pk}
        )

    class Meta:
        verbose_name = _('fuel')
        verbose_name_plural = _('fuel')
        ordering = ('-date_requested',)
    
class Comment(AbstractComment):
    """
        Commenting model for Fuel
    """
    fuel = models.ForeignKey(
        Fuel, 
        related_name='%(class)s_fuel', 
        on_delete=models.PROTECT
    )
    comment = models.TextField(
        _('comment'),
        max_length=255,
        default=''
   )
   user = models.ForeignKey(
        User,
        related_name='user',
        on_delete=models.PROTECT
   )

    class Meta:
        get_latest_by = ['timestamp']
        verbose_name = _('fuel comment')
        verbose_name_plural = _('fuel comments')

    def __str__(self):
        return self.comment

    def get_absolute_url(self):
        return reverse(
            'fuel:fuel-detail', 
            kwargs={'fuel_id': self.fuel.pk, 'fuel_slug': self.fuel.slug}
        )
