from django.contrib import admin
from memoir.models import (
        Memo,
        Attachment,
        MemoComment,
        Archive,
    )

class AttachmentInline(admin.TabularInline):
    model = Attachment

class MemoCommentInline(admin.TabularInline):
    model = MemoComment

class MemoAdmin(admin.ModelAdmin):

    inlines = [
        AttachmentInline,
        MemoCommentInline
    ]
    list_display = [
        'reference_number',
        'sender',
        'to',
        'subject',
        'created',
        'is_open',
        'mem_type',
        'sent'
    ]

admin.site.register(Memo, MemoAdmin)
admin.site.register(Archive)
