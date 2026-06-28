from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.warga = User.objects.create_user(
            username='warga',
            password='warga12345',
            is_admin=False,
        )

        self.admin = User.objects.create_user(
            username='admin',
            password='dhani123A',
            is_admin=True,
            is_staff=True,
            is_superuser=True,
        )

    def test_AUTH_01_login_warga_dengan_kredensial_valid(self):
        url = reverse('token_obtain_pair')
        payload = {
            'username': 'warga',
            'password': 'warga12345',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_AUTH_02_login_warga_dengan_password_salah(self):
        url = reverse('token_obtain_pair')
        payload = {
            'username': 'warga',
            'password': 'passwordSALAH',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)

    def test_AUTH_03_warga_tidak_bisa_akses_halaman_admin(self):
        login_berhasil = self.client.login(
            username='warga',
            password='warga12345',
        )
        self.assertTrue(login_berhasil)

        response = self.client.get('/dashboard/')

        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_302_FOUND],
            "Warga biasa tidak boleh bisa masuk dashboard admin",
        )
