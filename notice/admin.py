from django.contrib import admin

from .models import Listing, Notice

admin.site.register(Listing)
admin.site.register(Notice)