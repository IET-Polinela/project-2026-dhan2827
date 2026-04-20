from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages
from django.views.generic import DetailView

from .models import Report
from .forms import ReportForm


# 🔥 HOME
def home(request):
    return render(request, 'main_app/index.html')


# 🔥 LIST LAPORAN
class ReportListView(ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'


# 🔥 CREATE (TAMBAH DATA)
class ReportCreateView(CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil ditambahkan!")
        return super().form_valid(form)


# 🔥 UPDATE (EDIT DATA)
class ReportUpdateView(UpdateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil diperbarui!")
        return super().form_valid(form)


# 🔥 DELETE (HAPUS DATA)
class ReportDeleteView(DeleteView):
    model = Report
    template_name = 'main_app/delete_report.html'
    success_url = reverse_lazy('report_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Laporan berhasil dihapus!")
        return super().delete(request, *args, **kwargs)
    
class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/detail_report.html'
    context_object_name = 'report'


# 🔥 UPDATE STATUS (WORKFLOW + VALIDASI)
class ReportUpdateStatusView(View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')

        # 🔒 RULE WORKFLOW (sesuai soal)
        valid_transitions = {
            "REPORTED": "VERIFIED",
            "VERIFIED": "IN_PROGRESS",
            "IN_PROGRESS": "RESOLVED",
        }

        # ✅ VALIDASI PERUBAHAN STATUS
        if report.status in valid_transitions and valid_transitions[report.status] == new_status:
            report.status = new_status
            report.save()
            messages.success(request, "Status berhasil diperbarui!")
        else:
            messages.error(request, "Perubahan status tidak valid!")

        return redirect('report_list')