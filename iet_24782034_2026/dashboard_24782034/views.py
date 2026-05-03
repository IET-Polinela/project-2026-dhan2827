from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.db.models import Count
from main_app.models import Report
from django.shortcuts import redirect
from django.contrib import messages

class DashboardView(TemplateView):
    template_name = 'dashboard_24782034/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "Akses ditolak! Hanya admin.")
            return redirect('report_list')  # arahkan ke reports

        return super().dispatch(request, *args, **kwargs)


class DashboardDataView(View):
    def get(self, request, *args, **kwargs):
        status_data = (
            Report.objects
            .values('status')
            .annotate(total=Count('id'))
            .order_by('status')
        )

        category_data = (
            Report.objects
            .values('category')
            .annotate(total=Count('id'))
            .order_by('category')
        )

        latest_reported = Report.objects.filter(status='REPORTED').order_by('-id')[:5]
        latest_resolved = Report.objects.filter(status='RESOLVED').order_by('-id')[:5]

        data = {
            'status_labels': [item['status'] for item in status_data],
            'status_counts': [item['total'] for item in status_data],

            'category_labels': [item['category'] for item in category_data],
            'category_counts': [item['total'] for item in category_data],

            'latest_reported': [
                {
                    'title': report.title,
                    'category': report.category,
                    'location': report.location,
                    'status': report.status,
                }
                for report in latest_reported
            ],

            'latest_resolved': [
                {
                    'title': report.title,
                    'category': report.category,
                    'location': report.location,
                    'status': report.status,
                }
                for report in latest_resolved
            ],
        }

        return JsonResponse(data)