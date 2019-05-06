from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from datetime import datetime

from django.utils import timezone
from datetime import timedelta

from dispatrace.forms import SignUpForm
from memoir.models import *
from fuel.models import Fuel
from profiles.models import *
from notice.models import Notice
from notify.models import Notification

def active_notifications(request):
    data = {}
    recipient = request.user
    if not recipient.is_anonymous:
        unread_and_active = Notification.objects.unread().filter(recipient=recipient)
        active = Notification.objects.active().filter(recipient=recipient)
        data['unread'] = unread_and_active.count()
        data['active'] = active.count()
    else:
        pass
    return JsonResponse(data)

@login_required
def dashboard(request):
    context = {}
    try:
        if request.user.user_profile.force_password_change:
            context['passord_force_reset'] = True
            # return redirect('django.contrib.auth.views.password_change')
    except AttributeError: #No profile?
        context['passord_force_reset'] = False    

    notices = Notice.objects.all()    
    yesterday = timezone.now() - timedelta(days=1)
    notices = notices.filter(expiry__gt=yesterday)
    context['notices'] = notices 
    return render(request, '_dashboard/main_dash.html', context=context)

def force_pwd_reset(request):
    data = {}
    passwords = request.POST
    pass_1 = passwords.get('password1', None)
    pass_2 = passwords.get('password2', None)
    if pass_1 == pass_2:
        user = request.user
        user.set_password(pass_2)
        user.save()
        profile = user.user_profile
        profile.force_password_change = False
        profile.save()
        data['message'] = "Success: Your password was successfully changed. You will be redirected for a re-login"
        data['error'] = False
    else:
        data['message'] = "The Passwords you provided do not match. Try again"
        data['error'] = True
    return JsonResponse(data)

@login_required
def signup_old(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully: Please Update every field. Its Mandatory !!!')
            username = form.cleaned_data.get('username')
            # raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=raw_password)
            # login(request, user)
            user = User.objects.get(username=username)
            profile_id = user.user_profile.pk
            return redirect('profiles:profile-detail', profile_id=profile_id)
        else:
            registration_form = SignUpForm()
    else:
        registration_form = SignUpForm()
    return render(request, 'registration/register.html', {'registration_form': registration_form})

@login_required
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                )
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            messages.success(request, 'Account created successfully: Please Update every field. Its Mandatory !!!')
            profile_id = user.user_profile.pk
            return redirect('profiles:profile-detail', profile_id=profile_id)
        else:
            registration_form = SignUpForm()
    else:
        registration_form = SignUpForm()
    return render(request, 'registration/register.html', {'registration_form': registration_form})

def dash_stats(request):
    """
    get mini sidebar-reports for Memos counts for the logged in user.
    """
    data = {}
    _intray = Memo.objects.filter(
        Q(sent__exact=True) & Q(is_open__exact=True) & ~Q(sender__exact=request.user), # ... and exclude those i created myself
        Q(recipients__username__contains=request.user.username) & ~Q(memocomment_comment__commenter__exact=request.user) | # if am recient exclude those i commented
        Q(to__exact=request.user) 
        # & Q(memocomment_comment__commenter__exact=request.user) , # where i am adresses to and include those i commented
    ).distinct()
    intray = _intray.filter(
        ~Q(receptors__username__contains=request.user.username)
    )

    drafts = Memo.objects.filter(
            Q(sent__exact=False) & Q(is_open__exact=True) & Q(sender__exact=request.user)
        ).distinct()

    outtray = Memo.objects.filter(
            Q(sender__exact=request.user) & Q(sent__exact=True) & Q(is_open__exact=True) |
            Q(sent__exact=True) & Q(is_open__exact=True) & Q(recipients__username__contains=request.user.username) & Q(memocomment_comment__commenter__exact=request.user) |
            Q(is_open__exact=True) & Q(receptors__username__contains=request.user.username) 
        ).distinct()

    archived = Memo.objects.filter(
            Q(archived__exact=True),
            Q(sender__exact=request.user) #Q(to__exact=request.user) | Q(recipients__username__contains=request.user.username)
        ).distinct()

    closed = Memo.objects.filter(
            Q(is_open__exact=False) & Q(archived__exact=False),
            Q(sender__exact=request.user) #Q(to__exact=request.user) | Q(recipients__username__contains=request.user.username)
        ).distinct()

    data['closed_count'] = closed.count()
    data['intray_count'] = intray.count()
    data['outtray_count'] = outtray.count()
    data['archived_count'] = archived.count()
    data['drafts_count'] = drafts.count()
    return JsonResponse(data)

