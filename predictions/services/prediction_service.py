import csv
import io
import logging
from django.db import transaction
from predictions.models import Prediction
from predictions.services import api_client, APIClientError

logger = logging.getLogger('predictions')

REQUIRED_CSV_FIELDS = {
    'surface_reelle_bati', 'nombre_pieces_principales', 'longitude',
    'latitude', 'type_local', 'code_departement'
}


def create_prediction(user, form_data):
    """Crée une prédiction individuelle via l'API externe."""
    prediction = Prediction(
        user_id=user.pk,
        surface_reelle_bati=float(form_data['surface_reelle_bati']),
        nombre_pieces_principales=int(form_data['nombre_pieces_principales']),
        surface_terrain=float(form_data.get('surface_terrain') or 0),
        longitude=float(form_data['longitude']),
        latitude=float(form_data['latitude']),
        type_local=form_data['type_local'],
        code_departement=form_data['code_departement'],
        status='pending',
    )
    prediction.save()

    try:
        result = api_client.predict(prediction.input_data)
        prediction.prix_estime = result.get('prix_estime')
        prediction.intervalle_bas = result.get('intervalle_bas')
        prediction.intervalle_haut = result.get('intervalle_haut')
        prediction.prix_m2 = result.get('prix_m2')
        prediction.modele_version = result.get('modele_version', '')
        prediction.latence_api_ms = result.get('latence_ms')
        prediction.status = 'success'
        logger.info(f"Prédiction {prediction.id} : {prediction.prix_estime}€")
    except APIClientError as e:
        prediction.status = 'error'
        prediction.error_message = str(e)
        logger.error(f"Erreur prédiction {prediction.id} : {e}")

    prediction.save()
    return prediction


def process_batch_from_csv(user, batch, file_content):
    """Traite un batch CSV via l'API externe."""
    batch.status = 'processing'
    batch.save()

    try:
        text = file_content.decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(text))

        if not REQUIRED_CSV_FIELDS.issubset(set(reader.fieldnames or [])):
            missing = REQUIRED_CSV_FIELDS - set(reader.fieldnames or [])
            raise ValueError(f"Colonnes manquantes dans le CSV : {missing}")

        rows = list(reader)
        if len(rows) > 500:
            raise ValueError("Le fichier CSV ne peut pas dépasser 500 lignes.")

        items = []
        for row in rows:
            items.append({
                'surface_reelle_bati': float(row['surface_reelle_bati']),
                'nombre_pieces_principales': int(row['nombre_pieces_principales']),
                'surface_terrain': float(row.get('surface_terrain') or 0),
                'longitude': float(row['longitude']),
                'latitude': float(row['latitude']),
                'type_local': row['type_local'],
                'code_departement': row['code_departement'],
            })

        batch.nb_lignes = len(items)
        results = api_client.predict_batch(items)

        predictions = []
        for item, result in zip(items, results):
            p = Prediction(
                user_id=user.pk,
                **item,
                prix_estime=result.get('prix_estime'),
                intervalle_bas=result.get('intervalle_bas'),
                intervalle_haut=result.get('intervalle_haut'),
                prix_m2=result.get('prix_m2'),
                modele_version=result.get('modele_version', ''),
                latence_api_ms=result.get('latence_ms'),
                status='success',
            )
            predictions.append(p)

        with transaction.atomic():
            Prediction.objects.bulk_create(predictions)

        batch.nb_succes = len(predictions)
        batch.status = 'done'

    except (ValueError, APIClientError) as e:
        batch.status = 'error'
        batch.error_message = str(e)
        logger.error(f"Erreur batch {batch.id} : {e}")

    batch.save()
    return batch
