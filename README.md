# FastAPI Clean Architecture Starter (Async, SOLID, TDD/DDD/BDD)

Un starter moderne FastAPI avec une architecture propre (Clean Architecture), principes SOLID, DI (Annotated/Depends), appels HTTP asynchrones via httpx (cachés derrière un service), configuration par environnement (Pydantic Settings) et logs adaptés (console/JSON pour cloud/GCP/AWS), ainsi que des tests unitaires, d'intégration, E2E et BDD (pytest-bdd).

## Fonctionnalités
- FastAPI moderne (Python 3.11+, typings, Annotated DI)
- Clean Architecture / DDD: séparation domaine, application (use cases), infrastructure (adapters), API
- SOLID: dépendance sur des abstractions (services), implémentations adaptateurs remplaçables
- Appels HTTP externes via `httpx` encapsulés (aucune dépendance directe côté domaine)
- Configurations via Pydantic Settings: env local/cloud/gcp/aws, timeouts, URLs…
- Logging configurable selon l'environnement (console local, JSON pour cloud/GCP/AWS)
- Validation des entrées/sorties avec Pydantic (schemas de réponse)
- OpenAPI/Swagger prêts (docs, redoc)
- Tests: unitaires, intégration, E2E, et BDD (pytest-bdd)
- Asynchrone de bout en bout

## Arborescence
```
app/
  api/v1/routers.py        # Endpoints versionnés
  application/use_cases.py # Cas d'usage (orchestration)
  config/settings.py       # Configuration (Pydantic Settings)
  di/container.py          # Dépendances (Annotated + Depends)
  domain/                  # Entités + Services (interfaces métier)
    entities.py
    services.py
  infrastructure/
    http/http_client.py    # Adapter httpx pour HttpClient
    http/interfaces.py     # Interface technique HttpClient (hors domaine)
    logging/config.py      # Config des logs
    providers/cat_fact_http_provider.py # Adapter HTTP vers API publique
  main.py                  # Application FastAPI (OpenAPI, lifespan, routers)
  schemas/responses.py     # Schemas Pydantic (réponses)

tests/
  unit/                    # Tests unitaires (domaine/use-cases)
  integration/             # Tests adapter http (API publique)
  e2e/                     # Tests E2E FastAPI (overrides DI)
  bdd/                     # Scénarios pytest-bdd
    features/*.feature
    steps/*.py
```

## Démarrage rapide
1. Créer et activer un environnement virtuel Python 3.11+
2. Installer les dépendances:
   ```bash
   pip install -e .[dev]
   ```
3. Variables d'env (optionnel): copier `.env.example` en `.env` et ajuster.
4. Lancer l'API:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Docs OpenAPI: http://127.0.0.1:8000/docs

## Configuration (Pydantic Settings)
Variables (préfixe APP_):
- APP_ENV: local | cloud | gcp | aws (défaut: local)
- APP_LOG_LEVEL: DEBUG | INFO | WARNING | ERROR | CRITICAL (défaut: INFO)
- APP_CAT_FACT_BASE_URL: URL base de l'API publique (défaut: https://catfact.ninja)
- APP_HTTP_TIMEOUT_SECONDS: timeout des requêtes httpx (défaut: 10.0)

Voir `app/config/settings.py`.

## Logging
- local: format lisible console
- cloud/gcp/aws: format JSON (compatible agrégation de logs)

Voir `app/infrastructure/logging/config.py`.

## Endpoints
- GET `/v1/facts/random` → récupère un fact aléatoire depuis l'API publique (via service/adapter). Réponse:
  ```json
  { "text": "...", "source": "catfact.ninja" }
  ```

## Tests
- Unitaires: `pytest tests/unit -q`
- Intégration (réseau): `pytest tests/integration -q`
- E2E: `pytest tests/e2e -q`
- BDD (pytest-bdd): `pytest tests/bdd -q`
- Tous: `pytest -q`

Les tests E2E/BDD surchargent la DI pour stubber l'usage de réseau.

## Principes d'architecture
- Domain: entités/services (purs, sans dépendances techniques)
- Application: use cases orchestrant les services
- Infrastructure: adapters (httpx, providers, logging)
- Interface: API FastAPI (contrats via schémas Pydantic)

L'appel HTTP est encapsulé dans `HttpClient` et son implémentation `HttpxHttpClient`; le domaine/UC parle à l'interface métier `CatFactProvider`, et l'implémentation `CatFactHttpProvider` utilise le client HTTP.

## Remplacements/extension
- Pour changer de fournisseur: implémentez `CatFactProvider` et remplacez le binding dans `di/container.py`.
- Pour un autre client HTTP: implémentez `HttpClient`.

## Qualité & bonnes pratiques
- Typage strict, fonctions asynchrones, dépendances injectées via Annotated/Depends
- Séparation stricte métier/technique (Clean Architecture, SOLID)
- Tests multi-niveaux (TDD/DDD/BDD prêts)

## Licence
MIT
