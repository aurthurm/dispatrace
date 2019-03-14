from django.urls import path, re_path
from .views import *

app_name = 'notice'
urlpatterns = [
    path('listings', ListingsList.as_view(), name='notice-listings'),
    path('listing/add/', ListingCreate.as_view(), name='listing-add'),
    path('listing/<int:listing_id>/delete', ListingDelete.as_view(), name='listing-delete'),
    path('listing/<int:listing_id>/edit', EditListing.as_view(), name='listing-edit'),
    path('listing/<int:listing_id>/item/add', NoticeCreate.as_view(), name='item-add'),
    path('listing/<int:listing_id>/item/<int:item_id>/update', NoticeUpdate.as_view(), name='item-update'),
    path('listing/<int:listing_id>/item/<int:item_id>/delete', NoticeDelete.as_view(), name='item-delete'),
    path('ajax/load-offices/', load_offices, name='ajax_load_offices'),
    path('ajax/load-departments/', load_departments, name='ajax_load_departments'),
]
