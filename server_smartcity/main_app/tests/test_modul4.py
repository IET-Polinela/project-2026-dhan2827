from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from main_app.models import Report

User = get_user_model()


class CRUDAndValidationTests(APITestCase):
    def setUp(self):
        self.warga = User.objects.create_user(
            username='warga_crud',
            password='warga12345',
            is_admin=False,
        )
        self.client.force_authenticate(user=self.warga)

    def test_FT_01_buat_laporan_dengan_data_lengkap(self):
        url = reverse('report-list')

        payload = {
            'title': 'Lampu Jalan Mati',
            'category': 'Fasilitas Umum',
            'description': 'Lampu jalan dekat gerbang kampus mati total.',
            'location': 'Gerbang Kampus',
            'status': 'DRAFT',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "POST laporan valid harus menghasilkan HTTP 201 Created",
        )

        self.assertEqual(response.data['title'], payload['title'])

        laporan = Report.objects.get(id=response.data['id'])
        self.assertEqual(laporan.reporter, self.warga)

    def test_FT_02_ditolak_jika_judul_kosong(self):
        url = reverse('report-list')

        payload = {
            'category': 'Infrastruktur',
            'description': 'Deskripsi ada, tapi title sengaja tidak dikirim.',
            'location': 'Area Kampus',
            'status': 'DRAFT',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "POST tanpa title harus ditolak",
        )
        self.assertIn('title', response.data)

    def test_FT_03_ditolak_jika_deskripsi_kosong(self):
        url = reverse('report-list')

        payload = {
            'title': 'Laporan Tanpa Deskripsi',
            'category': 'Infrastruktur',
            'location': 'Area Kampus',
            'status': 'DRAFT',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "POST tanpa description harus ditolak",
        )
        self.assertIn('description', response.data)

    def test_FT_04_xss_script_disimpan_sebagai_string_literal(self):
        url = reverse('report-list')

        kode_xss = '<script>alert("xss")</script>'
        payload = {
            'title': 'Laporan XSS Test',
            'category': 'Keamanan',
            'description': kode_xss,
            'location': 'Lab Keamanan Siber',
            'status': 'DRAFT',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Data dengan karakter HTML harus tetap diterima oleh API",
        )

        laporan = Report.objects.get(title='Laporan XSS Test')
        self.assertIn('script', laporan.description.lower())
