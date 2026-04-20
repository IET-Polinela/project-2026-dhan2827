from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),

    path('reports/', ReportListView.as_view(), name='report_list'),
    path('reports/create/', ReportCreateView.as_view(), name='report_create'),
    path('reports/<int:pk>/edit/', ReportUpdateView.as_view(), name='report_update'),
    path('reports/<int:pk>/delete/', ReportDeleteView.as_view(), name='report_delete'),
    path('reports/<int:pk>/detail/', ReportDetailView.as_view(), name='report_detail'),
    path('reports/<int:pk>/update-status/', ReportUpdateStatusView.as_view(), name='update_status'),
]