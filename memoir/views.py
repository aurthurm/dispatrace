from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from guardian.mixins import PermissionRequiredMixin
from django.template.loader import render_to_string
from django.db.models import Q, F
from reversion.models import Version
from datetime import datetime

from memoir.permissions import (
		has_recipients, 
		can_comment, 
		can_close, 
		is_recent_commenter, 
		has_commented, 
		get_next_commenter, 
		all_have_commented
	)
from memoir.models import *
from memoir.utils import get_ref_number
from memoir.forms import UploadFileForm, MemoForm, MemoReasignForm
from memoir.mixins import AjaxableResponseMixin

from notify.signals import notify

class MemoCreate(LoginRequiredMixin, CreateView):
	model = Memo
	pk_url_kwarg = 'memo_id'
	slug_url_kwarg = 'memo_slug'
	form_class = MemoForm

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['formTitle'] = "Create a Memorandum"
		context['new_memo'] = True
		return context

	def form_valid(self, form):
		form.instance.sender = self.request.user
		form.instance.reference_number = get_ref_number(user=self.request.user)
		return super().form_valid(form)

class MemoUpdate(LoginRequiredMixin, UpdateView):
	model = Memo
	pk_url_kwarg = 'memo_id'
	slug_url_kwarg = 'memo_slug'
	form_class = MemoForm

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['formTitle'] = "Edit Memo"
		return context
    
class MemoReassign(LoginRequiredMixin, UpdateView):
	model = Memo
	pk_url_kwarg = 'memo_id'
	slug_url_kwarg = 'memo_slug'
	form_class = MemoReasignForm

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['formTitle'] = "Memo Reassignment"
		return context
    
class CommentCreate(LoginRequiredMixin, UserPassesTestMixin, AjaxableResponseMixin, CreateView):
	model = MemoComment
	fields = ['comment']
	pk_url_kwarg = 'memo_id'

	def test_func(self):
		user=self.request.user
		memo = get_object_or_404(Memo, pk=self.kwargs.get('memo_id'))
		return can_comment(user, memo)

	def form_valid(self, form):
		data = {}
		_password = self.request.POST['password_confirm']
		_user = authenticate(username=self.request.user.username, password=_password)

		if _user == self.request.user:
			data['pass_passed']     = "yes"
		else:
			data['success_message'] = "Wrong Password. Cant Submit Comment"
			data['pass_passed']     = "no"
			return JsonResponse(data)
		
		# try:
		# 	self.request.user == authenticate(username=self.request.user.username, password=_password)
		# except e:
		# 	raise PermissionDenied

		form.instance.commenter = self.request.user
		memo = get_object_or_404(Memo, pk=self.kwargs.get('memo_id'))
		form.instance.memo = memo
		response = super().form_valid(form)

		# Notify every recipient that a memo has been commented
		if has_recipients(memo):
			notify.send(
				self.request.user, 
				recipient_list=list(memo.recipients.all()), 
				actor=self.request.user,
				verb='has commented on memo', 
				target=memo, 
				nf_type='new_memo_sent'
			)
		# Notify the memo.to that a memo has been commented
		notify.send(
			self.request.user, 
			recipient=memo.to, 
			actor=self.request.user,
			verb='has commented on memo', 
			target=memo, 
			nf_type='new_memo_sent'
		)
		# Notify the memo.sender that a memo has been commented
		notify.send(
			self.request.user, 
			recipient=memo.sender, 
			actor=self.request.user,
			verb='has commented on memo', 
			target=memo, 
			nf_type='new_memo_sent'
		)
		# Notify the next commnter that they can comment on this memo
		if not all_have_commented(memo):
			next_commenter = get_next_commenter(self.request.user, memo)
			if next_commenter is not None:
				notify.send(
					self.request.user, 
					recipient=next_commenter, 
					actor=self.request.user,
					verb='You can now comment on memo', 
					target=memo, 
					nf_type='can_comment_on_memo'
				)
			else:
				if not has_commented(self.request.user, memo):
					notify.send(
						self.request.user, 
						recipient=memo.to, 
						actor=self.request.user,
						verb='You can now comment on memo', 
						target=memo, 
						nf_type='can_comment_on_memo'
					)

		if self.request.is_ajax():
			data['success_message'] = "Successfully submitted form data."
			return JsonResponse(data)
		else:
			return response

