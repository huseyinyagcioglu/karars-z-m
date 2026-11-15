from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Poll(models.Model):
    """Kullanıcıların oluşturduğu anket sorusu."""
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='polls',
        verbose_name="Oluşturan Kullanıcı"
    )
    question = models.CharField(
        max_length=255,
        verbose_name="Soru / Kararsızlık"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Anket"
        verbose_name_plural = "Anketler"

    def __str__(self):
        return self.question

    @property
    def total_votes(self):
        return self.votes.count()

    def clean(self):
        super().clean()
        if self.pk:
            count = self.options.count()
            if count < 2 or count > 5:
                raise ValidationError("Bir ankette en az 2, en çok 5 seçenek bulunmalıdır.")


class Option(models.Model):
    """Ankete ait seçenekler (En az 2, en çok 5 adet)."""
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="Bağlı Olduğu Anket"
    )
    text = models.CharField(
        max_length=150,
        verbose_name="Seçenek Metni"
    )

    class Meta:
        verbose_name = "Seçenek"
        verbose_name_plural = "Seçenekler"

    def __str__(self):
        return f"{self.poll.question[:30]}... -> {self.text}"

    @property
    def vote_count(self):
        return self.votes.count()

    def vote_percentage(self):
        total = self.poll.total_votes
        if total == 0:
            return 0
        return round((self.vote_count / total) * 100, 1)


class Vote(models.Model):
    """
    Anket oyu.
    - Üye olan kullanıcılar için: user dolu, session_key opsiyonel.
    - Misafirler için: user boş (null), session_key dolu.
    """
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name="Anket"
    )
    option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name="Verilen Oy Seçeneği"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='votes',
        verbose_name="Kullanıcı (Üye ise)"
    )
    session_key = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="Misafir Oturum Anahtarı"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oy Tarihi")

    class Meta:
        verbose_name = "Oy"
        verbose_name_plural = "Oylar"
        constraints = [
            # Bir üye aynı ankete yalnızca bir kez oy verebilir
            models.UniqueConstraint(
                fields=['poll', 'user'],
                condition=models.Q(user__isnull=False),
                name='unique_vote_per_user_per_poll'
            ),
            # Bir misafir (oturum anahtarı ile) aynı ankete yalnızca bir kez oy verebilir
            models.UniqueConstraint(
                fields=['poll', 'session_key'],
                condition=models.Q(session_key__isnull=False),
                name='unique_vote_per_session_per_poll'
            ),
        ]

    def __str__(self):
        voter = self.user.username if self.user else f"Misafir ({self.session_key[:8]})"
        return f"{voter} -> {self.option.text}"