class Reports(TemplateView):
    """
    Generate System Reports for Memos, Fuel and Notices.
    based on office provided  by user else generate system wide reports
    if no office is provided.
    """
    model = Fuel

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            data = {}
            fuel = Fuel.objects.all()
            memo = Memo.objects.all()
            notice = Notice.objects.all()
            user = self.request.user        

            _city = str(self.request.GET.get('city', 0)).strip()
            _office = str(self.request.GET.get('office', 0)).strip()
            _department = str(self.request.GET.get('department', 0)).strip()
            print(self.request.GET)

            if _city:
                city = get_object_or_404(City, pk=int(_city))
                if _office:
                    office = get_object_or_404(Office, pk=int(_office))
                    if _department:
                        department = get_object_or_404(Department, pk=int(_department))            
                        notice = notice.filter(
                                Q(creator__user_profile__city__exact=city) &
                                Q(creator__user_profile__office__exact=office) &
                                Q(creator__user_profile__department__exact=department)
                            )
                        fuel = fuel.filter(
                                Q(requester__user_profile__city__exact=city) &
                                Q(requester__user_profile__office__exact=office) &
                                Q(requester__user_profile__department__exact=department)
                            )
                        memo = memo.filter(
                                Q(sender__user_profile__city__exact=city) &
                                Q(sender__user_profile__office__exact=office) &
                                Q(sender__user_profile__department__exact=department)
                            )
                    else:
                        department = None            
                        notice = notice.filter(
                                Q(creator__user_profile__city__exact=city) &
                                Q(creator__user_profile__office__exact=office)
                            )
                        fuel = fuel.filter(
                                Q(requester__user_profile__city__exact=city) &
                                Q(requester__user_profile__office__exact=office)
                            )
                        memo = memo.filter(
                                Q(sender__user_profile__city__exact=city) &
                                Q(sender__user_profile__office__exact=office)
                            )
                else:
                    office = None
                    department = None            
                    notice = notice.filter(
                            Q(creator__user_profile__city__exact=city)
                        )
                    fuel = fuel.filter(
                            Q(requester__user_profile__city__exact=city)
                        )
                    memo = memo.filter(
                            Q(sender__user_profile__city__exact=city)
                        )
            else:
                city = None
                office = None
                department = None
                notice = notice
                fuel = fuel
                memo = memo

            yesterday = timezone.now() - timedelta(days=1)
            active_notice = notice.filter(expiry__gt=yesterday) 
            data['notice'] = {
                'total': notice.count(),
                'active': active_notice.count(),
                'expired': notice.count() - active_notice.count()
            }

            data['fuel'] = {
                'total': fuel.count(),
                'open': fuel.filter(is_open__exact=True).count(),
                'closed': fuel.filter(is_open__exact=False, archived__exact=False).count(),
                'archived': fuel.filter(is_open__exact=False, archived__exact=True).count(),
                'vehicle': fuel.filter(plus_vehicle=True).count(),
                'declined': fuel.filter(is_open__exact=False, accepted=False).count(),
                'approved': fuel.filter(is_open__exact=False, accepted=True).count()
            }

            data['memo'] = {
                'total': memo.count(),
                'open': memo.filter(sent__exact=True, is_open__exact=True).count(),
                'closed': memo.filter(sent__exact=True, is_open__exact=False, archived__exact=False).count(),
                'archived': memo.filter(sent__exact=True, is_open__exact=False, archived__exact=True).count(),
                'drafts': memo.filter(sent__exact=False).count(),
                'private': memo.filter(mem_type__exact=PRIVATE).count(),
            }
            return JsonResponse(data, safe=False)
        else:
            return render(self.request, '_reports/reports.html', context={
                    'cities': City.objects.all()
                })


