from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
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
from profiles.models import *
from notice.models import Notice
from notify.models import Notification

def active_notifications(request):
    data = {}
    recipient = request.user
    unread_and_active = Notification.objects.unread().filter(recipient=recipient)
    active = Notification.objects.active().filter(recipient=recipient)
    data['unread'] = unread_and_active.count()
    data['active'] = active.count()
    return JsonResponse(data)

@login_required
def dashboard(request):
    notices = Notice.objects.all()    
    yesterday = timezone.now() - timedelta(days=1)
    notices = notices.filter(expiry__gt=yesterday)
    context={
       'notices': notices 
    }
    return render(request, '_dashboard/main_dash.html', context=context)

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