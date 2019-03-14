from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import json
from django.core import serializers

from profiles.models import *
from .forms import UserProfileForm, ProfileForm, ProfileUpdateForm

def paginate(request, unaginated):
	page = request.GET.get('page', 1)

	paginator = Paginator(unaginated, 10)
	try:
		the_list = paginator.page(page)
	except PageNotAnInteger:
		the_list = paginator.page(1)
	except EmptyPage:
		the_list = paginator.page(paginator.num_pages)
	return the_list


class UserList(LoginRequiredMixin, ListView):
	queryset = User.objects.exclude(username__exact='AnonymousUser').order_by('username')	
	model = User
	paginate_by = 15

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context

def users_search(request):
    
    if request.method == 'GET':
        data = []
        q = request.GET.get('qry')
        queryset = UserProfile.objects.all()
        if q:
            results = queryset.filter(
                Q(user__username__icontains=q)|
                Q(user__first_name__icontains=q)|
                Q(user__last_name__icontains=q)                
            )
        else:
            results = queryset
            
        for result in results:
            if len(result.group.all()) != 0:
                groups = []
                for group in result.group.all():
                    groups.append({
                        'name': group.name
                    })
            else:
                groups = {}
            data.append({
                'profile_id': result.pk,
                'username': result.user.username,
                'first_name': result.user.first_name,
                'last_name': result.user.last_name,
                'title': result.title,
                'phone':  result.phone,
                'cell': result.cell,
                'status': result.active,
                'level': result.level.level,
                'city': result.city.name,
                'office': result.office.name,
                'department': result.department.name,
                'groups': groups
            })
        return JsonResponse(data, safe=False)
    
class ProfileDetail(LoginRequiredMixin, DetailView):
	model = UserProfile	
	pk_url_kwarg = 'profile_id'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context

class ProfileEdit(LoginRequiredMixin, UpdateView):
	model = UserProfile
	pk_url_kwarg = 'profile_id'
	template_name = 'profiles/profile_form.html'
	form_class = ProfileUpdateForm

	def get_success_url(self):
		profile_id = self.kwargs['profile_id']
		return reverse('profiles:profile-detail', kwargs={'profile_id':profile_id})

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Edit Profile"
		context['user_edit'] = UserProfile.objects.get(pk=self.kwargs['profile_id'])
		return context

	def form_valid(self, form):

		_city = str(self.request.POST.get('city')).strip()
		_office = str(self.request.POST.get('office')).strip()
		_department = str(self.request.POST.get('department')).strip()

		if len(_city) is not 0:
			form.instance.city = get_object_or_404(City, pk=int(_city))
			if len(_office) is not 0:
				form.instance.office = get_object_or_404(Office, pk=int(_office))
				if len(_department) is not 0:
					form.instance.department = get_object_or_404(Department, pk=int(_department))
				else:
					form.instance.department = None
			else:
				form.instance.office = None
				form.instance.department = None
		else:
			form.instance.city = None
			form.instance.office = None
			form.instance.department = None

		return super().form_valid(form)

class CoutriesView(View):
	template_name = 'configure/config_list.html'
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {'countries': paginate(request, Country.objects.all()), 'country_active': True})

class CitiesView(View):
	template_name = 'configure/config_list.html'
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {'cities': paginate(request, City.objects.all()), 'cities_active': True})

class OfficesView(View):
	template_name = 'configure/config_list.html'
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {'offices': paginate(request, Office.objects.all()), 'offices_active': True})

class LevelsView(View):
	template_name = 'configure/config_list.html'
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {'levels': paginate(request, Level.objects.all()), 'levels_active': True})

class DepartmentsView(View):
	template_name = 'configure/config_list.html'
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {'departments': paginate(request, Department.objects.all()), 'departments_active': True})

class CountryAdd(LoginRequiredMixin, CreateView):
	model = Country
	template_name = 'configure/form.html'
	fields = [
		'name',
	]
	success_url = reverse_lazy('profiles:config-list')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Add Country"
		return context

class CountryEdit(LoginRequiredMixin, UpdateView):
	model = Country
	pk_url_kwarg = 'country_id'
	template_name = 'configure/form.html'
	fields = [
		'name',
	]
	success_url = reverse_lazy('profiles:config-list')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Edit Country"
		return context

class CityAdd(LoginRequiredMixin, CreateView):
	model = City
	template_name = 'configure/form.html'
	fields = [
		'country',
		'name',
		'abbreviation',
	]
	success_url = reverse_lazy('profiles:config-list')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Add City"
		return context

class CityEdit(LoginRequiredMixin, UpdateView):
	model = City
	pk_url_kwarg = 'city_id'
	template_name = 'configure/form.html'
	fields = [
		'country',
		'name',
		'abbreviation',
	]
	success_url = reverse_lazy('profiles:config-list')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Edit City"
		return context

class OfficeAdd(LoginRequiredMixin, CreateView):
	model = Office
	template_name = 'configure/form.html'
	fields = [
		'country',
		'city',
		'name',
		'code',
	]
	success_url = reverse_lazy('profiles:config-list')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Add Office/Branch"
		return context

class OfficeEdit(LoginRequiredMixin, UpdateView):
	model = Office
	pk_url_kwarg = 'office_id'
	template_name = 'configure/form.html'
	fields = [
		'country',
		'city',
		'name',
		'code',
	]
	success_url = reverse_lazy('profiles:config-list')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Edit Office/Branch"
		return context

class DepartmentAdd(LoginRequiredMixin, CreateView):
	model = Department
	template_name = 'configure/form.html'
	fields = [
		'country',
		'city',
		'office',
		'name',
		'code',
	]
	success_url = reverse_lazy('profiles:config-list')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Add Department"
		return context

class DepartmentEdit(LoginRequiredMixin, UpdateView):
	model = Department
	pk_url_kwarg = 'department_id'
	template_name = 'configure/form.html'
	fields = [
		'country',
		'city',
		'office',
		'name',
		'code',
	]
	success_url = reverse_lazy('profiles:config-list')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Edit Department"
		return context

class LevelAdd(LoginRequiredMixin, CreateView):
	model = Level
	template_name = 'configure/form.html'
	fields = [
		'name',
		'level',
	]
	success_url = reverse_lazy('profiles:config-list')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Add LEVEL"
		return context

class LevelEdit(LoginRequiredMixin, UpdateView):
	model = Level
	pk_url_kwarg = 'level_id'
	template_name = 'configure/form.html'
	fields = [
		'name',
		'level',
	]
	success_url = reverse_lazy('profiles:config-list')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Edit LEVEL"
		return context

def od_populator(request): # office and deprtment options populator
	data = {}
	if request.method == 'GET':		
		do = request.GET.get('do')

		if do == 'pop_offices':
			_city = request.GET.get('city')
			city = City.objects.get(name=_city)
			offices = Office.objects.filter(city=city).values()
			data['offices'] = list(offices)
			return JsonResponse(data)

		if do == 'pop_departments':
			_office = request.GET.get('office')
			_city = request.GET.get('city')
			city = City.objects.get(name=_city)
			office = Office.objects.get(name=_office, city=city)
			departments = Department.objects.filter(office=office, city=office.city).values()
			data['departments'] = list(departments)
			return JsonResponse(data)

	data['query'] ='error'
	return JsonResponse(data)
