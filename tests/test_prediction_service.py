"""
tests/test_prediction_service.py

C18 — Tests du service de prédiction et des modèles.
Utilise pytest-django pour les tests de BDD.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class TestPredictionModel(TestCase):
    """Tests unitaires du modèle Prediction."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            consentement_rgpd=True,
        )

    def test_input_data_property(self):
        """La propriété input_data retourne le bon dictionnaire."""
        from predictions.models import Prediction

        p = Prediction(
            user=self.user,
            surface_reelle_bati=75.0,
            nombre_pieces_principales=3,
            surface_terrain=0.0,
            longitude=2.3522,
            latitude=48.8566,
            type_local="Appartement",
            code_departement="75",
        )
        data = p.input_data
        assert data["surface_reelle_bati"] == 75.0
        assert data["type_local"] == "Appartement"
        assert data["code_departement"] == "75"
        assert "longitude" in data
        assert "latitude" in data

    def test_str_representation(self):
        """__str__ retourne une représentation lisible."""
        from predictions.models import Prediction

        p = Prediction.objects.create(
            user=self.user,
            surface_reelle_bati=50.0,
            nombre_pieces_principales=2,
            longitude=2.0,
            latitude=48.0,
            type_local="Appartement",
            code_departement="75",
            status="success",
            prix_estime=250000.0,
        )
        assert "testuser" in str(p)
        assert "Appartement" in str(p)


class TestCreatePrediction(TestCase):
    """Tests du service create_prediction."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
        )
        self.form_data = {
            "surface_reelle_bati": 75.0,
            "nombre_pieces_principales": 3,
            "surface_terrain": None,
            "longitude": 2.3522,
            "latitude": 48.8566,
            "type_local": "Appartement",
            "code_departement": "75",
        }
        self.api_response = {
            "prix_estime": 320000.0,
            "intervalle_bas": 288000.0,
            "intervalle_haut": 352000.0,
            "prix_m2": 4266.67,
            "modele_version": "test-v1",
            "latence_ms": 25.0,
        }

    def test_create_prediction_success(self):
        """En cas de succès API, la prédiction est sauvegardée avec les bons résultats."""
        from predictions.models import Prediction
        from predictions.services.prediction_service import create_prediction

        with patch(
            "predictions.services.prediction_service.api_client.predict",
            return_value=self.api_response,
        ):
            prediction = create_prediction(self.user, self.form_data)

        assert prediction.status == "success"
        assert prediction.prix_estime == 320000.0
        assert prediction.modele_version == "test-v1"
        assert Prediction.objects.filter(user=self.user, status="success").count() == 1

    def test_create_prediction_api_error(self):
        """En cas d'erreur API, la prédiction est sauvegardée en statut error."""
        from predictions.services import APIClientError
        from predictions.services.prediction_service import create_prediction

        with patch(
            "predictions.services.prediction_service.api_client.predict",
            side_effect=APIClientError("API indisponible"),
        ):
            prediction = create_prediction(self.user, self.form_data)

        assert prediction.status == "error"
        assert "API indisponible" in prediction.error_message
        assert prediction.prix_estime is None


class TestProcessBatchFromCsv(TestCase):
    """Tests du traitement batch CSV."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="batchuser",
            email="batch@example.com",
            password="testpass123",
        )

    def test_batch_missing_columns_error(self):
        """Un CSV avec colonnes manquantes doit mettre le batch en erreur."""
        from predictions.models import PredictionBatch
        from predictions.services.prediction_service import process_batch_from_csv

        batch = PredictionBatch.objects.create(user=self.user)
        csv_content = b"surface_reelle_bati,nombre_pieces_principales\n75,3\n"

        result = process_batch_from_csv(self.user, batch, csv_content)
        assert result.status == "error"
        assert "Colonnes manquantes" in result.error_message

    def test_batch_too_many_rows(self):
        """Un CSV avec plus de 500 lignes doit être rejeté."""
        from predictions.models import PredictionBatch
        from predictions.services.prediction_service import process_batch_from_csv

        batch = PredictionBatch.objects.create(user=self.user)
        header = "surface_reelle_bati,nombre_pieces_principales,surface_terrain,longitude,latitude,type_local,code_departement\n"
        rows = "\n".join(["75,3,0,2.35,48.85,Appartement,75"] * 501)
        csv_content = (header + rows).encode()

        result = process_batch_from_csv(self.user, batch, csv_content)
        assert result.status == "error"
        assert "500" in result.error_message

    def test_batch_success(self):
        """Un CSV valide doit créer les prédictions en BDD."""
        from predictions.models import Prediction, PredictionBatch
        from predictions.services.prediction_service import process_batch_from_csv

        batch = PredictionBatch.objects.create(user=self.user)
        header = "surface_reelle_bati,nombre_pieces_principales,surface_terrain,longitude,latitude,type_local,code_departement\n"
        rows = "\n".join(
            [
                "75,3,0,2.35,48.85,Appartement,75",
                "120,4,200,2.35,48.85,Maison,78",
            ]
        )
        csv_content = (header + rows).encode()

        api_result = {
            "prix_estime": 300000,
            "intervalle_bas": 270000,
            "intervalle_haut": 330000,
            "prix_m2": 4000,
            "modele_version": "v1",
            "latence_ms": 10,
        }

        with patch(
            "predictions.services.prediction_service.api_client.predict_batch",
            return_value=[api_result, api_result],
        ):
            result = process_batch_from_csv(self.user, batch, csv_content)

        assert result.status == "done"
        assert result.nb_succes == 2
        assert Prediction.objects.filter(user=self.user).count() == 2


class TestReportService(TestCase):
    """Tests du service de génération de rapports."""

    def setUp(self):
        self.user = User.objects.create_user(username="reporter", email="r@test.com", password="x")
        from predictions.models import Prediction

        Prediction.objects.create(
            user=self.user,
            surface_reelle_bati=75.0,
            nombre_pieces_principales=3,
            longitude=2.35,
            latitude=48.85,
            type_local="Appartement",
            code_departement="75",
            prix_estime=350000.0,
            prix_m2=4666.0,
            status="success",
        )

    def test_export_csv_contains_header(self):
        """L'export CSV doit contenir une ligne d'entête."""
        from predictions.models import Prediction
        from predictions.services.report_service import export_predictions_csv

        qs = Prediction.objects.filter(user=self.user)
        csv_content = export_predictions_csv(qs)
        assert "prix_estime_eur" in csv_content
        assert "350000" in csv_content

    def test_export_json_is_valid(self):
        """L'export JSON doit être parsable et contenir les bonnes clés."""
        import json

        from predictions.models import Prediction
        from predictions.services.report_service import export_predictions_json

        qs = Prediction.objects.filter(user=self.user)
        json_content = export_predictions_json(qs)
        data = json.loads(json_content)
        assert len(data) == 1
        assert "entree" in data[0]
        assert "resultat" in data[0]
        assert data[0]["resultat"]["prix_estime"] == 350000.0
