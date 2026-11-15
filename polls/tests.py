from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Poll, Option, Vote

User = get_user_model()


class KararsizimFlowTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='ahmet_kararsiz',
            email='ahmet@example.com',
            password='Password123!'
        )

    def test_anonymous_redirected_from_poll_create(self):
        """Misafir anket açmaya çalıştığında giriş sayfasına yönlendirilmeli."""
        response = self.client.get(reverse('polls:create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_poll_create_success_with_options(self):
        """Üye kullanıcı 3 seçenekli anket oluşturabilmeli."""
        self.client.login(username='ahmet_kararsiz', password='Password123!')
        response = self.client.post(reverse('polls:create'), {
            'question': 'Akşam ne izlesem?',
            'options': ['Interstellar', 'Inception', 'The Dark Knight']
        })
        self.assertEqual(response.status_code, 302)
        poll = Poll.objects.first()
        self.assertIsNotNone(poll)
        self.assertEqual(poll.question, 'Akşam ne izlesem?')
        self.assertEqual(poll.creator.username, 'ahmet_kararsiz')
        self.assertEqual(poll.options.count(), 3)

    def test_poll_create_validation_min_max(self):
        """1 seçenek veya 6 seçenek verildiğinde anket açılmamalı."""
        self.client.login(username='ahmet_kararsiz', password='Password123!')
        # 1 seçenek (Hata vermeli)
        response = self.client.post(reverse('polls:create'), {
            'question': 'Tek seçenekli soru',
            'options': ['Yalnız Seçenek']
        })
        self.assertEqual(Poll.objects.count(), 0)

        # 6 seçenek (Hata vermeli)
        response = self.client.post(reverse('polls:create'), {
            'question': 'Çok seçenekli soru',
            'options': ['1', '2', '3', '4', '5', '6']
        })
        self.assertEqual(Poll.objects.count(), 0)

    def test_guest_voting_and_deduplication(self):
        """Misafir oy verebilmeli ve aynı ankete 2. kez oy verememeli."""
        poll = Poll.objects.create(creator=self.user, question='Kahve mi çay mı?')
        opt_kahve = Option.objects.create(poll=poll, text='Kahve')
        opt_cay = Option.objects.create(poll=poll, text='Çay')

        # Misafir ilk oyunu verir
        guest_client = Client()
        response = guest_client.post(reverse('polls:vote', kwargs={'pk': poll.pk}), {
            'option': opt_kahve.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(poll.total_votes, 1)
        self.assertEqual(opt_kahve.vote_count, 1)
        self.assertEqual(opt_kahve.vote_percentage(), 100.0)

        # Misafir aynı ankete 2. kez oy vermeyi dener
        response2 = guest_client.post(reverse('polls:vote', kwargs={'pk': poll.pk}), {
            'option': opt_cay.id
        })
        self.assertEqual(response2.status_code, 302)
        # Oy sayısı 1 olarak kalmalı
        self.assertEqual(poll.total_votes, 1)

    def test_authenticated_user_voting_and_deduplication(self):
        """Üye kullanıcı oy verebilmeli ve aynı ankete tekrar oy verememeli."""
        poll = Poll.objects.create(creator=self.user, question='Python mu Go mu?')
        opt_python = Option.objects.create(poll=poll, text='Python')
        opt_go = Option.objects.create(poll=poll, text='Go')

        self.client.login(username='ahmet_kararsiz', password='Password123!')
        response = self.client.post(reverse('polls:vote', kwargs={'pk': poll.pk}), {
            'option': opt_python.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(poll.total_votes, 1)
        self.assertEqual(opt_python.vote_count, 1)

        # Tekrar oy vermeyi dener
        response2 = self.client.post(reverse('polls:vote', kwargs={'pk': poll.pk}), {
            'option': opt_go.id
        })
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(poll.total_votes, 1)
