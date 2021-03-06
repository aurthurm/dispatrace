from django import template
from memoir.permissions import level_higher_than_last_commenter
from django.contrib.auth.models import Group

register = template.Library()

@register.simple_tag
def fuel_urgency(*args, **kwargs):	
    fuel = kwargs['fuel']
    priority = ''
    if fuel.priority == 'High':
        priority = 'p-urgent'
    if fuel.priority == 'Moderate':
        priority = 'p-moderate'
    if fuel.priority == 'Normal':
        priority = 'p-normal'
    return priority

@register.simple_tag
def can_assign(*args, **kwargs):
    fuel = kwargs['fuel']
    user = kwargs['user']
    reassign = False
    if fuel.is_open:
        if user == fuel.requester or user == fuel.assessor or user == fuel.approver:
            reassign = True
        else:
            reassign = False
    else:
        reassign = False
    return reassign
 
@register.filter(name='has_group') 
def has_group(user, group_name):
    group =  Group.objects.get(name=group_name) 
    return group in user.groups.all()

@register.simple_tag
def fuel_status(*args, **kwargs):
    fuel = kwargs['fuel']
    if fuel.is_open:
        status = "<span class='badge badge-info'>OPEN</span>"
    else:
        if fuel.accepted:
            status = "<span class='badge badge-success'>APPROVED</span>"
        else:
            status = "<span class='badge badge-danger'>DECLINED</span>"
    return status

@register.simple_tag
def can_comment(*args, **kwargs):
    fuel = kwargs['fuel']
    user = kwargs['user']
    if fuel.is_open == True:
        if user == fuel.assessor or user == fuel.approver: # only these 2 are allowed to comment
            # if there are no comments then only allow the assessor to comment
            if fuel.comment_fuel.all().count() is 0 and user == fuel.assessor:
                return True
            elif fuel.comment_fuel.all().count() is 1 and user == fuel.approver:
                return True
            elif fuel.comment_fuel.all().count() is 0 and user == fuel.approver and fuel.assessor == None:
                return True
            else: 
                return False
        else:
            return False
    else:
        return False

@register.simple_tag
def can_edit_comment(*args, **kwargs):
    comment = kwargs['comment']
    fuel = kwargs['fuel']
    user = kwargs['user']
    if fuel.is_open == True:
        if user == fuel.assessor or user == fuel.approver: 
            # is user == last commenter then edit.
            if fuel.comment_fuel.all().count() != 0:
                last_commenter = fuel.comment_fuel.all().latest().commenter
                if user == last_commenter:
                    if last_commenter == comment.commenter:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False

@register.simple_tag
def can_approve(*args, **kwargs):
    fuel = kwargs['fuel']
    user = kwargs['user']
    if user == fuel.approver and fuel.comment_fuel.all().count() is 2:
        return True
    elif fuel.comment_fuel.all().count() is 1 and user == fuel.approver and fuel.assessor == None:
        return True
    else:
        return False