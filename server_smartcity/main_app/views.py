from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Report
from .forms import ReportForm


# HOME
def home(request):
    return render(request, 'main_app/index.html')


# MIXIN PROTEKSI ADMIN
class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Silakan login terlebih dahulu.")
            return redirect('login')

        if not request.user.is_admin:
            messages.error(request, "Akses Ditolak. Hanya admin yang dapat mengakses fitur ini.")
            return redirect('report_list')

        return super().dispatch(request, *args, **kwargs)

class DashboardView(AdminRequiredMixin, ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'

    def get_queryset(self):
        return Report.objects.exclude(status='DRAFT').order_by('-id')
    
# LIST LAPORAN (boleh untuk semua user)
class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'

    def get_queryset(self):

        user = self.request.user

        # admin tidak boleh lihat draft orang
        if user.is_superuser:
            return Report.objects.exclude(status='DRAFT')

        return (
            Report.objects.filter(reporter=user)
            |
            Report.objects.exclude(status='DRAFT')
        ).distinct()
    
class MyReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'

    def get_queryset(self):

        return Report.objects.filter(
            reporter=self.request.user
        ).order_by('-id')


# DETAIL LAPORAN (boleh untuk semua user)
class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/detail_report.html'
    context_object_name = 'report'

# CREATE REPORT (LOGIN REQUIRED)
class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        messages.success(self.request, "Laporan berhasil ditambahkan!")
        return super().form_valid(form)

# UPDATE REPORT
class ReportUpdateView(LoginRequiredMixin, UpdateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):

        report = self.get_object()

        if request.user.is_superuser:
            messages.error(request, "Admin tidak boleh mengedit laporan.")
            return redirect('report_list')

        if report.reporter != request.user:
            messages.error(request, "Anda bukan pemilik laporan.")
            return redirect('report_list')

        if report.status != 'DRAFT':
            messages.error(request, "Hanya laporan DRAFT yang bisa diedit.")
            return redirect('report_list')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil diperbarui!")
        return super().form_valid(form)
    
# DELETE REPORT
class ReportDeleteView(LoginRequiredMixin, DeleteView):
    model = Report
    template_name = 'main_app/delete_report.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):

        report = self.get_object()

        if request.user.is_superuser:
            messages.error(request, "Admin tidak boleh menghapus laporan.")
            return redirect('report_list')

        if report.reporter != request.user:
            messages.error(request, "Anda bukan pemilik laporan.")
            return redirect('report_list')

        if report.status != 'DRAFT':
            messages.error(request, "Hanya laporan DRAFT yang bisa dihapus.")
            return redirect('report_list')

        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Laporan berhasil dihapus!")
        return super().delete(request, *args, **kwargs)

# UPDATE STATUS (ADMIN ONLY)
class ReportUpdateStatusView(AdminRequiredMixin, View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')

        valid_transitions = {
            "REPORTED": "VERIFIED",
            "VERIFIED": "IN_PROGRESS",
            "IN_PROGRESS": "RESOLVED",
        }

        if report.status in valid_transitions and valid_transitions[report.status] == new_status:
            report.status = new_status
            report.save()
            messages.success(request, "Status berhasil diperbarui!")
        else:
            messages.error(request, "Perubahan status tidak valid!")

        return redirect('report_list')
    
class ReportSearchView(View):
    def get(self, request):
        keyword = request.GET.get('q', '')
        user = request.user

        reports = Report.objects.filter(
            Q(title__icontains=keyword) |
            Q(category__icontains=keyword) |
            Q(status__icontains=keyword) |
            Q(location__icontains=keyword)
        )

        # Admin tidak boleh melihat draft siapa pun
        if user.is_authenticated and user.is_admin:
            reports = reports.exclude(status='DRAFT')

        # User biasa hanya boleh melihat laporan sendiri + laporan publik non-draft
        elif user.is_authenticated:
            reports = reports.filter(
                Q(reporter=user) | ~Q(status='DRAFT')
            ).distinct()

        # Guest hanya boleh melihat laporan publik non-draft
        else:
            reports = reports.exclude(status='DRAFT')

        reports = reports.order_by('-id')

        data = [
            {
                'id': report.id,
                'title': report.title,
                'category': report.category,
                'location': report.location,
                'status': report.status,
            }
            for report in reports
        ]

        return JsonResponse({'reports': data})


class ReportDetailJsonView(View):
    def get(self, request, pk):
        report = Report.objects.get(pk=pk)

        data = {
            'id': report.id,
            'title': report.title,
            'category': report.category,
            'description': report.description,
            'location': report.location,
            'status': report.status,
        }

        return JsonResponse(data)


def report_detail_api(request, pk):
    report = get_object_or_404(Report, pk=pk)

    data = {
        'id': report.id,
        'title': report.title,
        'category': report.category,
        'description': report.description,
        'location': report.location,
        'status': report.status,
    }

    return JsonResponse(data)