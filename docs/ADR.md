# Architecture Decision Records (ADR)
# ImmoPredictor — Bloc E4 RNCP37827

---

## ADR-001 : Choix de Django comme framework backend

**Date** : 2025-01
**Statut** : Accepté

### Contexte
L'application doit consommer une API externe, gérer des utilisateurs avec authentification, stocker un historique en base de données et exposer une interface web accessible.

### Décision
Utiliser **Django 4.2 LTS** avec Django REST Framework.

### Justification
- Authentification intégrée (contrib.auth) → moins de code à écrire et à sécuriser
- ORM Django → protection SQL injection native, migrations gérées
- Templates → auto-échappement XSS
- Écosystème mature (pytest-django, debug-toolbar, ratelimit)
- LTS 4.2 supporté jusqu'en avril 2026

### Alternatives rejetées
- FastAPI : adapté pour les API, mais pas pour les templates et la gestion d'authentification web
- Flask : trop minimaliste, nécessite trop d'extensions tierces

---

## ADR-002 : Client HTTP avec retry automatique

**Date** : 2025-01
**Statut** : Accepté

### Contexte
L'API de prédiction externe est une dépendance critique. Des erreurs réseau transitoires (503, timeout) ne doivent pas échouer immédiatement.

### Décision
Utiliser **requests** avec `urllib3.util.retry.Retry` configuré sur 3 tentatives avec backoff exponentiel.

### Justification
- Résilience aux erreurs transitoires de l'API externe
- Refresh automatique du token JWT sur 401 (token expiré)
- Session réutilisée (connexions HTTP persistantes)

---

## ADR-003 : PostgreSQL comme base de données de production

**Date** : 2025-01
**Statut** : Accepté

### Contexte
Besoin d'une base de données relationnelle robuste pour stocker utilisateurs, prédictions et batches.

### Décision
**PostgreSQL 16** en production, SQLite pour les tests locaux et le développement rapide.

### Justification
- ACID complet (transactions atomiques pour bulk_create des batches)
- Meilleure performance sur les requêtes de filtrage/pagination
- Supporté nativement par Django

---

## ADR-004 : Stockage en clair des résultats (pas de chiffrement applicatif)

**Date** : 2025-01
**Statut** : Accepté

### Contexte
Les résultats de prédiction (prix estimés) ne sont pas des données personnelles sensibles au sens du RGPD, mais ils sont liés à un utilisateur.

### Décision
Les résultats sont stockés en clair dans PostgreSQL, protégés par l'authentification Django et les permissions de niveau objet (filtrage `user=request.user`).

### Mitigation
- Chiffrement au repos géré au niveau de la base de données (PostgreSQL disk encryption en production)
- Accès via HTTPS uniquement
- Droit à l'oubli implémenté

---

## ADR-005 : GitHub Actions pour CI/CD

**Date** : 2025-01
**Statut** : Accepté

### Contexte
Besoin d'un pipeline automatisé pour valider la qualité du code et déployer l'application.

### Décision
**GitHub Actions** avec 5 jobs : lint → test → build → deploy-staging → deploy-production.

### Justification
- Intégration native avec GitHub
- Gratuit pour les projets open-source
- GHCR (GitHub Container Registry) pour stocker les images Docker
- Environnements avec protections (approbation manuelle pour production)

---

## ADR-006 : HTMX vs SPA React

**Date** : 2025-01
**Statut** : Accepté

### Contexte
L'interface utilisateur doit être interactive (formulaires, filtres) sans être excessivement complexe.

### Décision
Templates Django natifs + JavaScript vanilla minimal. Pas de HTMX ni React pour cette version.

### Justification
- Simplicité de développement et de maintenance
- Moins de surface d'attaque (pas de dépendances JS tierces)
- Accessibilité facilitée (pas de rehydration React)
- Sufficient pour le périmètre fonctionnel visé

### Evolution possible
HTMX pourrait être ajouté ultérieurement pour le rechargement partiel des filtres/résultats sans rechargement complet de page.
