from django.contrib import admin
from django.urls import path, include, re_path

from .views import *

app_name="profiles"
urlpatterns = [
    path('users-list', UserList.as_view(), name='users-list'),
    path('users-list/seach', users_search, name='users-ajax-search'),
    path('profile-<int:profile_id>/detail', ProfileDetail.as_view(), name='profile-detail'),
    path('profile-<int:profile_id>/edit', ProfileEdit.as_view(), name='profile-edit'),
    path('configurations/list/countries', CoutriesView.as_view(), name='config-list-countries'),
    path('configurations/list/cities', CitiesView.as_view(), name='config-list-cities'),
    path('configurations/list/levels', LevelsView.as_view(), name='config-list-levels'),
    path('configurations/list/departments', DepartmentsView.as_view(), name='config-list-departments'),
    path('configurations/list/offices', OfficesView.as_view(), name='config-list-offices'),
    path('country/add', CountryAdd.as_view(), name='country-add'),
    path('country/<int:country_id>/edit', CountryEdit.as_view(), name='country-edit'),
    path('city/add', CityAdd.as_view(), name='city-add'),
    path('city/<int:city_id>/edit', CityEdit.as_view(), name='city-edit'),
    path('office/add', OfficeAdd.as_view(), name='office-add'),
    path('office/<int:office_id>/edit', OfficeEdit.as_view(), name='office-edit'),
    path('department/add', DepartmentAdd.as_view(), name='department-add'),
    path('department/<int:department_id>/edit', DepartmentEdit.as_view(), name='department-edit'),
    path('level/add', LevelAdd.as_view(), name='level-add'),
    path('level/<int:level_id>/edit', LevelEdit.as_view(), name='level-edit'),
    path('populate', od_populator, name='populate'),
]