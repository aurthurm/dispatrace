from django import template
from memoir.permissions import level_higher_than_last_commenter
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group') 
def has_group(user, group_name):
    group =  Group.objects.get(name=group_name) 
    return group in user.groups.all()

