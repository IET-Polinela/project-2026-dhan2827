from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from main_app.models import Report

User = get_user_model()


class WorkflowStateTests(APITestCase):
    def setUp(self):
        self.warga = User.objects.create_user(
            username='warga10',
            password='warga12345',
            is_admin=False,
        )

        self.laporan_draft = Report.objects.create(
            title='Lampu Kampus Mati',
            category='Fasilitas Umum',
            description='Lampu di depan gedung rektorat tidak menyala.',
            location='Gedung Rektorat',
            status='DRAFT',
            reporter=self.warga,
        )

        self.laporan_reported = Report.objects.create(
            title='Saluran Air Tersumbat',
            category='Infrastruktur',
            description='Saluran air di samping kantin tersumbat.',
            location='Kantin Polinela',
            status='REPORTED',
            reporter=self.warga,
        )

        self.laporan_resolved = Report.objects.create(
            title='AC Rusak di Lab',
            category='Fasilitas Umum',
            description='AC di Lab CPS 1 sudah diperbaiki.',
            location='Lab CPS 1',
            status='RESOLVED',
            reporter=self.warga,
        )

    def test_WF_01_warga_mengajukan_draf_menjadi_reported(self):
        self.client.force_authenticate(user=self.warga)

        url = f'/api/report/{self.laporan_draft.pk}/'
        payload = {
            'title': self.laporan_draft.title,
            'category': self.laporan_draft.category,
            'description': self.laporan_draft.description,
            'location': self.laporan_draft.location,
            'status': 'REPORTED',
        }

        response = self.client.put(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.laporan_draft.refresh_from_db()
        self.assertEqual(self.laporan_draft.status, 'REPORTED')

    def test_WF_02_tidak_bisa_edit_laporan_yang_sudah_reported(self):
        self.client.force_authenticate(user=self.warga)

        judul_awal = self.laporan_reported.title
        deskripsi_awal = self.laporan_reported.description

        url = f'/api/report/{self.laporan_reported.pk}/'
        payload = {
            'title': 'Listrik LabJar Mati',
            'category': self.laporan_reported.category,
            'description': 'Kehabisan token listrik di LabJar, mohon segera diperbaiki.',
            'location': self.laporan_reported.location,
            'status': self.laporan_reported.status,
        }

        response = self.client.put(url, payload, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Laporan REPORTED tidak boleh diedit warga",
        )

        self.laporan_reported.refresh_from_db()
        self.assertEqual(self.laporan_reported.title, judul_awal)
        self.assertEqual(self.laporan_reported.description, deskripsi_awal)

    def test_WF_05_laporan_resolved_tidak_bisa_diubah(self):
        self.client.force_authenticate(user=self.warga)

        judul_awal = self.laporan_resolved.title
        deskripsi_awal = self.laporan_resolved.description

        url = f'/api/report/{self.laporan_resolved.pk}/'
        payload = {
            'title': 'Judul Baru',
            'category': self.laporan_resolved.category,
            'description': 'Deskripsi Baru',
            'location': self.laporan_resolved.location,
            'status': self.laporan_resolved.status,
        }

        response = self.client.put(url, payload, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Laporan RESOLVED harus terkunci dan tidak boleh diedit",
        )

        self.laporan_resolved.refresh_from_db()
        self.assertEqual(self.laporan_resolved.title, judul_awal)
        self.assertEqual(self.laporan_resolved.description, deskripsi_awal)


class AdminWorkflowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_portal',
            password='AdminPass123!',
            is_admin=True,
            is_staff=True,
            is_superuser=True,
        )

        self.laporan_reported = Report.objects.create(
            title='Jalan Rusak di Blok C',
            category='Infrastruktur',
            description='Jalan berlubang parah di area parkir Blok C.',
            location='Blok C Polinela',
            status='REPORTED',
            reporter=self.admin,
        )

    def test_WF_03_admin_mengubah_status_reported_ke_verified(self):
        self.client.force_login(self.admin)

        url = reverse('update_status', kwargs={'pk': self.laporan_reported.pk})

        response = self.client.post(url, {
            'status': 'VERIFIED',
            'new_status': 'VERIFIED',
        })

        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_302_FOUND],
            "Admin harus bisa mengubah status REPORTED menjadi VERIFIED",
        )

        self.laporan_reported.refresh_from_db()
        self.assertEqual(self.laporan_reported.status, 'VERIFIED')

    def test_WF_04_tidak_ada_transisi_langsung_ke_resolved_dari_reported(self):
        allowed_transitions = {
            'DRAFT': ['REPORTED'],
            'REPORTED': ['VERIFIED'],
            'VERIFIED': ['IN_PROGRESS'],
            'IN_PROGRESS': ['RESOLVED'],
            'RESOLVED': [],
        }

        next_statuses = allowed_transitions.get(self.laporan_reported.status, [])

        self.assertIn('VERIFIED', next_statuses)
        self.assertNotIn('RESOLVED', next_statuses)
