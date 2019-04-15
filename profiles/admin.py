from django.contrib import admin

from profiles.models import *

class ProfileAdmin(admin.ModelAdmin):
	list_display = [
		'user',
		'title',
		'city',
		'office',
		'department',
		'level',
	]
	search_fields = ('user__username',)

admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(Level)
admin.site.register(Department)
admin.site.register(Office)
admin.site.register(City)
admin.site.register(Country)