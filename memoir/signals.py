from django.db.models.signals import post_save
from django.shortcuts import render, get_object_or_404

from memoir.models import Memo, MemoComment, Archive
from memoir.permissions import *

def memo_editing(instance, sender, **kwargs):
    memo = instance.memo
    comment_count = memo.memocomment_comment.all().count()

    # Once a memo has a single comment, the sender should
    # not be able to comment ever unless required.
    if not comment_count == 0:
	    ban_permission(memo.sender, memo, permission='change_memo')
    else:
	    allow_permission(memo.sender, memo, permission='change_memo')

post_save.connect(memo_editing, sender=MemoComment)

def allow_editing(instance, sender, **kwargs):
    memo = instance
    if kwargs['created'] == True:
	    allow_permission(memo.sender, memo, permission='change_memo')
        
post_save.connect(allow_editing, sender=Memo)

def archive_memo(instance, *args, **kwargs):
    memo = Memo.objects.get(pk=instance.memo.pk)
    if kwargs['created']:
        memo.archived = True
        memo.save()

post_save.connect(archive_memo, sender=Archive)
    
