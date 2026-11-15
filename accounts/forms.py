from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Kullanıcı Adı",
        help_text="Anketlerde diğer kullanıcılara sadece bu ad gösterilir.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'örnek: karar_avcisi'
        })
    )
    email = forms.EmailField(
        required=True,
        label="E-posta Adresi",
        help_text="E-posta adresiniz diğer kullanıcılarla asla paylaşılmaz.",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ornek@email.com'
        })
    )
    password = forms.CharField(
        label="Şifre",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
    )
    password_confirm = forms.CharField(
        label="Şifre Tekrarı",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Bu kullanıcı adı zaten alınmış. Lütfen başka bir tane seçin.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu e-posta adresi ile kayıtlı bir hesap zaten var.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Şifreler birbiriyle uyuşmuyor.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Kullanıcı Adı",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kullanıcı adınızı girin'
        })
    )
    password = forms.CharField(
        label="Şifre",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
    )
