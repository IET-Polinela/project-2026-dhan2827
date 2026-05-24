from rest_framework import viewsets, permissions
from .models import Report
from .serializers import ReportSerializer
from .permissions import IsOwnerAndDraftOrReadOnly


class ReportViewSet(viewsets.ModelViewSet):

    serializer_class = ReportSerializer

    def get_queryset(self):

        user = self.request.user

        # ADMIN
        if user.is_superuser:
            return Report.objects.exclude(
                status='DRAFT'
            )

        # CITIZEN
        return Report.objects.filter(
            reporter=user
        )
    
    def get_permissions(self):

        if self.action in ['update', 'partial_update', 'destroy']:
            return [
                permissions.IsAuthenticated(),
                IsOwnerAndDraftOrReadOnly()
            ]

        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):

        # reporter otomatis dari user login JWT
        serializer.save(reporter=self.request.user)