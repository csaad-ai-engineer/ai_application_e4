"""
tests/test_views.py

C18 — Tests d'intégration des vues Django.
Teste l'authentification, les redirections et le comportement des formulaires.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestAuthViews(TestCase):
    """Tests des vues d'authentification."""

    def test_register_get(self):
        """La page d'inscription est accessible."""
        response = self.client.get(reverse("register"))
        assert response.status_code == 200
        assert "form" in response.context

    def test_register_post_valid(self):
        """Un formulaire d'inscription valide crée un compte et redirige."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
            "consentement_rgpd": True,
        }
        response = self.client.post(reverse("register"), data)
        assert response.status_code == 302
        assert User.objects.filter(username="newuser").exists()
        user = User.objects.get(username="newuser")
        assert user.consentement_rgpd is True

    def test_register_post_missing_rgpd(self):
        """Sans consentement RGPD, le formulaire est invalide."""
        data = {
            "username": "norgpd",
            "email": "norgpd@example.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }
        response = self.client.post(reverse("register"), data)
        assert response.status_code == 200
        assert not User.objects.filter(username="norgpd").exists()

    def test_login_success(self):
        """Une connexion valide redirige vers le dashboard."""
        User.objects.create_user(username="loginuser", email="l@test.com", password="testpass123")
        response = self.client.post(
            reverse("login"), {"username": "loginuser", "password": "testpass123"}
        )
        assert response.status_code == 302

    def test_login_invalid_credentials(self):
        """Des identifiants invalides restent sur la page de login."""
        response = self.client.post(reverse("login"), {"username": "nobody", "password": "wrong"})
        assert response.status_code == 200


class TestPredictViews(TestCase):
    """Tests d'intégration des vues de prédiction."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client.login(username="testuser", password="testpass123")

    def test_dashboard_authenticated(self):
        """Le dashboard est accessible pour un utilisateur connecté."""
        response = self.client.get(reverse("dashboard"))
        assert response.status_code == 200

    def test_dashboard_redirects_anonymous(self):
        """Le dashboard redirige vers login pour un anonyme."""
        self.client.logout()
        response = self.client.get(reverse("dashboard"))
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_predict_get(self):
        """La page de prédiction est accessible."""
        response = self.client.get(reverse("predict"))
        assert response.status_code == 200

    def test_predict_post_success(self):
        """Un formulaire de prédiction valide appelle l'API et redirige."""
        api_response = {
            "prix_estime": 350000.0,
            "intervalle_bas": 315000.0,
            "intervalle_haut": 385000.0,
            "prix_m2": 4666.67,
            "modele_version": "v1",
            "latence_ms": 30.0,
        }
        data = {
            "type_local": "Appartement",
            "surface_reelle_bati": "75",
            "nombre_pieces_principales": "3",
            "surface_terrain": "",
            "code_departement": "75",
            "latitude": "48.8566",
            "longitude": "2.3522",
        }
        with patch(
            "predictions.services.prediction_service.api_client.predict", return_value=api_response
        ):
            response = self.client.post(reverse("predict"), data)

        assert response.status_code == 302
        from predictions.models import Prediction

        assert Prediction.objects.filter(user=self.user, status="success").count() == 1

    def test_predict_post_missing_field(self):
        """Un formulaire incomplet reste sur la page de prédiction."""
        data = {
            "type_local": "Appartement",
            # surface_reelle_bati manquant
        }
        response = self.client.post(reverse("predict"), data)
        assert response.status_code == 200

    def test_history_view(self):
        """La vue historique retourne 200 avec les prédictions."""
        response = self.client.get(reverse("prediction_history"))
        assert response.status_code == 200
        assert "page_obj" in response.context

    def test_export_csv(self):
        """L'export CSV retourne un fichier avec le bon Content-Type."""
        response = self.client.get(reverse("export_csv"))
        assert response.status_code == 200
        assert "text/csv" in response["Content-Type"]

    def test_export_json(self):
        """L'export JSON retourne un fichier avec le bon Content-Type."""
        response = self.client.get(reverse("export_json"))
        assert response.status_code == 200
        assert "application/json" in response["Content-Type"]

    def test_prediction_detail_wrong_user(self):
        """Un utilisateur ne peut pas accéder aux prédictions d'un autre."""
        from predictions.models import Prediction

        other_user = User.objects.create_user(
            username="other", email="o@test.com", password="pass"
        )
        pred = Prediction.objects.create(
            user=other_user,
            surface_reelle_bati=50,
            nombre_pieces_principales=2,
            longitude=2.0,
            latitude=48.0,
            type_local="Appartement",
            code_departement="75",
        )
        response = self.client.get(reverse("prediction_detail", kwargs={"pk": pred.pk}))
        assert response.status_code == 404


class TestBatchView(TestCase):
    """Tests d'intégration de la vue batch."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="batchtest",
            email="b@test.com",
            password="testpass123",
        )
        self.client.login(username="batchtest", password="testpass123")

    def test_batch_upload_get(self):
        """La page d'upload batch est accessible."""
        response = self.client.get(reverse("batch_upload"))
        assert response.status_code == 200

    def test_batch_upload_invalid_extension(self):
        """Un fichier non-CSV est rejeté."""
        import io

        fake_file = io.BytesIO(b"data")
        fake_file.name = "data.xlsx"
        response = self.client.post(reverse("batch_upload"), {"fichier_csv": fake_file})
        assert response.status_code == 200  # Reste sur la page avec erreur
