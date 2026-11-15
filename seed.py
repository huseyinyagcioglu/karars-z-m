"""
Kararsızım projesi için örnek başlangıç verisi (seed script).
Çalıştırmak için: python seed.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from polls.models import Poll, Option

User = get_user_model()

def seed():
    print("🌱 Başlangıç verileri yükleniyor...")

    # Örnek kullanıcı
    user, created = User.objects.get_or_create(
        username='karar_avcisi',
        defaults={'email': 'avci@kararsizim.local'}
    )
    if created:
        user.set_password('karar1234')
        user.save()
        print(f"👤 Örnek kullanıcı oluşturuldu: @{user.username} (şifre: karar1234)")

    # Örnek Anket 1
    if not Poll.objects.filter(question="Bu akşam ne izlemeliyim?").exists():
        p1 = Poll.objects.create(creator=user, question="Bu akşam ne izlemeliyim?")
        Option.objects.create(poll=p1, text="Bilim Kurgu (Interstellar)")
        Option.objects.create(poll=p1, text="Polisiye / Gizem (Se7en)")
        Option.objects.create(poll=p1, text="Kafa dağıtacak bir komedi")
        print("🗳️ Anket 1 oluşturuldu.")

    # Örnek Anket 2
    if not Poll.objects.filter(question="Hafta sonu kahvaltısı için hangisi daha iyi?").exists():
        p2 = Poll.objects.create(creator=user, question="Hafta sonu kahvaltısı için hangisi daha iyi?")
        Option.objects.create(poll=p2, text="Evde sıcak menemen ve taze çay")
        Option.objects.create(poll=p2, text="Dışarıda serpme kahvaltı")
        print("🗳️ Anket 2 oluşturuldu.")

    print("✅ Başlangıç verileri başarıyla hazırlandı!")

if __name__ == '__main__':
    seed()
