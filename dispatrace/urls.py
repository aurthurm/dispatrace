from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from ajax_select import urls as ajax_select_urls
from django.conf.urls.static import static

from dispatrace.views import signup, dashboard, dash_stats, active_notifications, force_pwd_reset

admin.autodiscover()

urlpatterns = [
    path('notifications/', include('notify.urls', 'notifications')),
    path('session_security/', include('session_security.urls')),
    path('ajax_select/', include(ajax_select_urls)),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('admin/', admin.site.urls),
    path('register', signup, name='create-account'),
    path('notification-count', active_notifications, name='notify-count-active'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/force-password-reset/', force_pwd_reset, name='pasword-force-reset'),
    path('', dashboard, name='home'),
    path('dash-stats/', dash_stats, name='dash-stats'),
    path('profiles/', include('profiles.urls')),
    path('memos/', include('memoir.urls')),
    path('fuel/', include('fuel.urls')),
    path('notices/', include('notice.urls')),
]

#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import os
    from django.views.generic.base import RedirectView
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += static(settings.MEDIA_URL + 'uploads/', document_root=os.path.join(settings.MEDIA_ROOT, 'uploads'))

