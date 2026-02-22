import logging
import time
from typing import Optional

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("predictions")


class APIClientError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class PredictionAPIClient:

    def __init__(self):
        self.base_url = settings.PREDICTION_API_URL.rstrip("/")
        self.username = settings.PREDICTION_API_USERNAME
        self.password = settings.PREDICTION_API_PASSWORD
        self.timeout = settings.PREDICTION_API_TIMEOUT
        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0

        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST", "GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _authenticate(self) -> str:
        url = f"{self.base_url}/token"
        try:
            response = self.session.post(
                url,
                json={"username": self.username, "password": self.password},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.Timeout:
            raise APIClientError("Timeout lors de l'authentification à l'API.")
        except requests.RequestException as e:
            raise APIClientError(f"Erreur d'authentification : {e}")

        data = response.json()
        token = data.get("access_token")
        if not token:
            raise APIClientError("Token absent dans la réponse d'authentification.")

        self._token_expires_at = time.time() + 55 * 60
        return token

    def _get_token(self) -> str:
        if not self._token or time.time() >= self._token_expires_at:
            self._token = self._authenticate()
        return self._token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    def predict(self, payload: dict) -> dict:
        url = f"{self.base_url}/predict"
        try:
            response = self.session.post(
                url, json=payload, headers=self._headers(), timeout=self.timeout
            )
            if response.status_code == 401:
                self._token = None
                response = self.session.post(
                    url, json=payload, headers=self._headers(), timeout=self.timeout
                )
            response.raise_for_status()
        except requests.Timeout:
            raise APIClientError("Timeout lors de la prédiction.")
        except requests.HTTPError as e:
            detail = ""
            try:
                detail = e.response.json().get("detail", "")
            except Exception:
                pass
            raise APIClientError(
                f"Erreur HTTP {e.response.status_code}: {detail}", e.response.status_code
            )
        except requests.RequestException as e:
            raise APIClientError(f"Erreur réseau : {e}")
        return response.json()

    def predict_batch(self, items: list) -> list:
        if not items:
            return []

        results = []
        chunk_size = 100

        for i in range(0, len(items), chunk_size):
            chunk = items[i : i + chunk_size]
            url = f"{self.base_url}/predict/batch"

            try:
                response = self.session.post(
                    url, json=chunk, headers=self._headers(), timeout=self.timeout * 5
                )

                if response.status_code == 401:
                    self._token = None
                    response = self.session.post(
                        url, json=chunk, headers=self._headers(), timeout=self.timeout * 5
                    )

                response.raise_for_status()

            except requests.RequestException as e:
                raise APIClientError(f"Erreur réseau (batch) : {e}")

            # L'API retourne maintenant une liste de PredictionResponse
            results.extend(response.json())

        return results

    def health(self) -> dict:
        url = f"{self.base_url}/health"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIClientError(f"API indisponible : {e}")


# Nouveau — recrée l'instance à chaque import
def get_api_client():
    return PredictionAPIClient()


api_client = PredictionAPIClient()
