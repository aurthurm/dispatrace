from django.contrib import admin
from django.urls import path, include, re_path

from .views import *

app_name="fuel"
urlpatterns = [
    path('', FuelListing.as_view(), name='requests-listings'),
    path('archives', FuelArchivedListing.as_view(), name='fuel-archives'),
    path('archives/search', FuelSearch.as_view(), name='fuel-search'),
    path('request/<int:fuel_id>/detail', FuelDetail.as_view(), name='fuel-detail'),
    path('request/<int:fuel_id>/archive', fuel_archive, name='fuel-archive'),
    path('request-new', FuelRequest.as_view(), name='request-fuel'),
    path('request/<int:fuel_id>/edit', FuelUpdate.as_view(), name='fuel-edit'),   
    path('reports', reports_fuel, name='reports-fuel'),
    path('request/<int:fuel_id>/close', close_request, name='close-request'),
    path('request/<int:fuel_id>/detail/add-comment', fuel_comment, name='fuel-add-comment'),
    path('request/<int:fuel_id>/reassign', FuelReassign.as_view(), name='fuel-reassign'),
]