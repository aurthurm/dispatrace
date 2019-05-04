from django.contrib import admin
from django.urls import path, include, re_path

from memoir.views import *

app_name="memoir"
urlpatterns = [
    path('in-tray', InTray.as_view(), name='in-tray'),
    path('out-tray', OutTray.as_view(), name='out-tray'),
    path('archived', MemoArchived.as_view(), name='archived'),
    path('closed', MemoClosed.as_view(), name='closed'),
    path('drafts', Drafts.as_view(), name='drafts'),

    path('memo/<int:memo_id>/<slug:memo_slug>', MemoDetail.as_view(), name='memo-detail'),
    path('create-new', MemoCreate.as_view(), name='create-memo'),
    path('memo/<int:memo_id>/<slug:memo_slug>/edit', MemoUpdate.as_view(), name='memo-edit'),
    path('memo/<int:memo_id>/<slug:memo_slug>/delete', MemoDelete.as_view(), name='memo-delete'),
    path('memo/<int:memo_id>/<slug:memo_slug>/reassign', MemoReassign.as_view(), name='memo-reassign'),
    path('memo/<int:memo_id>/<slug:memo_slug>/send', MemoSend, name='memo-send'),
    path('memo/<int:memo_id>/<slug:memo_slug>/close', MemoClose, name='memo-close'),
    path('memo/<int:memo_id>/<slug:memo_slug>/recept', MemoRecept, name='memo-recept'),
    path('memo/<int:memo_id>/<slug:memo_slug>/archive', MemoArchive, name='memo-archive'),
    path('memo/<int:memo_id>/<slug:memo_slug>/add-recipient', MemoAddRecipients, name='add-recipient'),
    path('memo/<int:memo_id>/<slug:memo_slug>/attach-item', FileUploadView.as_view(), name='attach-item'),
    path('memo/<int:memo_id>/<slug:memo_slug>/add-to', MemoTO, name='add-to'),
    path('memo/<int:memo_id>/<slug:memo_slug>/comment-attach', CommentCreate.as_view(), name='memo-comment'),
    path('memo/<int:memo_id>/comment/<int:comment_id>/edit', CommentEdit, name='comment-edit'),   
    path('search', MemoSearchListView.as_view(), name='memo-search'),
]