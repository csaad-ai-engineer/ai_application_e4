from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login as auth_login
from .forms import RegisterForm, ProfileUpdateForm, DataExportForm, DeletionRequestForm


def register(request):
    """C17 - Création de compte avec consentement RGPD."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} ! Votre compte a été créé.")
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    from .forms import LoginForm
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        print("POST data:", request.POST)
        print("Form valid:", form.is_valid())
        print("Form errors:", form.errors)
        if form.is_valid():
            user = form.get_user()
            print("User:", user)
            user.backend = 'accounts.backends.AccountsBackend'
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm(request=request)
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def export_data(request):
    """RGPD - Export des données personnelles (Article 20 RGPD)."""
    if request.method == 'POST':
        form = DataExportForm(request.POST)
        if form.is_valid():
            user = request.user
            predictions = list(user.predictions.values(
                'id', 'created_at', 'prix_estime', 'surface_reelle_bati',
                'nombre_pieces_principales', 'code_departement', 'type_local'
            ))
            # Convertir les datetimes en string
            for p in predictions:
                if p.get('created_at'):
                    p['created_at'] = p['created_at'].isoformat()

            data = {
                'utilisateur': {
                    'username': user.username,
                    'email': user.email,
                    'date_inscription': user.date_joined.isoformat(),
                    'consentement_rgpd': user.consentement_rgpd,
                    'consentement_date': user.consentement_date.isoformat() if user.consentement_date else None,
                },
                'predictions': predictions,
            }
            response = JsonResponse(data, json_dumps_params={'indent': 2, 'ensure_ascii': False})
            response['Content-Disposition'] = 'attachment; filename="mes_donnees.json"'
            return response
    else:
        form = DataExportForm()
    return render(request, 'accounts/export_data.html', {'form': form})


@login_required
def request_deletion(request):
    """RGPD - Droit à l'oubli (Article 17 RGPD)."""
    if request.method == 'POST':
        form = DeletionRequestForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            user.demande_suppression = True
            user.demande_suppression_date = timezone.now()
            user.save()
            # En production : déclencher un workflow de suppression différée
            logout(request)
            messages.info(request, "Votre demande de suppression a été enregistrée. Vos données seront supprimées dans 30 jours.")
            return redirect('login')
    else:
        form = DeletionRequestForm(user=request.user)
    return render(request, 'accounts/request_deletion.html', {'form': form})
