from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Adresse e-mail",
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'aria-required': 'true'})
    )
    consentement_rgpd = forms.BooleanField(
        required=True,
        label="J'accepte la politique de confidentialité et le traitement de mes données personnelles.",
        error_messages={'required': "Vous devez accepter la politique de confidentialité pour créer un compte."}
    )

    class Meta:
        from accounts.models import User
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'consentement_rgpd')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.consentement_rgpd = True
        user.consentement_date = timezone.now()
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'autofocus': True, 'aria-required': 'true'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'aria-required': 'true'})
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        from django.contrib.auth import authenticate
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Nom d'utilisateur ou mot de passe incorrect."
                )
            if not self.user_cache.is_active:
                raise forms.ValidationError("Ce compte est inactif.")
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        from accounts.models import User
        model = User
        fields = ('first_name', 'last_name', 'email')
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Adresse e-mail',
        }


class DataExportForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="Je confirme vouloir exporter l'ensemble de mes données personnelles."
    )


class DeletionRequestForm(forms.Form):
    confirm_username = forms.CharField(
        label="Confirmez votre nom d'utilisateur pour valider la demande de suppression.",
        widget=forms.TextInput(attrs={'aria-required': 'true'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_confirm_username(self):
        value = self.cleaned_data['confirm_username']
        if self.user and value != self.user.username:
            raise forms.ValidationError("Le nom d'utilisateur ne correspond pas.")
        return value
