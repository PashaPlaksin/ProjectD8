from django import urls
from django.shortcuts import render
from allauth.account.views import SignupView, LoginView, PasswordResetView

class MySignupView(SignupView):
    template_name = 'accounts/base.html'

class MyLoginView(LoginView):
    template_name = 'accounts/base.html'


class MyPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'

urlpatterns = [
    urls(r'^accounts/login', MyLoginView.as_view(), name='account_login'),
    # url(r'^accounts/signup', MySignupView.as_view(), name='account_signup'),
    # url(r'^accounts/password_reset', MyPasswordResetView.as_view(), name='account_reset_password'),
]
# Create your views here.
