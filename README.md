# AI APPLICATION 🏠

**Application web Django de prédiction immobilière par IA**
Projet réalisé dans le cadre de la validation du Bloc E4 — RNCP37827 « Développeur en intelligence artificielle » (Simplon).

---

## 🎯 Contexte et objectif

Le projet présente une application web ImmoPredictor qui permet à des utilisateurs de :
- créer un compte (avec consentement RGPD)
- saisir les caractéristiques d'un bien immobilier et obtenir une estimation de prix par notre API IA
- importer un fichier CSV pour effectuer des estimations en lot (batch)
- consulter, filtrer et exporter l'historique de leurs prédictions
- exercer leurs droits RGPD (export de données, droit à l'oubli)

L'application consomme une API FastAPI externe qui expose `/predict` et `/predict/batch`.

---

## 🏗️ Architecture

```
ai_application_e4/
├── immo_predictor/      # Configuration Django (settings, urls, wsgi)
├── accounts/            # Authentification, profil utilisateur, RGPD
├── predictions/         # Modèles, vues, formulaires, services
│   └── services/        # APIClient, PredictionService, ReportService
├── templates/           # Templates HTML (Jinja-style Django)
│   ├── accounts/
│   └── predictions/
├── static/              # CSS, JS
├── tests/               # Tests unitaires et d'intégration
└── .github/workflows/   # CI/CD GitHub Actions
```

### Stack technique
| Composant         | Technologie           |
|-------------------|-----------------------|
| Backend           | Django 4.2 + DRF      |
| Base de données   | PostgreSQL 16         |
| Cache             | Redis 7               |
| Client HTTP       | requests (retry auto) |
| Reverse proxy     | Nginx                 |
| Conteneurisation  | Docker + Compose      |
| Tests             | pytest + pytest-django |
| CI/CD             | GitHub Actions        |

---

## 🚀 Installation

### 1. Prérequis
- Python 3.12+
- Docker + Docker Compose (recommandé)

### 2. Clonage et configuration

```bash
git clone https://github.com/votre-org/immo_predictor.git
cd immo_predictor
cp .env.example .env
# Éditez .env avec vos valeurs (DB, API URL, SECRET_KEY…)
```

### 3. Démarrage avec Docker Compose

```bash
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

L'application est accessible sur http://localhost:80.

### 4. Développement local (sans Docker)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

---

## 🧪 Tests

```bash
# Lancer tous les tests avec couverture
pytest tests/

# Rapport de couverture HTML
open htmlcov/index.html
```

Couverture cible : **≥ 80%**

### Structure des tests

| Fichier | Contenu |
|---------|---------|
| `tests/test_api_client.py` | Tests unitaires du client JWT (mock HTTP) |
| `tests/test_prediction_service.py` | Tests des services et modèles |
| `tests/test_views.py` | Tests d'intégration des vues |
| `tests/test_forms.py` | Tests de validation des formulaires |

---

## 🔄 CI/CD

Le pipeline GitHub Actions (`.github/workflows/ci.yml`) exécute automatiquement :

1. **Lint** : `black`, `isort`, `flake8` — sur chaque push
2. **Tests** : pytest avec couverture sur PostgreSQL — sur chaque push
3. **Build** : image Docker publiée sur GHCR — sur `main` et `develop`
4. **Staging** : déploiement automatique sur l'env. staging (`develop`)
5. **Production** : déploiement manuel déclenché sur `main`

---

## 🔒 Sécurité

- **CSRF** : protection Django native sur tous les formulaires POST
- **XSS** : auto-échappement des templates Django
- **Injection SQL** : ORM Django exclusivement
- **Rate limiting** : `django-ratelimit` (100 req/h en DRF)
- **JWT** : tokens non persistés côté Django, refresh automatique
- **Secrets** : variables d'environnement, jamais en dur dans le code
- **HTTPS** : `SECURE_SSL_REDIRECT` + HSTS activés en production

---

## ♿ Accessibilité (WCAG 2.1 AA)

- Lien d'évitement (skip link) vers le contenu principal
- Attributs `aria-label`, `aria-current`, `aria-required`, `role`
- Navigation entièrement au clavier (`:focus-visible` visible)
- Rapport de contraste > 4.5:1 sur toutes les couleurs
- Labels explicites sur tous les champs de formulaire
- Messages d'erreur liés aux champs avec `role="alert"`
- Responsive mobile-first

---

## 📋 Conformité RGPD

| Article RGPD | Implémentation |
|---|---|
| Art. 6 — Licéité | Consentement explicite à l'inscription |
| Art. 13 — Information | Mentions dans les formulaires |
| Art. 17 — Droit à l'oubli | Formulaire de demande de suppression |
| Art. 20 — Portabilité | Export JSON de toutes les données utilisateur |

---

## 📚 Compétences E4 couvertes

| Compétence | Couverture |
|---|---|
| C14 — Analyse du besoin | Modélisation, schémas, spécifications dans `/docs` |
| C15 — Cadre technique | Architecture ADR, choix de pile documentés |
| C16 — Coordination | Workflow Git (branches, PR), méthode agile |
| C17 — Développement | Django, DRF, services, templates accessibles, RGPD |
| C18 — Tests automatisés | pytest, couverture ≥80%, intégration continue |
| C19 — Livraison continue | GitHub Actions (lint → test → build → deploy) |

---

## 📂 Format du CSV (import batch)

```csv
surface_reelle_bati,nombre_pieces_principales,surface_terrain,longitude,latitude,type_local,code_departement
75.5,3,0,2.3522,48.8566,Appartement,75
120,4,200,2.35,48.85,Maison,78
```

Limite : 500 lignes par fichier, taille max 5 Mo.

---

## 🤝 Contribution

1. Fork du dépôt
2. Créer une branche : `git checkout -b feature/ma-fonctionnalite`
3. Commit : `git commit -m "feat: description"`
4. Push : `git push origin feature/ma-fonctionnalite`
5. Ouvrir une Pull Request vers `develop`

---

## 📄 Licence

Projet académique RNCP37827
