from django.urls import path
from django.urls import path
from .views import *
from usermanagement_24782034.views import CustomLoginView, CustomLogoutView 
from .views import *

urlpatterns = [
    path('', home, name='home'),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('reports/', ReportListView.as_view(), name='report_list'),
    path('reports/create/', ReportCreateView.as_view(), name='report_create'),
    path('reports/<int:pk>/edit/', ReportUpdateView.as_view(), name='report_update'),
    path('reports/<int:pk>/delete/', ReportDeleteView.as_view(), name='report_delete'),
    path('reports/<int:pk>/detail/', ReportDetailView.as_view(), name='report_detail'),
    path('reports/<int:pk>/update-status/', ReportUpdateStatusView.as_view(), name='update_status'),
]