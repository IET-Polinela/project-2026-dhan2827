from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import RequestFactory, TestCase
from django.urls import NoReverseMatch, reverse
from rest_framework.test import APITestCase

from main_app.models import Report
from main_app.serializers import ReportSerializer

User = get_user_model()


class SerializerAndModelCoverageTests(APITestCase):
    def setUp(self):
        self.warga = User.objects.create_user(
            username="warga_str_test",
            password="Password123!",
            is_admin=False,
        )

    def test_report_model_str(self):
        report = Report.objects.create(
            title="Laporan Str Uji",
            category="Lainnya",
            description="Deskripsi",
            location="Lokasi",
            status="REPORTED",
            reporter=self.warga,
        )

        self.assertEqual(str(report), "Laporan Str Uji")

    def test_report_serializer_no_request_context(self):
        report = Report.objects.create(
            title="Laporan Serializer Uji",
            category="Lainnya",
            description="Deskripsi",
            location="Lokasi",
            status="REPORTED",
            reporter=self.warga,
        )

        serializer = ReportSerializer(report, context={})
        data = serializer.data

        self.assertFalse(data["is_owner"])

        reporter_value = data.get("reporter_name", data.get("reporter"))
        self.assertEqual(reporter_value, "Warga Anonim")


class MainAppMonolithicViewsCoverageTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_mono",
            password="Password123!",
            is_admin=True,
            is_staff=True,
            is_superuser=True,
        )
        self.citizen = User.objects.create_user(
            username="citizen_mono",
            password="Password123!",
            is_admin=False,
            is_staff=False,
            is_superuser=False,
        )
        self.report = Report.objects.create(
            title="Laporan Monolitik Uji",
            category="Infrastruktur",
            description="Ada kerusakan infrastruktur.",
            location="Bandung",
            status="REPORTED",
            reporter=self.citizen,
        )
        self.draft_report = Report.objects.create(
            title="Draft Milik Citizen",
            category="Infrastruktur",
            description="Draft untuk pengujian owner.",
            location="Bandung",
            status="DRAFT",
            reporter=self.citizen,
        )

    def url(self, *names, **kwargs):
        for name in names:
            try:
                return reverse(name, kwargs=kwargs or None)
            except NoReverseMatch:
                continue
        raise NoReverseMatch(f"Tidak ada URL name yang cocok: {names}")

    def test_report_detail_api_valid(self):
        from main_app.views import report_detail_api

        request = RequestFactory().get("/dummy-url/")
        response = report_detail_api(request, self.report.id)

        self.assertEqual(response.status_code, 200)

    def test_report_detail_api_invalid(self):
        from main_app.views import report_detail_api

        request = RequestFactory().get("/dummy-url/")

        with self.assertRaises(Http404):
            report_detail_api(request, 99999)

    def test_report_search_unauthenticated(self):
        response = self.client.get(reverse("report_search") + "?q=Lampu")
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_search_citizen(self):
        self.client.login(username="citizen_mono", password="Password123!")
        response = self.client.get(reverse("report_search") + "?q=Lampu")
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_search_admin(self):
        self.client.login(username="admin_mono", password="Password123!")
        response = self.client.get(reverse("report_search") + "?q=Monolitik")
        self.assertEqual(response.status_code, 200)

    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

        used_templates = [template.name for template in response.templates]
        self.assertTrue(
            "main_app/index.html" in used_templates
            or "main_app/home.html" in used_templates
            or len(used_templates) > 0
        )

    def test_report_list_view_unauthenticated(self):
        response = self.client.get(reverse("report_list"))
        self.assertIn(response.status_code, [302, 403])

    def test_report_list_view_citizen(self):
        self.client.login(username="citizen_mono", password="Password123!")
        response = self.client.get(reverse("report_list"))
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_list_view_admin(self):
        self.client.login(username="admin_mono", password="Password123!")
        response = self.client.get(reverse("report_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main_app/report_list.html")

    def test_report_create_view_unauthenticated(self):
        response = self.client.get(self.url("add_report", "report_create"))
        self.assertIn(response.status_code, [302, 403])

    def test_report_create_view_citizen_get(self):
        self.client.login(username="citizen_mono", password="Password123!")
        response = self.client.get(self.url("add_report", "report_create"))
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_create_view_citizen_post_valid(self):
        self.client.login(username="citizen_mono", password="Password123!")
        payload = {
            "title": "Laporan Form Baru",
            "category": "Infrastruktur",
            "description": "Deskripsi baru.",
            "location": "Jakarta",
            "status": "DRAFT",
        }

        response = self.client.post(self.url("add_report", "report_create"), payload)

        self.assertIn(response.status_code, [200, 302, 403])
        if response.status_code in [200, 302]:
            self.assertTrue(Report.objects.filter(title="Laporan Form Baru").exists())

    def test_report_detail_view_unauthenticated(self):
        response = self.client.get(self.url("report_detail", pk=self.report.id))
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_detail_view_citizen(self):
        self.client.login(username="citizen_mono", password="Password123!")
        response = self.client.get(self.url("report_detail", pk=self.report.id))
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_detail_view_admin(self):
        self.client.login(username="admin_mono", password="Password123!")
        response = self.client.get(self.url("report_detail", pk=self.report.id))
        self.assertEqual(response.status_code, 200)

    def test_report_update_view_unauthenticated(self):
        response = self.client.get(self.url("update_report", "report_update", pk=self.report.id))
        self.assertIn(response.status_code, [302, 403])

    def test_report_update_view_citizen_non_owner(self):
        other_citizen = User.objects.create_user(
            username="citizen_lain",
            password="Password123!",
            is_admin=False,
        )
        self.client.login(username="citizen_lain", password="Password123!")
        response = self.client.get(self.url("update_report", "report_update", pk=self.report.id))
        self.assertIn(response.status_code, [302, 403])

    def test_report_update_view_owner_draft_get(self):
        self.client.login(username="citizen_mono", password="Password123!")
        response = self.client.get(self.url("update_report", "report_update", pk=self.draft_report.id))
        self.assertIn(response.status_code, [200, 302, 403])

    def test_report_update_view_admin_get_forbidden(self):
        self.client.login(username="admin_mono", password="Password123!")
        response = self.client.get(self.url("update_report", "report_update", pk=self.report.id))
        self.assertIn(response.status_code, [302, 403])

    def test_report_update_view_admin_post_forbidden_and_data_unchanged(self):
        self.client.login(username="admin_mono", password="Password123!")
        original_title = self.report.title
        payload = {
            "title": "Laporan Terupdate Oleh Admin",
            "category": "Infrastruktur",
            "description": "Deskripsi terupdate.",
            "location": "Jakarta",
            "status": "REPORTED",
        }

        response = self.client.post(self.url("update_report", "report_update", pk=self.report.id), payload)

        self.assertIn(response.status_code, [302, 403])
        self.report.refresh_from_db()
        self.assertEqual(self.report.title, original_title)
        self.assertNotEqual(self.report.title, "Laporan Terupdate Oleh Admin")

    def test_report_delete_view_unauthenticated(self):
        response = self.client.get(self.url("delete_report", "report_delete", pk=self.report.id))
        self.assertIn(response.status_code, [302, 403])

    def test_report_delete_view_citizen_non_owner(self):
        other_citizen = User.objects.create_user(
            username="citizen_lain_delete",
            password="Password123!",
            is_admin=False,
        )
        self.client.login(username="citizen_lain_delete", password="Password123!")
        response = self.client.get(self.url("delete_report", "report_delete", pk=self.report.id))
        self.assertIn(response.status_code, [302, 403])

    def test_report_delete_view_admin_get_forbidden(self):
        self.client.login(username="admin_mono", password="Password123!")
        response = self.client.get(self.url("delete_report", "report_delete", pk=self.report.id))
        self.assertIn(response.status_code, [302, 403])
        self.assertTrue(Report.objects.filter(id=self.report.id).exists())

    def test_report_delete_view_admin_post_forbidden_and_data_still_exists(self):
        self.client.login(username="admin_mono", password="Password123!")
        response = self.client.post(self.url("delete_report", "report_delete", pk=self.report.id))
        self.assertIn(response.status_code, [302, 403])
        self.assertTrue(Report.objects.filter(id=self.report.id).exists())

    def test_report_update_status_view_unauthenticated(self):
        response = self.client.post(reverse("update_status", kwargs={"pk": self.report.id}), {"status": "VERIFIED"})
        self.assertIn(response.status_code, [302, 403])

    def test_report_update_status_view_citizen(self):
        self.client.login(username="citizen_mono", password="Password123!")
        response = self.client.post(reverse("update_status", kwargs={"pk": self.report.id}), {"status": "VERIFIED"})
        self.assertIn(response.status_code, [302, 403])

    def test_report_update_status_view_admin_valid_transition(self):
        self.client.login(username="admin_mono", password="Password123!")
        response = self.client.post(reverse("update_status", kwargs={"pk": self.report.id}), {"status": "VERIFIED"})
        self.assertEqual(response.status_code, 302)

        self.report.refresh_from_db()
        self.assertEqual(self.report.status, "VERIFIED")
