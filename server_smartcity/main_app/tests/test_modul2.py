from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from main_app.models import Report

User = get_user_model()


class PrivacyAndDataHidingTests(APITestCase):
    def setUp(self):
        self.warga_a = User.objects.create_user(
            username='warga_a',
            password='TestPass123!',
            is_admin=False,
        )
        self.warga_b = User.objects.create_user(
            username='warga_b',
            password='TestPass123!',
            is_admin=False,
        )

        self.draft_milik_b = Report.objects.create(
            title='Draf Rahasia Warga B',
            category='Infrastruktur',
            description='Ini adalah draf yang belum diajukan.',
            location='Lokasi Rahasia',
            status='DRAFT',
            reporter=self.warga_b,
        )

        self.laporan_publik_a = Report.objects.create(
            title='Jalan Berlubang di Depan Kampus',
            category='Infrastruktur',
            description='Ada lubang besar yang membahayakan pengendara.',
            location='Jl. Soekarno Hatta',
            status='REPORTED',
            reporter=self.warga_a,
        )

        self.laporan_publik_b = Report.objects.create(
            title='Sampah Menumpuk di Trotoar',
            category='Kebersihan',
            description='Sampah tidak diangkut selama seminggu.',
            location='Jl. Gatot Subroto',
            status='REPORTED',
            reporter=self.warga_b,
        )

    def _get_results(self, response):
        data = response.data
        if isinstance(data, dict) and 'results' in data:
            return data['results']
        return data

    def test_PRIV_01_feed_kota_menyembunyikan_identitas_reporter(self):
        self.client.force_authenticate(user=self.warga_a)

        response = self.client.get('/api/report/?tab=feed')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self._get_results(response)
        self.assertTrue(len(results) > 0, "Feed kota seharusnya memiliki minimal 1 laporan")

        for laporan in results:
            self.assertEqual(
                laporan['reporter'],
                'Warga Anonim',
                f"Laporan '{laporan['title']}' harus menampilkan reporter sebagai Warga Anonim",
            )

    def test_PRIV_02_laporan_saya_menampilkan_nama_asli(self):
        self.client.force_authenticate(user=self.warga_a)

        response = self.client.get('/api/report/?tab=my_reports')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self._get_results(response)
        self.assertTrue(len(results) > 0, "Harus ada laporan milik Warga A")

        for laporan in results:
            self.assertIn('reporter_name', laporan)
            self.assertEqual(
                laporan['reporter_name'],
                'warga_a',
                "Pada tab my_reports, reporter_name harus menampilkan username asli pemilik",
            )

    def test_PRIV_03_tidak_bisa_baca_draf_orang_lain(self):
        self.client.force_authenticate(user=self.warga_a)

        url = f'/api/report/{self.draft_milik_b.pk}/'
        response = self.client.get(url, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Warga A tidak boleh melihat draf milik Warga B",
        )

    def test_PRIV_04_tidak_bisa_modifikasi_draf_orang_lain(self):
        self.client.force_authenticate(user=self.warga_a)

        judul_awal = self.draft_milik_b.title
        deskripsi_awal = self.draft_milik_b.description

        url = f'/api/report/{self.draft_milik_b.pk}/'
        payload = {
            'title': 'Judul Dicoba Diubah',
            'category': self.draft_milik_b.category,
            'description': 'Isi draf dicoba diubah oleh orang lain',
            'location': self.draft_milik_b.location,
            'status': self.draft_milik_b.status,
        }

        response = self.client.put(url, payload, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Warga A tidak boleh memodifikasi draf milik Warga B",
        )

        self.draft_milik_b.refresh_from_db()
        self.assertEqual(self.draft_milik_b.title, judul_awal)
        self.assertEqual(self.draft_milik_b.description, deskripsi_awal)
