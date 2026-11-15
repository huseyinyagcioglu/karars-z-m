from django import forms
from .models import Poll


class PollCreateForm(forms.ModelForm):
    question = forms.CharField(
        max_length=255,
        required=True,
        label="Neyde kararsız kaldın?",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Örn: Akşam sinemaya mı gitsem yoksa restorana mı?'
        })
    )

    class Meta:
        model = Poll
        fields = ['question']

    def clean(self):
        cleaned_data = super().clean()
        # Seçenekler view katmanında request.POST.getlist('options') ile toplanıp doğrulanacak.
        return cleaned_data
