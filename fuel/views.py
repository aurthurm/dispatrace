from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.db.models import Sum, Q
from datetime import datetime
from django.http import JsonResponse

from .models import Fuel, Comment
from .utils import get_ref_number
from .forms import FuelForm, FuelReasignForm
from profiles.models import *

from notify.signals import notify

class FuelListing(ListView):
    model = Fuel
    paginate_by = 15

    def get_queryset(self):
        query = super(FuelListing, self).get_queryset()
        queryset = query.filter(
            Q(requester__exact=self.request.user) |
            Q(approver__exact=self.request.user) & Q(is_open__exact=True) |
            Q(assessor__exact=self.request.user) & Q(is_open__exact=True)
        )
        return queryset.filter(archived__exact=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class FuelArchivedListing(ListView):
    model = Fuel
    paginate_by = 15
    template_name = 'fuel/fuel_list.html'

    def get_queryset(self):
        query = super(FuelArchivedListing, self).get_queryset()
        queryset = query.filter(
            Q(requester__exact=self.request.user) |
            Q(approver__exact=self.request.user) & Q(is_open__exact=True) |
            Q(assessor__exact=self.request.user) & Q(is_open__exact=True)
        )
        return queryset.filter(archived__exact=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fuel_archives'] = True
        return context
    
class FuelSearch(TemplateView):
    model = Fuel

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            data = []
            result = Fuel.objects.all()
            query = self.request.GET.get('qry')
            if query:
                result = result.filter(
                        Q(reference_number__icontains=query) | 
                        Q(reason__icontains=query)
                    )
            else:
                result = result

            if len(result) != 0:	
                for fuel in result:
                    data.append({
                        'id': fuel.pk,
                        'reference': fuel.reference_number,
                        'reason': fuel.reason,
                        'status': fuel.accepted,
                        'requestor': fuel.requester.username,
                        'amount': fuel.amount,
                        'origin': fuel.origin.name,
                        'destination': fuel.destination.name,
                        'type': fuel.fuel_type
                    })
                return JsonResponse(data, safe=False)
            else:
                return JsonResponse({})
        else:
            return render(self.request, 'fuel/fuel_list.html', context={})

class FuelRequest(LoginRequiredMixin, CreateView):
    model = Fuel
    form_class = FuelForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formTitle'] = "Create a new Fuel Request"
        context['new_fuel'] = True
        return context

    def form_valid(self, form):
        form.instance.requester = self.request.user
        form.instance.reference_number = get_ref_number(user=self.request.user)
        form.instance.city = self.request.user.user_profile.city
        form.instance.department = self.request.user.user_profile.department
        form.instance.office = self.request.user.user_profile.office
        return super().form_valid(form)

class FuelUpdate(LoginRequiredMixin, UpdateView):
	model = Fuel
	form_class = FuelForm
	pk_url_kwarg = 'fuel_id'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['formTitle'] = "Edit Fuel Request"
		return context
    
class FuelDetail(LoginRequiredMixin, DetailView):
	model = Fuel	
	pk_url_kwarg = 'fuel_id'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context

class FuelReassign(LoginRequiredMixin, UpdateView):
	model = Fuel
	pk_url_kwarg = 'fuel_id'
	form_class = FuelReasignForm

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['formTitle'] = "Fuel Reassignment"
		return context

def fuel_archive(request, fuel_id):
    fuel = get_object_or_404(Fuel, pk=int(fuel_id))
    fuel.archived = True
    fuel.save()
    return JsonResponse({
        'success': 'success'
    })

@login_required
def close_request(request, fuel_id):
    data = {}
    _value = request.POST.get('acceptance')
    fuel = Fuel.objects.get(pk=fuel_id)
    if _value == 'accepted':
        fuel.is_open=False
        fuel.accepted=True
        fuel.save()
        data['state'] = "accepted"
        data['success_message'] = "Request accepted and is now closed"
    if _value == 'declined':
        fuel.is_open=False
        fuel.accepted=False
        fuel.save()
        data['state'] = "declined"
        data['success_message'] = "Request declined and is now closed"

    notify.send(
        request.user, 
        recipient=fuel.requester, 
        actor=request.user,
        verb='Request was Finalised',
        target=fuel, 
        nf_type='can_comment_on_memo'
    )
    
    return JsonResponse(data)

@login_required
def fuel_comment(request, fuel_id):
    data = {}
    comment = request.POST.get('comment')
    password = request.POST.get('password')
    _user = authenticate(username=request.user.username, password=password)

    if _user == request.user:
        data['pass_passed'] = 'yes'
    else:			
        data['success_message'] = 'Wrong Password. Cant Submit Comment'
        data['pass_passed'] = 'no'
        return JsonResponse(data)

    fuel_request = Fuel.objects.get(pk=fuel_id)
    Comment.objects.create(
        fuel=fuel_request,
        comment=comment,
        commenter=request.user
    )

    if request.user == fuel_request.approver:
        pass
    else:
        notify.send(
            request.user, 
            recipient=fuel_request.approver, 
            actor=request.user,
            verb='Request has been Assessed',
            target=fuel_request, 
            nf_type='can_comment_on_memo'
        )
        notify.send(
            request.user, 
            recipient=fuel_request.approver, 
            actor=request.user,
            verb='You can now Approve',
            target=fuel_request, 
            nf_type='can_comment_on_memo'
        )
        notify.send(
            request.user, 
            recipient=fuel_request.requester, 
            actor=request.user,
            verb='Request has been Assessed',
            target=fuel_request, 
            nf_type='can_comment_on_memo'
        )

    data['success_message'] = 'Comment was successfully submitted'
    return JsonResponse(data)

@login_required
def reports_fuel(request):
    if request.method == "GET" and not request.is_ajax():
        cities = City.objects.all()
        departments = Department.objects.all()
        offices = Office.objects.all()
        diesel = Fuel.objects.filter(fuel_type__exact='Diesel')
        petrol = Fuel.objects.filter(fuel_type__exact='Petrol')
        context = {
            'diesel_requests': diesel.count(),
            'petrol_requests': petrol.count(),
            'diesel_amount_total': diesel.aggregate(dat=Sum('amount')),
            'petrol_amount_total': petrol.aggregate(pat=Sum('amount')),
            'cities': cities
        }
        return render(request, '_reports/fuel.html', context=context)

    if request.method == 'GET' and request.is_ajax:
        data = {}
        _city = request.GET.get('city')
        _office = request.GET.get('office')
        _department = request.GET.get('department')
        _dateFrom = request.GET.get('dateFrom')
        _dateTo = request.GET.get('dateTo')

        if _dateTo != '':
            dateTo = datetime.strptime(_dateTo,'%m/%d/%Y')
        else:
            dateTo = datetime.now()

        if _dateFrom != '':
            dateFrom = datetime.strptime(_dateFrom,'%m/%d/%Y')
        else:
            dateFrom = datetime.strptime('1/1/2010','%m/%d/%Y')

        if _city != 'None':
            city = City.objects.get(name=_city)
        else:
            city = 'None'

        if _office != 'None':
            office = Office.objects.get(name=_office, city=city)
        else:
            office = 'None'
            
        if _department != 'None':
            department = Department.objects.get(name=_department, office=office, city=city)
        else:
            department = 'None'

        if city == 'None':
            diesel = Fuel.objects.filter(fuel_type__exact='Diesel', date_requested__range=(dateFrom, dateTo))
            petrol = Fuel.objects.filter(fuel_type__exact='Petrol', date_requested__range=(dateFrom, dateTo))
            data['diesel_requests'], data['petrol_requests'] = diesel.count(), petrol.count()
            data['diesel_amount_total'], data['petrol_amount_total'] = diesel.aggregate(dat=Sum('amount')), petrol.aggregate(dat=Sum('amount'))
        
        if city != "None" and office == 'None':
            diesel = Fuel.objects.filter(
                   Q(city__exact=city) & Q(fuel_type__exact='Diesel')
                )
            diesel = diesel.filter(date_requested__range=(dateFrom, dateTo))
            petrol = Fuel.objects.filter(
                    Q(city__exact=city) & Q(fuel_type__exact='Petrol')
                )
            petrol = petrol.filter(date_requested__range=(dateFrom, dateTo))
            data['diesel_requests'], data['petrol_requests'] = diesel.count(), petrol.count()
            data['diesel_amount_total'], data['petrol_amount_total'] = diesel.aggregate(dat=Sum('amount')), petrol.aggregate(dat=Sum('amount'))
        
        if city != 'None' and office != 'None' and department == 'None':
            diesel = Fuel.objects.filter(
                   Q(city__exact=city) & Q(office__exact=office) & Q(fuel_type__exact='Diesel')
                )
            diesel = diesel.filter(date_requested__range=(dateFrom, dateTo))
            petrol = Fuel.objects.filter(
                    Q(city__exact=city) & Q(office__exact=office) & Q(fuel_type__exact='Petrol')
                )
            petrol = petrol.filter(date_requested__range=(dateFrom, dateTo))
            data['diesel_requests'], data['petrol_requests'] = diesel.count(), petrol.count()
            data['diesel_amount_total'], data['petrol_amount_total'] = diesel.aggregate(dat=Sum('amount')), petrol.aggregate(dat=Sum('amount'))
        
        if city != 'None' and office != 'None' and department != 'None':
            diesel = Fuel.objects.filter(
                   Q(city__exact=city) & Q(office__exact=office) & Q(department__exact=department) & Q(fuel_type__exact='Diesel')
                )
            diesel = diesel.filter(date_requested__range=(dateFrom, dateTo))
            petrol = Fuel.objects.filter(
                    Q(city__exact=city) & Q(office__exact=office) & Q(department__exact=department) & Q(fuel_type__exact='Petrol')
                )
            petrol = petrol.filter(date_requested__range=(dateFrom, dateTo))
            data['diesel_requests'], data['petrol_requests'] = diesel.count(), petrol.count()
            data['diesel_amount_total'], data['petrol_amount_total'] = diesel.aggregate(dat=Sum('amount')), petrol.aggregate(dat=Sum('amount'))

        return JsonResponse(data)
