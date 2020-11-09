# -*- coding: utf-8 -*-
from django.conf.urls import url
from academicPhylogeny.registration_authorization_views import *

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    url('^password_reset/$', PasswordResetView.as_view()),
    url('^password_reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url('^password_reset_complete/$', PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    url('^password_reset_email_sent/$',PasswordResetEmailSent.as_view(), name="password_reset_email_sent")
    ]