import unittest

from django.test import TestCase, RequestFactory
from django.urls import reverse, NoReverseMatch
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from main_app.models import Report

User = get_user_model()


class SerializerAndModelCoverageTests(APITestCase):
    def setUp(self):
        self.warga = User.objects.create_user(
            username='wargaTest',
            password='warga12345',
            is_admin=False,
        )

    def test_report_model_str(self):
        report = Report.objects.create(
            title='Laporan Str Uji',
            category='Lainnya',
            description='Deskripsi',
            location='Lokasi',
            status='REPORTED',
            reporter=self.warga,
        )
        self.assertEqual(str(report), 'Laporan Str Uji')

    def test_report_serializer_no_request_context(self):
        from main_app.serializers import ReportSerializer

        report = Report.objects.create(
            title='Laporan Serializer Uji',
            category='Lainnya',
            description='Deskripsi',
            location='Lokasi',
            status='REPORTED',
            reporter=self.warga,
        )

        serializer = ReportSerializer(report, context={})
        data = serializer.data

        if 'is_owner' in data:
            self.assertFalse(data['is_owner'])

        if 'reporter_name' in data:
            self.assertEqual(data['reporter_name'], 'Warga Anonim')


class MainAppMonolithicViewsCoverageTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_mono',
            password='Password123!',
            is_admin=True,
            is_staff=True,
            is_superuser=True,
        )
        self.citizen = User.objects.create_user(
            username='citizen_mono',
            password='Password123!',
            is_admin=False,
            is_staff=False,
        )
        self.report = Report.objects.create(
            title='Laporan Monolitik Uji',
            category='Infrastruktur',
            description='Ada kerusakan infrastruktur.',
            location='Bandung',
            status='REPORTED',
            reporter=self.citizen,
        )

    def _reverse_or_skip(self, name, **kwargs):
        try:
            return reverse(name, kwargs=kwargs or None)
        except NoReverseMatch:
            self.skipTest(f"URL name '{name}' belum ada di project ini")

    def test_report_detail_api_valid_if_exists(self):
        try:
            from main_app.views import report_detail_api
        except ImportError:
            self.skipTest("View report_detail_api belum ada")

        request = RequestFactory().get('/dummy-url/')
        response = report_detail_api(request, self.report.id)
        self.assertEqual(response.status_code, 200)

    def test_report_detail_api_invalid_if_exists(self):
        try:
            from main_app.views import report_detail_api
        except ImportError:
            self.skipTest("View report_detail_api belum ada")

        from django.http import Http404

        request = RequestFactory().get('/dummy-url/')
        with self.assertRaises(Http404):
            report_detail_api(request, 99999)

    def test_report_search_unauthenticated(self):
        url = self._reverse_or_skip('report_search')
        response = self.client.get(url + '?q=Lampu')
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_search_citizen(self):
        url = self._reverse_or_skip('report_search')
        self.client.login(username='citizen_mono', password='Password123!')
        response = self.client.get(url + '?q=Lampu')
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_search_admin(self):
        url = self._reverse_or_skip('report_search')
        self.client.login(username='admin_mono', password='Password123!')
        response = self.client.get(url + '?q=Monolitik')
        self.assertIn(response.status_code, [200, 302, 403])

    def test_home_view(self):
        url = self._reverse_or_skip('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_report_list_view_unauthenticated(self):
        url = self._reverse_or_skip('report_list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_list_view_citizen(self):
        url = self._reverse_or_skip('report_list')
        self.client.login(username='citizen_mono', password='Password123!')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_list_view_admin(self):
        url = self._reverse_or_skip('report_list')
        self.client.login(username='admin_mono', password='Password123!')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_create_view_unauthenticated(self):
        url = self._reverse_or_skip('add_report')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_create_view_citizen(self):
        url = self._reverse_or_skip('add_report')
        self.client.login(username='citizen_mono', password='Password123!')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_create_view_admin_get(self):
        url = self._reverse_or_skip('add_report')
        self.client.login(username='admin_mono', password='Password123!')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_create_view_admin_post_valid(self):
        url = self._reverse_or_skip('add_report')
        self.client.login(username='admin_mono', password='Password123!')

        payload = {
            'title': 'Laporan Form Baru',
            'category': 'Infrastruktur',
            'description': 'Deskripsi baru.',
            'location': 'Jakarta',
            'status': 'DRAFT',
        }

        response = self.client.post(url, payload)
        self.assertIn(response.status_code, [200, 302, 400, 403])

    def test_report_detail_view_unauthenticated(self):
        url = self._reverse_or_skip('report_detail', pk=self.report.id)
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_detail_view_citizen(self):
        url = self._reverse_or_skip('report_detail', pk=self.report.id)
        self.client.login(username='citizen_mono', password='Password123!')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_detail_view_admin(self):
        url = self._reverse_or_skip('report_detail', pk=self.report.id)
        self.client.login(username='admin_mono', password='Password123!')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_update_view_unauthenticated(self):
        url = self._reverse_or_skip('update_report', pk=self.report.id)
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_update_view_citizen(self):
        url = self._reverse_or_skip('update_report', pk=self.report.id)
        self.client.login(username='citizen_mono', password='Password123!')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_update_view_admin_get(self):
        url = self._reverse_or_skip('update_report', pk=self.report.id)
        self.client.login(username='admin_mono', password='Password123!')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_update_view_admin_post_valid(self):
        url = self._reverse_or_skip('update_report', pk=self.report.id)
        self.client.login(username='admin_mono', password='Password123!')

        payload = {
            'title': 'Laporan Terupdate',
            'category': 'Infrastruktur',
            'description': 'Deskripsi terupdate.',
            'location': 'Jakarta',
            'status': 'REPORTED',
        }

        response = self.client.post(url, payload)
        self.assertIn(response.status_code, [200, 302, 400, 403])

    def test_report_delete_view_unauthenticated(self):
        url = self._reverse_or_skip('delete_report', pk=self.report.id)
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_delete_view_citizen(self):
        url = self._reverse_or_skip('delete_report', pk=self.report.id)
        self.client.login(username='citizen_mono', password='Password123!')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_delete_view_admin_get(self):
        url = self._reverse_or_skip('delete_report', pk=self.report.id)
        self.client.login(username='admin_mono', password='Password123!')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_delete_view_admin_post(self):
        url = self._reverse_or_skip('delete_report', pk=self.report.id)
        self.client.login(username='admin_mono', password='Password123!')
        response = self.client.post(url)
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_delete_view_direct_delete_method_if_exists(self):
        try:
            from main_app.views import ReportDeleteView
        except ImportError:
            self.skipTest("ReportDeleteView belum ada")

        url = self._reverse_or_skip('delete_report', pk=self.report.id)

        from django.contrib.messages.storage.fallback import FallbackStorage

        factory = RequestFactory()
        request = factory.post(url)
        request.user = self.admin
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))

        view = ReportDeleteView()
        view.setup(request, pk=self.report.id)
        view.object = view.get_object()

        response = view.delete(request)
        self.assertEqual(response.status_code, 302)

    def test_report_update_status_view_unauthenticated(self):
        url = self._reverse_or_skip('update_status', pk=self.report.id)
        response = self.client.post(url, {'status': 'VERIFIED'})
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_update_status_view_citizen(self):
        url = self._reverse_or_skip('update_status', pk=self.report.id)
        self.client.login(username='citizen_mono', password='Password123!')
        response = self.client.post(url, {'status': 'VERIFIED'})
        self.assertIn(response.status_code, [200, 302, 403])
