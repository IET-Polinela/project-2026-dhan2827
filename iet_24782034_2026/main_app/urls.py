from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/add/', views.add_report, name='add_report'),
]