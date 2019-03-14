from django.db import models
from django.utils import timezone
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.utils.translation import ugettext_lazy as _

from profiles.models import *

class Base(models.Model):
	name = models.CharField(max_length = 50)
	description = models.TextField(blank = True)
	creator = models.ForeignKey('auth.User', on_delete = models.PROTECT)
	created = models.DateTimeField(default = timezone.now)

	class Meta:
		abstract = True

	def __str__(self):
		return self.name

class Listing(Base):

	def get_absolute_url(self):
		return reverse('notice:notice-listings')

class Notice(Base):
	"""
		An Item can be seen as Tasks under each Listing
	"""    
	V_URGENT = 'Urgent'
	MODERATE = 'Moderate'
	NORMAL = 'Normal'
	CHOICES = (
		(V_URGENT, _('Urgent')),
		(MODERATE, _('Moderate')),
		(NORMAL, _('Normal')),
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

	priority = models.CharField(
		_('priority'),
		max_length=15,
		choices=CHOICES,
		default=NORMAL
	)

	description = RichTextField()
	Listing = models.ForeignKey(Listing, related_name ="notice_listings", on_delete = models.PROTECT)
	expiry = models.DateTimeField(default = timezone.now)
		
	def get_absolute_url(self):
		return reverse('notice:notice-listings')
	
	class Meta:
		ordering = ['-created']
