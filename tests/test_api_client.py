"""
tests/test_api_client.py

C18 — Tests automatisés du client API.
Utilise unittest.mock pour simuler les appels HTTP.
"""

import os
from unittest.mock import MagicMock, patch

import django
import pytest

from predictions.services import APIClientError, PredictionAPIClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "immo_predictor.settings")
django.setup()

# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def client():
    return PredictionAPIClient()


MOCK_TOKEN_RESPONSE = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test",
    "token_type": "bearer",
}

MOCK_PREDICTION_RESPONSE = {
    "prix_estime": 350000.0,
    "intervalle_bas": 315000.0,
    "intervalle_haut": 385000.0,
    "prix_m2": 4666.67,
    "modele_version": "v1.2.3",
    "latence_ms": 42.5,
}


# ─── Tests authentification ──────────────────────────────────────────────────
class TestAuthentication:
    def test_authenticate_success(self, client):
        """L'authentification retourne un token si l'API répond correctement."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_TOKEN_RESPONSE
        mock_resp.raise_for_status.return_value = None

        with patch.object(client.session, "post", return_value=mock_resp):
            token = client._authenticate()
            assert token == MOCK_TOKEN_RESPONSE["access_token"]

    def test_authenticate_timeout_raises(self, client):
        """Un timeout doit lever APIClientError."""
        import requests

        with patch.object(client.session, "post", side_effect=requests.Timeout):
            with pytest.raises(APIClientError, match="Timeout"):
                client._authenticate()

    def test_authenticate_missing_token_raises(self, client):
        """Si le token est absent de la réponse, APIClientError est levée."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status.return_value = None

        with patch.object(client.session, "post", return_value=mock_resp):
            with pytest.raises(APIClientError, match="Token absent"):
                client._authenticate()

    def test_get_token_caches(self, client):
        """Le token est mis en cache et non redemandé si valide."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_TOKEN_RESPONSE
        mock_resp.raise_for_status.return_value = None

        with patch.object(client.session, "post", return_value=mock_resp) as mock_post:
            client._get_token()
            client._get_token()
            # Appelé une seule fois
            assert mock_post.call_count == 1


# ─── Tests prédiction individuelle ──────────────────────────────────────────


class TestPredict:
    def test_predict_success(self, client):
        """predict() retourne les données de l'API en cas de succès."""
        # Mock du token
        client._token = "test_token"
        client._token_expires_at = float("inf")

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_PREDICTION_RESPONSE
        mock_resp.raise_for_status.return_value = None
        mock_resp.status_code = 200

        payload = {
            "surface_reelle_bati": 75.0,
            "nombre_pieces_principales": 3,
            "surface_terrain": 0,
            "longitude": 2.3522,
            "latitude": 48.8566,
            "type_local": "Appartement",
            "code_departement": "75",
        }

        with patch.object(client.session, "post", return_value=mock_resp):
            result = client.predict(payload)

        assert result["prix_estime"] == 350000.0
        assert result["modele_version"] == "v1.2.3"

    def test_predict_401_retries_with_new_token(self, client):
        """Un 401 déclenche un refresh du token et un nouvel essai."""
        client._token = "expired_token"
        client._token_expires_at = float("inf")

        token_resp = MagicMock()
        token_resp.json.return_value = MOCK_TOKEN_RESPONSE
        token_resp.raise_for_status.return_value = None

        predict_resp_401 = MagicMock()
        predict_resp_401.status_code = 401

        predict_resp_ok = MagicMock()
        predict_resp_ok.json.return_value = MOCK_PREDICTION_RESPONSE
        predict_resp_ok.raise_for_status.return_value = None
        predict_resp_ok.status_code = 200

        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            call_count["n"] += 1
            if "/token" in args[0]:
                return token_resp
            if call_count["n"] == 1:
                return predict_resp_401
            return predict_resp_ok

        with patch.object(client.session, "post", side_effect=side_effect):
            result = client.predict({"surface_reelle_bati": 50})
            assert result["prix_estime"] == 350000.0

    def test_predict_http_error_raises(self, client):
        """Une erreur HTTP non-401 doit lever APIClientError."""
        import requests

        client._token = "test_token"
        client._token_expires_at = float("inf")

        mock_resp = MagicMock()
        mock_resp.status_code = 422
        http_error = requests.HTTPError(response=mock_resp)
        mock_resp.raise_for_status.side_effect = http_error
        mock_resp.json.return_value = {"detail": "Validation error"}

        with patch.object(client.session, "post", return_value=mock_resp):
            with pytest.raises(APIClientError):
                client.predict({})


# ─── Tests batch ─────────────────────────────────────────────────────────────


class TestBatch:
    def test_predict_batch_empty_returns_empty(self, client):
        """Un batch vide retourne une liste vide sans appel API."""
        with patch.object(client.session, "post") as mock_post:
            result = client.predict_batch([])
            assert result == []
            mock_post.assert_not_called()

    def test_predict_batch_chunks_large_input(self, client):
        """Un batch de 250 items doit être découpé en 3 chunks."""
        client._token = "test_token"
        client._token_expires_at = float("inf")

        items = [{"surface_reelle_bati": 50 + i} for i in range(250)]

        mock_resp = MagicMock()
        mock_resp.json.side_effect = [
            [MOCK_PREDICTION_RESPONSE] * 100,
            [MOCK_PREDICTION_RESPONSE] * 100,
            [MOCK_PREDICTION_RESPONSE] * 50,
        ]
        mock_resp.raise_for_status.return_value = None
        mock_resp.status_code = 200

        with patch.object(client.session, "post", return_value=mock_resp) as mock_post:
            result = client.predict_batch(items)
            assert mock_post.call_count == 3  # 3 chunks de 100
            assert len(result) == 250


# ─── Tests health ─────────────────────────────────────────────────────────────


class TestHealth:
    def test_health_success(self, client):
        """health() retourne la réponse de l'API."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "healthy", "model": "loaded"}
        mock_resp.raise_for_status.return_value = None

        with patch.object(client.session, "get", return_value=mock_resp):
            result = client.health()
            assert result["status"] == "healthy"

    def test_health_error_raises(self, client):
        """Si l'API est indisponible, APIClientError est levée."""
        import requests

        with patch.object(client.session, "get", side_effect=requests.ConnectionError):
            with pytest.raises(APIClientError, match="indisponible"):
                client.health()
