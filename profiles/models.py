from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.contrib.auth.models import User, Group

class Country(models.Model):
    name = models.CharField(
        _('country'),
        max_length=255,
        default='',
        unique=True
    )

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')

    def __str__(self):
        return str(self.name)

class Department(models.Model):
    """
        A branch or office have different departments and sections t operate from
    """
    name = models.CharField(
        _('name'),
        max_length=255,
        default=''
    )
    code = models.CharField(
        _('code'),
        max_length=3,
        default=''
    )
    # country = models.ForeignKey(
    #     Country,
    #     on_delete=models.PROTECT,
    #     default=''
    # )
    # city = models.ForeignKey(
    #     City,
    #     on_delete=models.PROTECT,
    #     default=''
    # )
    # office = models.ForeignKey(
    #     Office,
    #     on_delete=models.PROTECT,
    #     default=''
    # )

    class Meta:
        verbose_name = _('department')
        verbose_name_plural = _('departments')

    def __str__(self):
        return str(self.name)

class Office(models.Model):
    """
        The name of your office in that city of yours.
        look at offices as branches in a city.
    """
    name = models.CharField(
        _('name'),
        max_length=255,
        default=''
    )
    code = models.CharField(
        _('code'),
        max_length=3,
        default=''
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        default=''
    )
    # city = models.ForeignKey(
    #     City,
    #     on_delete=models.PROTECT,
    #     default=''
    # )
    departments = models.ManyToManyField(
            Department, 
            related_name='office_departments',
            blank=True,
        )

    class Meta:
        # unique_together = ('name', 'city')
        verbose_name = _('office')
        verbose_name_plural = _('offices')

    def __str__(self):
        return str(self.name)


class City(models.Model):
    name = models.CharField(
        _('city'),
        max_length=255,
        default=''
    )
    abbreviation = models.CharField(
        _('abbreviation'),
        max_length=3,
        default=''
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        default=''
    )

    offices = models.ManyToManyField(
            Office, 
            related_name='city_offices',
            blank=True,
        )

    class Meta:
        verbose_name = _('city')
        verbose_name_plural = _('cities')

    def __str__(self):
        return str(self.name)


class Level(models.Model):
    """
        Registration of the different User Levels.
        This will help with Permissions management accross organisational Levels.
    """
    name = models.CharField(
            _('name'), 
            max_length=100 
        )
    level = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.level) + ' : ' + str(self.name)

    class Meta:
        unique_together = ('name', 'level')
        verbose_name = _('level')
        verbose_name_plural = _('levels')

class UserProfile(models.Model):
    """
        Additional information about the user is captured in their profile
    """
    user = models.OneToOneField(
            User, 
            related_name='user_profile', 
            on_delete=models.PROTECT
        )
    force_password_change = models.BooleanField(default=True)
    title = models.CharField(
            max_length=255, 
            blank=True, 
            default=''
        )
    phone = models.CharField(
            max_length=20, 
            blank=True, 
            default=''
        )
    cell = models.CharField(
            max_length=20, 
            blank=True, 
            default=''
        )
    active = models.BooleanField(default=True)
    level = models.ForeignKey(
            Level, 
            # related_name='user_level',
            on_delete=models.PROTECT,
            null=True,
            blank=True,
            default=''
        )
    city = models.ForeignKey(
        City,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        default=''
    )
    office = models.ForeignKey(
        Office,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        default=''
    )
    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        default=''
    )
    group = models.ManyToManyField(
        Group, 
        related_name='user_group',
        blank=True,
    )

    def get_absolute_url(self):
        return reverse(
                'profiles:profile-detail',
                kwargs={'profile_id': self.pk}
            )

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return '@' + str(self.user.username)
