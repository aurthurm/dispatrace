from django import template
from memoir.permissions import level_higher_than_last_commenter
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group') 
def has_group(user, group_name):
    group =  Group.objects.get(name=group_name) 
    return group in user.groups.all()

@register.simple_tag
def as_list(*args, **kwargs):
	no_list = kwargs['no_list']

	_list = []
	for k in no_list:
		_list.append(k.name)

	sentence = ""
	for k in _list:
		sentence += k
		sentence += ", "
	return sentence
