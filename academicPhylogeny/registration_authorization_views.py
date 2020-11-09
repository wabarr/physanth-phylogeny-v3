from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from academicPhylogeny.forms import UserCreateForm

class LoginView(auth_views.LoginView):
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context["userCreateForm"] = UserCreateForm()
        return context

class PasswordResetView(auth_views.PasswordResetView):
    success_url = "/password_reset_email_sent/"

class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    post_reset_login = True


class PasswordResetEmailSent(TemplateView):
    template_name = "password_reset_email_sent.html"

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    pass

class LogoutView(auth_views.LogoutView):
    next_page="/"

