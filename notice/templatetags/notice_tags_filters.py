from django import template
from memoir.permissions import level_higher_than_last_commenter, has_comments, is_recipient, is_to, is_sender
from django.contrib.auth.models import Group

from django.utils import timezone
from datetime import timedelta

from django.db.models import Q

register = template.Library()

@register.simple_tag
def notice_view(*args, **kwargs):	
	notice = kwargs['notice']	
	user = kwargs['user']
	allow = False
	user_city = user.user_profile.city
	user_department = user.user_profile.department
	user_office = user.user_profile.office

	if not notice.city == None:
		if user_city == notice.city:
			if not notice.office == None:
				if user_office == notice.office:
					if not notice.department == None:
						if user_department == notice.department:
							allow = True
					else:
						allow = True
			else:
				allow = True
	else:                                                                          # National View
		allow = True

	return allow

@register.simple_tag
def notice_urgency(*args, **kwargs):	
    notice = kwargs['notice']
    priority = ''
    if notice.priority == 'Urgent':
        priority = 'notice p-urgent'
    if notice.priority == 'Moderate':
        priority = 'notice p-moderate'
    if notice.priority == 'Normal':
        priority = 'notice p-normal'
    return priority

@register.simple_tag
def notices_filter(*args, **kwargs):
	notices = kwargs['notices']
	expired = kwargs['expired']

	yesterday = timezone.now() - timedelta(days=1)

	if expired:
		return notices.notice_listings.filter(Q(expiry__lte=yesterday))[:10]
	else:
		return notices.notice_listings.filter(Q(expiry__gte=yesterday))