class MemoSearchListView(LoginRequiredMixin, TemplateView):
	model = Memo

	def get(self, *args, **kwargs):
		if self.request.is_ajax():
			data = []
			result = Memo.objects.filter(sent__exact=True)
			query = self.request.GET.get('qry')
			if query:
				result = result.filter(
						Q(reference_number__icontains=query) | 
						Q(subject__icontains=query) |
						Q(message__icontains=query)
					)
			else:
				result = result

			if len(result) != 0:	
				for memo in result:
					data.append({
						'memo_id': memo.pk,
						'memo_slug': memo.slug,
						'reference': memo.reference_number,
						'subject': memo.subject,
						'to': memo.to.username,
						'sender': memo.sender.username,
						'datesent': memo.date_sent,
						'archived': memo.archived,
						'open': memo.is_open
					})
				return JsonResponse(data, safe=False)
			else:
				return JsonResponse({})
		else:
			return render(self.request, 'memoir/memo_search.html', context={})

class MemoList(LoginRequiredMixin, ListView):
	"""
	Display aall memos in the system irregardless of statuses [ arhived, public, sent]
	"""
	queryset = Memo.objects.filter(is_open__exact=True, sent__exact=True, archived__exact=False)
	model = Memo
	paginate_by = 10

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context


class InTray(LoginRequiredMixin, ListView):
	"""
	Display a Memo List defined by:
	1. Memos i received but awaiting my commenting.
	2. If memo.to let memo remain in intray before close even after comenting
	"""
	model = Memo
	template_name = 'memoir/memo_list.html'

	def get_queryset(self):
		qry_1 = super(InTray, self).get_queryset()
		qry_2 = qry_1.filter(
			Q(sent__exact=True) & Q(is_open__exact=True) & ~Q(sender__exact=self.request.user), # ... and exclude those i created myself
			Q(recipients__username__contains=self.request.user.username) & ~Q(memocomment_comment__commenter__exact=self.request.user) | # if am recient exclude those i commented
			Q(to__exact=self.request.user) 
			# & Q(memocomment_comment__commenter__exact=self.request.user) , # where i am adresses to and include those i commented
		).distinct()
		qry = qry_2.filter(
			~Q(receptors__username__contains=self.request.user.username)
		)
		return qry

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['intray_active_class'] = 'active'
		return context

class Drafts(LoginRequiredMixin, ListView):
	"""
	Display a Memo List defined by:
	1. Memos i create but havent sent them yet.
	"""
	model = Memo
	template_name = 'memoir/memo_list.html'

	def get_queryset(self):
		results = super(Drafts, self).get_queryset()
		results = results.filter(
				Q(sent__exact=False) & Q(is_open__exact=True) & Q(sender__exact=self.request.user)
			).distinct()
		return results

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['drafts_active_class'] = 'active'
		return context

class OutTray(LoginRequiredMixin, ListView):
	"""
	Display a Memo List defined by:
	1. Memos i created and still being reviewed by others but not archived yet.
	2. Memos i received and has already commented but still awaits commenting by next user.
	"""
	model = Memo
	template_name = 'memoir/memo_list.html'

	def get_queryset(self):
		results = super(OutTray, self).get_queryset()
		results = results.filter(
				Q(sender__exact=self.request.user) & Q(sent__exact=True) & Q(is_open__exact=True) |
				Q(sent__exact=True) & Q(is_open__exact=True) & Q(recipients__username__contains=self.request.user.username) & Q(memocomment_comment__commenter__exact=self.request.user) |
				Q(is_open__exact=True) & Q(receptors__username__contains=self.request.user.username) 
			).distinct()
		return results		

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['outtray_active_class'] = 'active'
		return context

class MemoArchived(LoginRequiredMixin, ListView):
	"""
	Display a Archived memos where request user is either adressed to or cc.
	Why see memos that didnt concern you from inception :)
	"""
	model = Memo
	template_name = 'memoir/memo_list.html'
	paginate_by = 10

	def get_queryset(self):
		results = super(MemoArchived, self).get_queryset()
		return results.filter(
				Q(archived__exact=True),
				Q(sender__exact=self.request.user) #Q(to__exact=self.request.user) | Q(recipients__username__contains=self.request.user.username)
			).distinct()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['archived_active_class'] = 'active'
		return context

class MemoClosed(LoginRequiredMixin, ListView):
	"""
	Display a Archived memos where request user is either adressed to or cc.
	Why see memos that didnt concern you from inception :)
	"""
	model = Memo
	template_name = 'memoir/memo_list.html'
	paginate_by = 10

	def get_queryset(self):
		results = super(MemoClosed, self).get_queryset()
		return results.filter(
				Q(is_open__exact=False) & Q(archived__exact=False),
				Q(sender__exact=self.request.user) #Q(to__exact=self.request.user) | Q(recipients__username__contains=self.request.user.username)
			).distinct()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['closed_active_class'] = 'active'
		return context
		
