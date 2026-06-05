from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

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


# LIST LAPORAN (boleh untuk semua user)
class ReportListView(ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'


# DETAIL LAPORAN (boleh untuk semua user)
class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/detail_report.html'
    context_object_name = 'report'


# CREATE (ADMIN ONLY)
class ReportCreateView(AdminRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil ditambahkan!")
        return super().form_valid(form)


# UPDATE (ADMIN ONLY)
class ReportUpdateView(AdminRequiredMixin, UpdateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil diperbarui!")
        return super().form_valid(form)


# DELETE (ADMIN ONLY)
class ReportDeleteView(AdminRequiredMixin, DeleteView):
    model = Report
    template_name = 'main_app/delete_report.html'
    success_url = reverse_lazy('report_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Laporan berhasil dihapus!")
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

        reports = Report.objects.filter(
            Q(title__icontains=keyword) |
            Q(category__icontains=keyword) |
            Q(status__icontains=keyword) |
            Q(location__icontains=keyword)
        ).order_by('-id')

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
    
class ReportSearchView(View):
    def get(self, request):
        keyword = request.GET.get('q', '')

        reports = Report.objects.filter(
            Q(title__icontains=keyword) |
            Q(location__icontains=keyword) |
            Q(status__icontains=keyword) |
            Q(category__icontains=keyword)
        ).order_by('-id')

        data = []

        for report in reports:
            data.append({
                'id': report.id,
                'title': report.title,
                'location': report.location,
                'status': report.status,
                'category': report.category,
            })

        return JsonResponse({'reports': data})