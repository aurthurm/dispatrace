from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify
import os

from mptt.models import MPTTModel, TreeForeignKey
from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords
import reversion

from memoir.settings import ATTACHMENT_UPLOAD_TO

class Core(models.Model):
    """
		Fields to determine our recipients and base details
	"""
    recipients = models.ManyToManyField(
        User,
        related_name="%(class)s_recipients"
    )
    to = models.ForeignKey(
        User,
        related_name="%(class)s_to",
        null=True,
        blank=True,
        default='',
        on_delete=models.PROTECT
    )
    sender = models.ForeignKey(
        User,
        related_name="%(class)s_from",
        on_delete=models.PROTECT
    )
    is_open = models.BooleanField( # is open for commenting ?
        _('is open'),
        default=True
    )
    archived = models.BooleanField(
        _('archived'),
        default=False
    )
    sent = models.BooleanField(
        _('sent'),
        default=False
    )
    created = models.DateTimeField(
        _('date created'), 
        default=timezone.now
    )
    date_sent = models.DateTimeField(
        _('date sent'), 
        db_index=True, 
        null=True,
        blank=True
    )
    reference_number = models.CharField(
        _('reference number'),
        max_length=23,
        db_index=True, 
        unique=True
    )

    class Meta:
        abstract=True
        get_latest_by = 'created'

class Content(models.Model):
    """
        Field to write content for the Memo: Reason and body message
    """
    subject = models.CharField(
        _('subject'),
        max_length=255
    )
    slug = models.SlugField(
        _('slug'), 
        max_length=255, 
        blank=True
    )
    message = RichTextField(
        _('memo body'),
        config_name='awesome_ckeditor'
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.subject)
        super(Content, self).save(*args, **kwargs)

    def __str__(self):
        return self.subject

    class Meta:
        abstract=True

class Type(models.Model):
    """
        Determines whether the memo being created is public or private.
        Public Memos are seen by everyone. 
        Private Memos are seen only by the sender and selected recipinet(s)
    """
    PUBLIC = 'PUB'
    PRIVATE = 'PVT'
    CHOICES = (
        (PUBLIC, _('Public')),
        (PRIVATE, _('Private')),
    )
    mem_type = models.CharField(
        _('memo type'),
        max_length=10,
        choices=CHOICES,
        default=PUBLIC
    )

    class Meta:
        abstract=True

class Priority(models.Model):
    """
        Determines whether the memo being created is public or private.
        Public Memos are seen by everyone. 
        Private Memos are seen only by the sender and selected recipinet(s)
    """
    V_URGENT = 'Very Urgent'
    MODERATE = 'Moderate'
    NORMAL = 'Normal'
    CHOICES = (
        (V_URGENT, _('Very Urgent')),
        (MODERATE, _('Moderate')),
        (NORMAL, _('Normal')),
    )
    mem_priority = models.CharField(
        _('memo priority'),
        max_length=15,
        choices=CHOICES,
        default=NORMAL
    )

    class Meta:
        abstract=True

@reversion.register()
class Memo(
        Core, 
        Priority,
        Type,
        Content,
    ):
    """
        Memo Model
    """
    def get_absolute_url(self):
        return reverse(
            'memoir:memo-detail', 
            kwargs={'memo_id': self.pk, 'memo_slug': self.slug}
        )

    commenting_required = models.BooleanField(
        _('commenting required'),
        default=True
    )
    receptors = models.ManyToManyField( # for memos that do not  need commenting. A user who acknwledged reception will be added here
        User,
        related_name="%(class)s_receptors",
        blank=True
    )

    class Meta:
        ordering = ['-created']
        verbose_name = _('memo')
        verbose_name_plural = _('memos')
        permissions = (
            ('add_comment', 'Comment Memo'), 
        )

    # history = HistoricalRecords()

class AbstractComment(MPTTModel):
    """
        Commenting Abstract model
    """
    parent = TreeForeignKey(
        'self', 
        related_name='%(class)s_sub_comment', 
        db_index=True, 
        null=True, 
        blank=True, 
        on_delete=models.PROTECT
    )
    comment = RichTextField()
    commenter = models.ForeignKey(
        User, 
        on_delete=models.PROTECT
    )
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract=True

@reversion.register()
class MemoComment(AbstractComment):
    """
        Commenting model for Fuel
    """
    memo = models.ForeignKey(
        Memo, 
        related_name='%(class)s_comment', 
        on_delete=models.PROTECT
    )

    class Meta:
        get_latest_by = ['timestamp']
        verbose_name = _('memo comment')
        verbose_name_plural = _('memo comments')

    def __str__(self):
        return self.comment

    def get_absolute_url(self):
        return reverse(
            'memoir:memo-detail', 
            kwargs={'memo_id': self.memo.pk, 'memo_slug': self.memo.slug}
        )

def file_upload_to_dispatcher(entry, filename):
    return entry.file_upload_to(filename)

class Attachment(models.Model):
    """
        Add Attachments to memos
    """
    memo = models.ForeignKey(
        Memo, 
        on_delete=models.CASCADE
    )

    def file_upload_to(self, filename):
        now = timezone.now()
        filename, extension = os.path.splitext(filename)

        return os.path.join(
                ATTACHMENT_UPLOAD_TO,
                now.strftime('%Y'),
                now.strftime('%m'),
                now.strftime('%d'),
                '%s%s' % (slugify(filename), extension)
            )

    file_name = models.CharField(
        _('file name'),
        max_length=255
    )

    file = models.FileField(
        _('file'), blank=True,
        upload_to=file_upload_to_dispatcher,
        help_text=_('Attach File'))

    def __str__(self):
        return "Attached to: " + str(self.memo)

    # history = HistoricalRecords()

@reversion.register()
class Archive(models.Model):
    """
        Close Memo / Archive
    """
    memo = models.ForeignKey(
        Memo,
        on_delete=models.PROTECT
    )
    archived = models.BooleanField(
        _('archived'),
        default=False
    )
    archiver = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )
    date_archived = models.DateTimeField(
        _('date archived'), 
        db_index=True, 
        default=timezone.now
    )

    def __str__(self):
        return str(self.memo.subject)

    class Meta:
        verbose_name = _('archive')
        verbose_name_plural = _('archives')

    # history = HistoricalRecords()

class MinMaxFloat(models.FloatField):
    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        super(MinMaxFloat, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(MinMaxFloat, self).formfield(**defaults)  