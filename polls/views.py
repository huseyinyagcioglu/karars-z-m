from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError
from .models import Poll, Option, Vote
from .forms import PollCreateForm


def get_user_vote(poll, request):
    """Kullanıcının (üye veya misafir) bu ankette kullandığı oyu döner."""
    if request.user.is_authenticated:
        return Vote.objects.filter(poll=poll, user=request.user).first()
    elif request.session.session_key:
        return Vote.objects.filter(poll=poll, session_key=request.session.session_key).first()
    return None


def feed_view(request):
    """Tüm anketlerin listelendiği ana sayfa / akış."""
    # Misafir oturumunu başlat
    if not request.session.session_key:
        request.session.save()

    polls = Poll.objects.filter(is_active=True).select_related('creator').prefetch_related('options', 'votes')

    # Kullanıcının oy verdiği anket id'lerini topla
    voted_poll_ids = set()
    if request.user.is_authenticated:
        voted_poll_ids = set(Vote.objects.filter(user=request.user).values_list('poll_id', flat=True))
    elif request.session.session_key:
        voted_poll_ids = set(Vote.objects.filter(session_key=request.session.session_key).values_list('poll_id', flat=True))

    return render(request, 'polls/feed.html', {
        'polls': polls,
        'voted_poll_ids': voted_poll_ids,
    })


def poll_detail_view(request, pk):
    """Tek bir anketin detay ve oy ekranı."""
    if not request.session.session_key:
        request.session.save()

    poll = get_object_or_404(Poll.objects.select_related('creator').prefetch_related('options'), pk=pk)
    user_vote = get_user_vote(poll, request)
    has_voted = user_vote is not None

    return render(request, 'polls/poll_detail.html', {
        'poll': poll,
        'user_vote': user_vote,
        'has_voted': has_voted,
    })


@login_required
def poll_create_view(request):
    """Yeni anket açma ekranı. Yalnızca üyeler anket oluşturabilir."""
    if request.method == 'POST':
        form = PollCreateForm(request.POST)
        raw_options = request.POST.getlist('options')
        # Boşlukları temizle ve boş seçenekleri ele
        clean_options = [opt.strip() for opt in raw_options if opt.strip()]

        if not form.is_valid():
            return render(request, 'polls/poll_create.html', {
                'form': form,
                'entered_options': raw_options
            })

        if len(clean_options) < 2:
            messages.error(request, "En az 2 seçenek eklemelisiniz.")
            return render(request, 'polls/poll_create.html', {
                'form': form,
                'entered_options': raw_options
            })

        if len(clean_options) > 5:
            messages.error(request, "En fazla 5 seçenek ekleyebilirsiniz.")
            return render(request, 'polls/poll_create.html', {
                'form': form,
                'entered_options': raw_options[:5]
            })

        try:
            with transaction.atomic():
                poll = form.save(commit=False)
                poll.creator = request.user
                poll.save()

                for opt_text in clean_options:
                    Option.objects.create(poll=poll, text=opt_text)

            messages.success(request, "Kararsızlığın yayınlandı! Bakalım topluluk ne diyecek.")
            return redirect('polls:detail', pk=poll.pk)

        except Exception as e:
            messages.error(request, f"Anket oluşturulurken bir hata oluştu: {e}")
            return render(request, 'polls/poll_create.html', {
                'form': form,
                'entered_options': raw_options
            })

    else:
        form = PollCreateForm()
        # Varsayılan olarak 2 boş seçenekle başlat
        return render(request, 'polls/poll_create.html', {
            'form': form,
            'entered_options': ['', '']
        })


def vote_view(request, pk):
    """Oy verme işlemi. Hem üyeler hem de misafirler oy kullanabilir."""
    if request.method != 'POST':
        return redirect('polls:detail', pk=pk)

    poll = get_object_or_404(Poll, pk=pk, is_active=True)
    option_id = request.POST.get('option')

    if not option_id:
        messages.warning(request, "Lütfen bir seçenek işaretleyin.")
        return redirect('polls:detail', pk=pk)

    option = get_object_or_404(Option, pk=option_id, poll=poll)

    # Oturum kontrolü
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    # Mükerrer oy kontrolü
    if request.user.is_authenticated:
        if Vote.objects.filter(poll=poll, user=request.user).exists():
            messages.warning(request, "Bu ankete zaten oy verdiniz.")
            return redirect('polls:detail', pk=pk)
        try:
            Vote.objects.create(poll=poll, option=option, user=request.user)
            messages.success(request, "Oyunuz başarıyla kaydedildi!")
        except IntegrityError:
            messages.warning(request, "Bu ankete zaten oy kullandınız.")
    else:
        if Vote.objects.filter(poll=poll, session_key=session_key).exists():
            messages.warning(request, "Bu ankete zaten oy verdiniz.")
            return redirect('polls:detail', pk=pk)
        try:
            Vote.objects.create(poll=poll, option=option, session_key=session_key)
            messages.success(request, "Misafir oyunuz başarıyla kaydedildi!")
        except IntegrityError:
            messages.warning(request, "Bu ankete zaten oy kullandınız.")

    return redirect('polls:detail', pk=pk)
