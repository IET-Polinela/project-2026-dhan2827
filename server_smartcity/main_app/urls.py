from django.urls import path

from .views import (
    home,
    DashboardView,
    ReportListView,
    MyReportListView,
    ReportDetailView,
    ReportCreateView,
    ReportUpdateView,
    ReportDeleteView,
    ReportUpdateStatusView,
    ReportSearchView,
    ReportDetailJsonView,
    report_detail_api,
)
from usermanagement_24782034.views import (
    CustomLoginView,
    CustomLogoutView
)


urlpatterns = [

    path('', home, name='home'),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('reports/', ReportListView.as_view(), name='report_list'),

    path(
        'my-reports/',
        MyReportListView.as_view(),
        name='my_reports'
    ),

    path(
        'reports/create/',
        ReportCreateView.as_view(),
        name='report_create'
    ),

    path(
        'reports/<int:pk>/edit/',
        ReportUpdateView.as_view(),
        name='report_update'
    ),

    path(
        'reports/<int:pk>/delete/',
        ReportDeleteView.as_view(),
        name='report_delete'
    ),

    path(
        'reports/<int:pk>/detail/',
        ReportDetailView.as_view(),
        name='report_detail'
    ),

    path(
        'reports/<int:pk>/update-status/',
        ReportUpdateStatusView.as_view(),
        name='update_status'
    ),

    path(
        'search/',
        ReportSearchView.as_view(),
        name='report_search'
    ),

    path(
        'detail-json/<int:pk>/',
        ReportDetailJsonView.as_view(),
        name='report_detail_json'
    ),
        # ALIAS UNTUK TEST ADDITIONAL
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    path(
        'reports/add/',
        ReportCreateView.as_view(),
        name='add_report'
    ),

    path(
        'reports/<int:pk>/update/',
        ReportUpdateView.as_view(),
        name='update_report'
    ),

    path(
        'reports/<int:pk>/remove/',
        ReportDeleteView.as_view(),
        name='delete_report'
    ),

    path(
        'report-detail-api/<int:pk>/',
        report_detail_api,
        name='report_detail_api'
    ),
]