from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import RegisterView, ReportViewSet

router = DefaultRouter()
router.register(r'report', ReportViewSet, basename='report')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
]