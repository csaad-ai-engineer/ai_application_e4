# Spécifications fonctionnelles — ImmoPredictor
# C14 — Analyser les besoins d'une application intégrant de l'IA

---

## 1. Contexte

L'application ImmoPredictor permet à des utilisateurs de consommer un service d'estimation immobilière par IA. Le modèle de machine learning est exposé via une API FastAPI (développée séparément) qui propose deux endpoints principaux :
- `POST /predict` — estimation individuelle
- `POST /predict/batch` — estimation en lot (max 100 par appel)

ImmoPredictor constitue le **front-end utilisateur** de ce service.

---

## 2. Acteurs et cas d'utilisation

### Acteurs
- **Utilisateur authentifié** : peut effectuer des estimations, consulter son historique, exporter ses données
- **Administrateur** (Django admin) : gère les comptes utilisateurs, supervise les prédictions

### Diagramme des cas d'utilisation (textuel)

```
Utilisateur
├── S'inscrire (avec consentement RGPD)
├── Se connecter / déconnecter
├── Effectuer une estimation individuelle
│   ├── Saisir les caractéristiques du bien
│   └── Visualiser le résultat (prix, fourchette, prix/m²)
├── Importer un batch CSV
│   ├── Uploader un fichier CSV
│   └── Consulter le rapport de traitement
├── Consulter l'historique
│   ├── Filtrer par type, département, date
│   └── Paginer les résultats
├── Exporter ses données
│   ├── CSV de l'historique
│   └── JSON complet (RGPD)
└── Gérer son compte
    ├── Modifier son profil
    ├── Demander l'export de ses données
    └── Demander la suppression (droit à l'oubli)
```

---

## 3. Règles métier

| ID | Règle |
|----|-------|
| RM01 | Un utilisateur doit accepter les CGU/politique RGPD pour créer un compte |
| RM02 | Un utilisateur ne peut voir que ses propres prédictions |
| RM03 | Le fichier CSV ne peut dépasser 500 lignes et 5 Mo |
| RM04 | Le token JWT API est renouvelé automatiquement avant expiration |
| RM05 | En cas d'erreur API, la prédiction est sauvegardée en statut `error` |
| RM06 | L'export de données doit être disponible dans les 72h (RGPD art. 20) |
| RM07 | La demande de suppression déclenche une suppression différée sous 30 jours |

---

## 4. Modèle de données (entités principales)

```
User
├── username, email (unique)
├── consentement_rgpd, consentement_date
└── demande_suppression, demande_suppression_date

Prediction
├── user (FK User)
├── Entrées: surface_reelle_bati, nombre_pieces_principales,
│           surface_terrain, longitude, latitude,
│           type_local, code_departement
├── Sorties: prix_estime, intervalle_bas, intervalle_haut,
│            prix_m2, modele_version, latence_api_ms
└── status (pending | success | error), error_message

PredictionBatch
├── user (FK User)
├── fichier_csv
├── nb_lignes, nb_succes, nb_erreurs
└── status (pending | processing | done | error)
```

---

## 5. Contraintes non-fonctionnelles

| Catégorie | Exigence |
|-----------|----------|
| Performance | Réponse < 3s pour une estimation individuelle |
| Disponibilité | 99% (hors maintenance planifiée) |
| Sécurité | HTTPS obligatoire, OWASP Top 10 couverts |
| Accessibilité | WCAG 2.1 AA (navigation clavier, lecteur d'écran) |
| RGPD | Consentement, portabilité, droit à l'oubli |
| Scalabilité | Architecture conteneurisée, horizontalement scalable |

---

## 6. Interfaces

### Interface utilisateur
- Design responsive (mobile + desktop)
- Feedback immédiat sur les erreurs de formulaire
- Messages de confirmation après actions
- Navigation accessible au clavier
- Contraste couleur WCAG AA

### Interface API (sortante vers l'API de prédiction)
- Authentification Bearer JWT
- Retry automatique sur erreurs 5xx
- Timeout configurable (défaut 10s)
- Logs des appels pour audit

---

## 7. Architecture de déploiement

```
Internet → Nginx (reverse proxy) → Gunicorn (Django)
                                         ↓
                                    PostgreSQL
                                         ↓
                                      Redis
                                         ↓
                               API FastAPI (externe)
```
