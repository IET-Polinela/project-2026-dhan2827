from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CitizenRegisterForm
from .models import CustomUser


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        messages.success(self.request, "Login berhasil.")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Logout berhasil.")
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    model = CustomUser
    form_class = CitizenRegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Registrasi berhasil, silakan login.")
        return super().form_valid(form)