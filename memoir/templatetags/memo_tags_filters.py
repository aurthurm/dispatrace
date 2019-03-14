from django import template
from memoir.permissions import level_higher_than_last_commenter, has_comments, is_recipient, is_to, is_sender
from django.contrib.auth.models import Group

register = template.Library()

@register.simple_tag
def commented_class(*args, **kwargs):
	memo = kwargs['memo']
	recipient = kwargs['recipient']

	if memo.memocomment_comment.filter(commenter__exact=recipient).count() != 0 or recipient in memo.receptors.all():
		return "success"
	else:
		return "warning"

@register.filter
def sortbyuserlevel(memo):
    recipients = memo.recipients.all().order_by('user_profile__level__level')
    return recipients

@register.simple_tag
def can_view_last_comment(*args, **kwargs):
	memo = kwargs['memo']
	comment = kwargs['comment']
	user = kwargs['user']
	permit_viewing = True
	if memo.memocomment_comment.filter(commenter__exact=memo.to).count() != 0: # has to commented?
		if comment == memo.memocomment_comment.all().latest():		# is this comment latest
			if memo.memocomment_comment.all().latest().commenter == memo.to: # is to the commenter of this lastest comment
				if memo.is_open and not user == memo.to: # has the memo not been closed/finalised/approved/...
					permit_viewing = False
	return permit_viewing

@register.simple_tag
def can_close_after_commenting(*args, **kwargs):
	memo = kwargs['memo']
	return memo.memocomment_comment.filter(commenter__exact=memo.to).count() != 0

@register.simple_tag
def can_recept_memo(*args, **kwargs):
	memo = kwargs['memo']
	user = kwargs['user']
	allow = False
	if is_to(user, memo) or is_recipient(user, memo):
		if not user in memo.receptors.all():
			allow = True
	return allow

@register.simple_tag
def memo_can_be_sent(*args, **kwargs):	
	memo = kwargs['memo']
	allow = False
	if memo.to != None: # and memo.recipients.all().count() != 0:
		allow = True
	return allow

@register.simple_tag
def memo_urgency(*args, **kwargs):	
    memo = kwargs['memo']
    priority = ''
    if memo.mem_priority == 'Very Urgent':
        priority = 'p-urgent'
    if memo.mem_priority == 'Moderate':
        priority = 'p-moderate'
    if memo.mem_priority == 'Normal':
        priority = 'p-normal'
    return priority

@register.simple_tag
def reassign(*args, **kwargs):
	memo = kwargs['memo']
	user = kwargs['user']
	allow = False
	# if has_comments(memo):
	# 	return level_higher_than_last_commenter(user, memo) and memo.is_open
	# else:
	# 	return False 
	if memo.is_open:
		if is_to(user, memo) or is_recipient(user, memo) or is_sender(user, memo):
			allow = True
	return allow

@register.filter(name='has_group') 
def has_group(user, group_name):
    group =  Group.objects.get(name=group_name) 
    return group in user.groups.all()

