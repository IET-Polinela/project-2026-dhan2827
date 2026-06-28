from django.db.models import Q

from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound

from .models import Report
from .serializers import ReportSerializer

from usermanagement_24782034.models import CustomUser
from usermanagement_24782034.serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ReportPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ReportPagination

    def get_queryset(self):
        user = self.request.user
        tab = self.request.query_params.get('tab')

        queryset = Report.objects.all().order_by('-updated_at')

        if tab == 'my_reports':
            return queryset.filter(reporter=user)

        if tab == 'feed':
            return queryset.filter(
                ~Q(reporter=user),
                ~Q(status='DRAFT')
            )

        return queryset.filter(
            Q(reporter=user) | ~Q(status='DRAFT')
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    def perform_update(self, serializer):
        report = self.get_object()
        user = self.request.user

        if report.status == 'RESOLVED':
            raise PermissionDenied("Laporan yang sudah selesai tidak dapat diubah.")

        if not user.is_staff and not user.is_superuser:
            if report.reporter != user:
                raise NotFound()

            if report.status != 'DRAFT':
                raise PermissionDenied("Laporan yang sudah diajukan tidak dapat diedit.")

        serializer.save()