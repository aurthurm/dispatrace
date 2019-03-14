from guardian.shortcuts import assign_perm, remove_perm
from guardian.shortcuts import get_perms # example: 'change_memo' in get_perms(user, memo)
from django.contrib.auth.models import Group
from django.db.models import Q

# Possible Group Names: Memo Editors, Memo Commenters, Memo Viewers
def get_perms_group(name=""):
    try:
        return Group.objects.get(name=name)
    except Group.DoesNotExist:
        group = Group.objects.create(name=name)
        group.save()
        return group

# get_perms_group('Memo Editors')
# get_perms_group('Memo Commenters')
# get_perms_group('Memo Viewers')

# def add_group_perms(group, permission='memoir.add_comment'):
#     assign_perm(permission, group)

# def remove_group_perms(group, permission='memoir.add_comment'):
#     remove_perm(permission, group)

def remove_from_perms_group(user, group=''):
    user.groups.remove(group)

def add_to_perms_group(user, group=''):
    user.groups.add(group)

def ban_permission(user, memo, permission=''):
    if user.has_perm(permission, memo):
        remove_perm(permission, user, memo)
    else:
        pass

def allow_permission(user, memo, permission=''):
    if not user.has_perm(permission, memo):
        assign_perm(permission, user, memo)
    else:
        pass

def has_comments(memo):
    return memo.memocomment_comment.all().count() != 0

def is_recipient(user, memo):
    return user in memo.recipients.all()

def is_to(user, memo):
    return user == memo.to

def is_sender(user, memo):
    return user == memo.sender

def level_higher_than_sender(user, memo):
    return user.user_profile.level.level > memo.sender.user_profile.level.level

def level_higher_than_last_commenter(user, memo):
    return user.user_profile.level.level > memo.memocomment_comment.all().latest().commenter.user_profile.level.level

def is_next_commenter(user, memo):
    ordered_recipients = memo.recipients.all().order_by('user_profile__level__level')
    last_commenter_level = memo.memocomment_comment.all().latest().commenter.user_profile.level.level
    not_commented = ordered_recipients.filter(Q(user_profile__level__level__gt=last_commenter_level))
    next_commenter = not_commented.first()
    return user == next_commenter

def all_have_commented(memo):
    if has_comments(memo):
        ordered_recipients = memo.recipients.all().order_by('user_profile__level__level')
        last_commenter = ordered_recipients.last()
        return memo.memocomment_comment.all().latest().commenter == last_commenter
    else:
        return False

def get_next_commenter(user, memo):
    ordered_recipients = memo.recipients.all().order_by('user_profile__level__level')
    if has_comments(memo):
        if all_have_commented(memo) == False:
            last_commenter_level = memo.memocomment_comment.all().latest().commenter.user_profile.level.level
            not_commented = ordered_recipients.filter(Q(user_profile__level__level__gt=last_commenter_level))
            next_commenter = not_commented.first()
            return next_commenter
    else:
        return ordered_recipients.first()

def is_recent_commenter(user, memo):
    return user == memo.memocomment_comment.all().latest().commenter

def has_commented(user, memo):
    return memo.memocomment_comment.filter(commenter__exact=user).count() != 0

def has_recipients(memo):
    return memo.recipients.all().count() != 0

def can_comment(user, memo):
    if is_recipient(user, memo) and memo.is_open:
        if has_comments(memo):
            if is_next_commenter(user, memo): # or is_recent_commenter(user, memo):
                allow_permission(user, memo, permission='add_comment')
                return user.has_perm('add_comment', memo)
            else:
                ban_permission(user, memo, permission='add_comment')
                return user.has_perm('add_comment', memo)
        else:
            if level_higher_than_sender(user, memo) and user == memo.recipients.all().order_by('user_profile__level__level').first():
                allow_permission(user, memo, permission='add_comment')
                return user.has_perm('add_comment', memo)
            else:
                ban_permission(user, memo, permission='add_comment')
                return user.has_perm('add_comment', memo)
    elif is_to(user, memo) and memo.is_open:   
        if has_recipients(memo):
            if all_have_commented(memo):
                allow_permission(user, memo, permission='add_comment')
                return user.has_perm('add_comment', memo)   
            else:
                ban_permission(user, memo, permission='add_comment')
                return user.has_perm('add_comment', memo)
        else:
            allow_permission(user, memo, permission='add_comment')
            return user.has_perm('add_comment', memo)           
    else:
        ban_permission(user, memo, permission='add_comment')
        # return user.has_perm('add_comment', memo) 
        return False

def can_close(user, memo):
    if user == memo.to:
        return True
    else:
        return False

def can_view_last_comment(memo):
    if memo.memocomment_comment.filter(commenter__exact=memo.to) and not memo.is_open:
        return True