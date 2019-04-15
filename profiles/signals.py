from django.db.models.signals import post_save, pre_save, m2m_changed
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

from profiles.models import UserProfile

def auto_create_profile(instance, sender, **kwargs):
    # Once a User is created, let the profile be ato created too

    if kwargs['created'] == True:
        user = instance
        UserProfile.objects.get_or_create(user=user)

post_save.connect(auto_create_profile, sender=User)

def add_user_to_group(instance, sender, **kwargs):
    user = User.objects.get(username=instance.user.username) 
    
    for group in user.groups.all():
        user.groups.remove(group)   
        
    for group in instance.group.all():
        user.groups.add(group)
        
m2m_changed.connect(add_user_to_group, sender=UserProfile.group.through)
