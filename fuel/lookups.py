from ajax_select import register, LookupChannel
from django.contrib.auth.models import User
from django.db.models import Q

@register('users')
class UsersLookup(LookupChannel):
    model = User

    def check_auth(self, request):
        if request.user.user_profile:
            return True

    def get_query(self, q, request):
        return self.model.objects.filter(
            Q(username__icontains=q) | 
            Q(first_name__icontains=q)  | 
            Q(last_name__icontains=q)
        ).distinct()

    def get_query(self, q, request):
        return self.model.objects.filter(username__icontains=q).order_by('username')

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % str(item.first_name) + " " + str(item.last_name) 
    
    def format_match(self, item):
        return u"<span class='tag'>%s</span>" % str(item.username) + ": " + str(item.first_name) + " " + str(item.last_name) + ": " + str(item.user_profile.level.level)