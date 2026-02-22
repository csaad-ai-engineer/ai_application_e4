"""
predictions/services/report_service.py

C17 - Service de génération de rapports (CSV, JSON).
"""
import csv
import io
import json


def export_predictions_csv(queryset) -> str:
    """Génère un CSV des prédictions."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'id', 'date', 'type_local', 'departement', 'surface_m2',
        'nb_pieces', 'prix_estime_eur', 'prix_m2_eur',
        'borne_basse_eur', 'borne_haute_eur', 'modele', 'statut'
    ])
    for p in queryset:
        writer.writerow([
            p.id,
            p.created_at.strftime('%Y-%m-%d %H:%M'),
            p.type_local,
            p.code_departement,
            p.surface_reelle_bati,
            p.nombre_pieces_principales,
            round(p.prix_estime, 2) if p.prix_estime else '',
            round(p.prix_m2, 2) if p.prix_m2 else '',
            round(p.intervalle_bas, 2) if p.intervalle_bas else '',
            round(p.intervalle_haut, 2) if p.intervalle_haut else '',
            p.modele_version,
            p.get_status_display(),
        ])
    return output.getvalue()


def export_predictions_json(queryset) -> str:
    """Génère un JSON des prédictions (conformité RGPD, portabilité)."""
    data = []
    for p in queryset:
        data.append({
            'id': p.id,
            'date': p.created_at.isoformat(),
            'entree': p.input_data,
            'resultat': {
                'prix_estime': p.prix_estime,
                'prix_m2': p.prix_m2,
                'intervalle_bas': p.intervalle_bas,
                'intervalle_haut': p.intervalle_haut,
                'modele_version': p.modele_version,
            },
            'statut': p.status,
        })
    return json.dumps(data, indent=2, ensure_ascii=False)
