from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/add/', views.add_report, name='add_report'),

    path('reports/edit/<int:id>/', views.edit_report, name='edit_report'),
    path('reports/delete/<int:id>/', views.delete_report, name='delete_report'),
]