class MemoArchiver(LoginRequiredMixin, CreateView):
	model = Archive

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context

	def form_valid(self, form):
		memo = get_object_or_404(Memo, pk=self.kwargs.get('memo_id'))
		form.instance.memo = memo
		form.instance.archiver = self.request.user
		form.instance.archived = True
		return super().form_valid(form)

class MemoDetail(LoginRequiredMixin, DetailView):
	model = Memo	
	pk_url_kwarg = 'memo_id'
	slug_url_kwarg = 'memo_slug'
	permission_required = 'memoir.view_memo'
	return_403 = True

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		memo_detail = Memo.objects.get(pk=self.kwargs['memo_id'])
		if memo_detail.commenting_required:
			comments = memo_detail.memocomment_comment.all()
			context['comments'] = comments
			can_comm = can_comment(self.request.user, memo_detail)
			if comments.count() != 0:
				can_edit_comm =  is_recent_commenter(self.request.user, memo_detail)
			else:
				can_edit_comm = False
				
			context['has_commented'] = False
			if has_commented(self.request.user, memo_detail):
				context['commented'] = "info"
				context['has_commented'] = True
			else:
				context['commented'] = "success"
			context['can_comment'] = can_comm
			context['can_edit_comment'] = can_edit_comm
		context['can_close'] = can_close(user=self.request.user, memo=memo_detail)
		context['which_memo'] = 'general'
		# context['history'] = memo_detail.history.all()
		memo_history = Version.objects.get_for_object(memo_detail)
		memo_versions = []
		for vers in memo_history:
			vers.object_id = int(vers.object_id) 
			memo_versions.append(vers)
		context['memo_trails'] = memo_versions

		# fuel_versions = []
		# for fuel in memo_detail.fuel_request.all():
		# 	fuel_history = Version.objects.get_for_object(fuel)
		# 	for vers in fuel_history:
		# 		vers.object_id = int(vers.object_id) 
		# 		fuel_versions.append(vers)		
		# context['fuel_trails'] = fuel_versions

		if memo_detail.commenting_required:
			comment_versions = []
			for comment in comments:
				comment_history = Version.objects.get_for_object(comment)
				for vers in comment_history:
					vers.object_id = int(vers.object_id) 
					comment_versions.append(vers)		
			context['comments_trails'] = comment_versions

			context['reveal_comment_message'] = False
			if not can_comm or not memo_detail.is_open:
				context['reveal_comment_css'] = 'display: none;'
				context['reveal_comment_message'] = True

		if self.request.user.has_perm('change_memo', memo_detail):
			can_edit = self.request.user.has_perm('change_memo', memo_detail)
			if memo_detail.receptors.all().count() != 0:
				can_edit = False
			context['can_edit'] = can_edit
		return context

def MemoTO(request, memo_id, memo_slug):
	if request.method == 'POST':
		memo = Memo.objects.get(pk=memo_id)
		to = request.POST.get('to')

		try:
			goes_to = User.objects.get(username=to)
		except User.DoesNotExist as e:
			raise e

		memo.to = goes_to
		memo.save()

		return JsonResponse({})

def MemoAddRecipients(request, memo_id, memo_slug):
	if request.method == 'POST':
		memo = Memo.objects.get(pk=memo_id)
		recipients = request.POST.get('recipients')

		try:
			user = User.objects.get(username=recipients)
		except User.DoesNotExist as e:
			raise e

		memo.recipients.add(user)

		return JsonResponse(
			{
				'data':user.username
			}
		)

def MemoSend(request, memo_id, memo_slug):
	if request.method == 'POST':
		data = {}
		memo = get_object_or_404(Memo, pk=memo_id)
		send = request.POST.get('send')
		_password = request.POST.get('c_password')

		_user = authenticate(username=request.user.username, password=_password)

		if _user == request.user:
			data['pass_passed']     = "yes"
		else:
			data['success_message'] = "Wrong Password. Cant Send memo"
			data['pass_passed']     = "no"
			return JsonResponse(data)

		memo.sent = send
		memo.date_sent = datetime.now()
		memo.reference_number = get_ref_number(user=request.user)
		memo.save()

		if has_recipients(memo):
			# Notify every recipient that a new memo has been sent
			notify.send(
				request.user, 
				recipient_list=list(memo.recipients.all()), 
				actor=request.user,
				verb='has sent a memo', 
				target=memo, 
				nf_type='new_memo_sent'
			)

		# Notify the memo.to that a memo has been sent
		notify.send(
			request.user, 
			recipient=memo.to, 
			actor=request.user,
			verb='has sent a memo', 
			target=memo, 
			nf_type='new_memo_sent'
		)

		# Notify the initial commnter that they can comment on this memo
		first_commenter = get_next_commenter(request.user, memo)
		if first_commenter != None:
			notify.send(
				request.user, 
				recipient=first_commenter, 
				actor=request.user,
				verb='You can now comment on memo', 
				target=memo, 
				nf_type='can_comment_on_memo'
			)

		data['success_message'] = 'Memo was successfully sent and is now in your OutTray'
		return JsonResponse(data)

