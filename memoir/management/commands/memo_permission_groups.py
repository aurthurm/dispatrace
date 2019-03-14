from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm, remove_perm
from guardian.shortcuts import get_perms
from memoir.models import Memo

# Code to add permission to group ???


# Now what - Say I want to add 'Can add project' permission to new_group?



class Command(BaseCommand):
    def get_perms_group(self, name=""):
        try:
            return Group.objects.get(name=name)
        except Group.DoesNotExist:
            group = Group.objects.create(name=name)
            group.save()
            return group

    def add_group_perms(self, group, permission='memoir.add_comment'):
        assign_perm(permission, group)

    def remove_group_perms(self, group, permission='memoir.add_comment'):
        remove_perm(permission, group) 

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating and Updating Permissions Group for Memos'))
        hr = self.get_perms_group(name='Human Resources')
        admin = self.get_perms_group(name='Administrator')
        admin = self.get_perms_group(name='Notice Creators')
        admin = self.get_perms_group(name='Auditors')
        self.stdout.write(self.style.SUCCESS('DONE'))