from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsFlowTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registration_success(self):
        """Kullanıcı adı, email ve şifre ile başarıyla kayıt olmalı ve oturum açmalı."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'yeni_kullanici',
            'email': 'yeni@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='yeni_kullanici').exists())
        user = User.objects.get(username='yeni_kullanici')
        self.assertEqual(user.email, 'yeni@example.com')

    def test_duplicate_username_fails(self):
        """Daha önce alınmış kullanıcı adı seçilememeli."""
        User.objects.create_user(username='mevcut_kullanici', email='mevcut@example.com', password='123')
        response = self.client.post(reverse('accounts:register'), {
            'username': 'mevcut_kullanici',
            'email': 'baska@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Bu kullanıcı adı zaten alınmış", response.content.decode('utf-8'))

    def test_duplicate_email_fails(self):
        """Daha önce kayıtlı e-posta adresi seçilememeli."""
        User.objects.create_user(username='kullanici1', email='ayni@example.com', password='123')
        response = self.client.post(reverse('accounts:register'), {
            'username': 'kullanici2',
            'email': 'ayni@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Bu e-posta adresi ile kayıtlı bir hesap zaten var", response.content.decode('utf-8'))

    def test_login_and_logout(self):
        """Giriş yapma ve çıkış yapma akışı."""
        User.objects.create_user(username='test_user', email='test@example.com', password='Password123!')
        login_res = self.client.post(reverse('accounts:login'), {
            'username': 'test_user',
            'password': 'Password123!',
        })
        self.assertEqual(login_res.status_code, 302)

        logout_res = self.client.get(reverse('accounts:logout'))
        self.assertEqual(logout_res.status_code, 302)