def MemoClose(request, memo_id, memo_slug):
	data = {}
	if request.method == 'POST':
		close = request.POST.get('close')
		if close:
			memo = get_object_or_404(Memo, pk=memo_id)
			memo.is_open = False
			memo.save()
			# Notify the memo.sender that a memo has been commented
			notify.send(
				request.user, 
				recipient=memo.sender, 
				actor=request.user,
				verb='has closed memo', 
				target=memo, 
				nf_type='new_memo_sent'
			)
			data['close_message'] = f'Memo was successfully closed and has been sent back to @{memo.sender}'
	return JsonResponse(data)

def MemoRecept(request, memo_id, memo_slug):
	if request.method == 'POST':
		data = {}
		recept = request.POST.get('recept')
		if recept:
			memo = get_object_or_404(Memo, pk=memo_id)
			if request.user in memo.recipients.all() or request.user == memo.to:
				memo.receptors.add(request.user)
				memo.save()
				data['close_message'] = f'Memo has been successfully labelled as recepted'
			else:				
				data['close_message'] = f'Error, you are not the recipient for this memo'

			#Close Memo automatically after everyone has recepted
			all_recipients = memo.recipients.all().count() + 1
			if all_recipients == memo.receptors.all().count():
				memo.is_open = False
				memo.save()
				data['close_message'] = f'Memo has been successfully labelled as recepted and memo is now closed'

		return JsonResponse(data)

def MemoArchive(request, memo_id, memo_slug):
	if request.method == 'POST':
		data = {}
		memo = get_object_or_404(Memo, pk=memo_id)
		archive = request.POST.get('archive')
		memo_for_archive = Archive.objects.create(
								memo=memo,
								archived=archive,
								archiver=request.user
							)
		memo_for_archive.save()
		data['archive_message'] = 'Memo was successfully and permanently archived.'
		return JsonResponse(data)

def CommentEdit(request, memo_id, comment_id):
	data = {}
	if request.method == 'POST':
		comment = get_object_or_404(MemoComment, pk=comment_id)
		new_comment = request.POST.get('comment')
		password_conf = request.POST.get('password_confirm')
		_user = authenticate(username=request.user.username, password=password_conf)

		if _user == request.user:
			data['pass_passed'] = 'yes'
		else:			
			data['success_message'] = 'Wrong Password. Cant Submit Comment'
			data['pass_passed'] = 'no'
			return JsonResponse(data)

		comment.comment = new_comment
		comment.save()
		data['success_message'] = "Comment Successfully updated"
		return JsonResponse(data)

	if request.method == 'GET':
		comment = get_object_or_404(MemoComment, pk=comment_id)
		c_id = '#comment-' + str(comment_id)
		form_id = 'form#comment-' + str(comment_id)
		data['comment'] = comment.comment
		data['comment_id'] = c_id
		data['form_id'] = form_id
		# data['comment_form'] = render_to_string('memoir/edit_comment_form.html', {'form_id':form_id, 'memo_id':memo_id, 'comment_id':comment_id }, request=request)
		return JsonResponse(data)


class FileUploadView(FormView):
	form_class = UploadFileForm
	template_name = 'memoir/upload.html'
	pk_url_kwarg = 'memo_id'
	slud_url_kwarg = 'memo_slud'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		memo = get_object_or_404(Memo, pk=self.kwargs.get('memo_id'))
		context['memo_subject'] = memo.subject
		return context

	def post(self, request, *args, **kwargs):
		memo = get_object_or_404(Memo, pk=self.kwargs.get('memo_id'))
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		file = request.FILES.get('file')
		name = request.POST.get('file_name')
		if form.is_valid():			
			attachment = Attachment.objects.create(
					memo=memo,
					file=file,
					file_name=name
				)
			attachment.save()
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def get_success_url(self, *args, **kwargs):
		return reverse('memoir:memo-detail', kwargs={'memo_id': self.kwargs.get('memo_id'), 'memo_slug': self.kwargs.get('memo_slug')})