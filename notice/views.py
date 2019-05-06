from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime

from .models import *
from .forms import NoticeForm, NoticeUpdateForm, ListingUpdate

class ListingsAllList(ListView):
	model = Listing

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['header'] = "Notice Board Manager"
		context['sub_header'] = "A listing is a group of similar notifices"
		return context

class ListingsList(ListView):
	model = Listing
	template_name = 'notice/listings.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		# get the request / logged on user
		user = self.request.user
		# Get all the boards the user has created
		user_listings = Listing.objects.filter(creator=user)
		context['header'] = "Notice Board Manager"
		context['sub_header'] = "A category groups similar notices together"
		context['user_listings'] = user_listings
		return context


class ListingCreate(LoginRequiredMixin, CreateView):
	model = Listing
	fields = ['name', 'description']

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context

	def form_valid(self, form):
		form.instance.creator = self.request.user
		return super().form_valid(form)

class ListingDelete(LoginRequiredMixin, DeleteView):
	model = Listing
	pk_url_kwarg = 'listing_id'
	success_url = reverse_lazy('notice:notice-listings')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		listing_id = self.kwargs['listing_id']
		listing = Listing.objects.get(pk=listing_id)
		listing_count = listing.notice_listings.count()
		if listing_count == 0:
			context['deleteable'] = True
		else:
			context['deleteable'] = False
			context['reason'] = "There (is/are) " + str(listing_count) + " notice(s) in this category. Delete all notices assigned to this category first in order to delete this category"
		return context

class ListingEdit(LoginRequiredMixin, View):
	model = Listing
	pk_url_kwarg = 'listing_id'

	def post(self, form, **kwargs):
		data =  dict()
		listing = Listing.objects.get(pk=self.kwargs['listing_id'])
		form = ListingUpdate(instance=listing, data=self.request.POST)
		if form.is_valid():
			listing = form.save()
			data['error'] =  "all is good"
		else:
			data['error'] =  "form not valid!"
		return reverse_lazy('notice:notice-listings')

class EditListing(LoginRequiredMixin, UpdateView):
	model = Listing
	pk_url_kwarg = 'listing_id'
	success_url = reverse_lazy('notice:notice-listings')
	form_class = ListingUpdate
	template_name = "notice/notice_form.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Edit Category"
		return context

class NoticeCreate(LoginRequiredMixin, CreateView):
	model = Notice
	# fields = ['name', 'priority', 'description', 'expiry']
	form_class = NoticeForm
	pk_url_kwarg = 'listing_id'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Create a Notice"
		return context

	def form_valid(self, form):
		form.instance.creator = self.request.user
		listing = get_object_or_404(Listing, pk=self.kwargs.get('listing_id'))
		form.instance.Listing = listing
		_expry = self.request.POST.get('expiry')
		_prio = self.request.POST.get('priority')
		form.instance.priority = _prio
		form.instance.expiry = datetime.strptime(_expry,'%Y-%m-%d')
		return super().form_valid(form)

class NoticeUpdate(LoginRequiredMixin, UpdateView):
	model = Notice
	form_class = NoticeUpdateForm
	pk_url_kwarg = 'item_id'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form_title'] = "Update a  Notice"
		return context

	def form_valid(self, form):
		form.instance.creator = self.request.user
		listing = get_object_or_404(Listing, pk=self.kwargs.get('listing_id'))
		form.instance.Listing = listing
		_expry = self.request.POST.get('expiry')
		_prio = self.request.POST.get('priority')

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

		form.instance.priority = _prio
		form.instance.expiry = datetime.strptime(_expry,'%Y-%m-%d')
		return super().form_valid(form)

class NoticeDelete(LoginRequiredMixin, DeleteView):
	model = Notice
	pk_url_kwarg = 'item_id'
	success_url = reverse_lazy('notice:notice-listings')

def load_offices(request):
    city_id = request.GET.get('city')
    city = get_object_or_404(City, pk=city_id)
    offices = city.offices.all().order_by('name')
    return render(request, 'notice/city_dropdown_list_options.html', {'items': offices})

def load_departments(request):
    office_id = request.GET.get('office')
    office = get_object_or_404(Office, pk=office_id)
    departments = office.departments.all().order_by('name')
    return render(request, 'notice/department_dropdown_list_options.html', {'items': departments})