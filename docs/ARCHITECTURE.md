# SkyLines Architecture

This document gives a high-level overview of how SkyLines is structured and how
data flows through the system. It answers the "draw and share the architecture
and working flow" request from
[issue #2484](https://github.com/skylines-project/skylines/issues/2484).

SkyLines is an open-source web platform for soaring/gliding pilots to share
flights, view rankings, and use live GPS tracking. Production runs at
<https://skylines.aero>.

## Tech stack

| Layer | Technology |
| --- | --- |
| Frontend | Ember.js 3.24 (Glimmer components), Bootstrap 3, OpenLayers 5 (2D), Cesium (3D) |
| Auth | OAuth 2 password grant (`ember-simple-auth` ↔ `flask-oauthlib`), Bearer tokens |
| API | Flask 1.1, 17 resource blueprints, `webargs`/voluptuous request validation |
| ORM / DB | SQLAlchemy + GeoAlchemy2 on PostgreSQL 10 + PostGIS 2.5, Alembic migrations |
| Async tasks | Celery 3 with Redis as broker + result backend |
| Live tracking | gevent UDP server speaking the XCSoar binary protocol (port 5597) |
| Flight analysis | `xcsoar` C++ Python extension (scoring, phases, contest legs) |
| Maps | MapProxy (tile cache/WSGI) in front of MapServer `.map` files |
| File storage | IGC logs on disk (`SKYLINES_FILES_PATH`), keyed by `IGCFile.filename` |

## System architecture

One Docker image runs as several processes, each started with a different
command. Stateful backends (Postgres, Redis, file storage) are shared.

```mermaid
graph TB
    subgraph client[Client]
        B[Browser: Ember SPA]
        X[XCSoar / LK8000 / trackers]
    end

    subgraph edge[Edge]
        P[Caddy / Ingress reverse proxy]
    end

    subgraph app[Application processes - one image, different commands]
        W[web: Gunicorn - create_combined_app<br/>serves Ember static + /api]
        WK[worker: Celery]
        TR[tracking: gevent UDP server :5597]
        MP[mapproxy: Gunicorn :9109]
    end

    subgraph data[Stateful backends]
        PG[(PostgreSQL + PostGIS)]
        RD[(Redis - Celery broker/result)]
        FS[/Flight files: IGC on disk or S3/]
    end

    MS[MapServer .map files]

    B -->|HTTPS /api/*, static| P
    P --> W
    P -->|/mapproxy/*| MP
    X -->|UDP binary protocol| TR

    W --> PG
    W --> RD
    W --> FS
    WK --> PG
    WK --> RD
    WK --> FS
    TR --> PG
    MP --> PG
    MP --> MS
    MS --> PG
```

## App-factory layering

The Flask application is composed in layers in `skylines/app.py`. The frontend
and API are separate WSGI apps combined via `DispatcherMiddleware`, with the API
mounted at `/api`.

```mermaid
graph LR
    A[create_app<br/>SQLAlchemy + Sentry] --> H[create_http_app<br/>+ logging + Celery]
    H --> F[create_frontend_app<br/>+ Ember SPA serving]
    H --> API[create_api_app<br/>+ OAuth + cache + blueprints]
    F --> C[create_combined_app<br/>frontend + API at /api]
    API --> C
```

The browser talks almost exclusively to the JSON API under `/api`. There is
**no Ember Data** — routes and components call `this.ajax.request('/api/...')`
and parse plain JSON. Side channels that do *not* go through the REST API are
map tiles (`/mapproxy`), the live-tracking UDP ingress, and the LiveTrack24
compatibility endpoints.

## Working flow 1 — flight upload & analysis

```mermaid
sequenceDiagram
    participant U as Browser (Ember)
    participant API as web (Flask /api)
    participant DB as PostgreSQL
    participant F as File store
    participant Q as Redis
    participant WK as Celery worker
    participant XC as xcsoar (C++ ext)

    U->>API: POST /api/flights/upload (IGC, Bearer token)
    API->>API: md5, dedup check (IGCFile.by_md5)
    API->>F: store IGC bytes
    API->>DB: insert IGCFile + Flight rows
    API->>Q: enqueue analyse_flight(flight_id)
    API-->>U: 200 (upload accepted)
    WK->>Q: pull task
    WK->>F: read IGC by key
    WK->>XC: analyse (scores, phases, contest legs)
    WK->>DB: write track geometry, phases, FlightPathChunks
    WK->>DB: find_meetings (nearby flights)
```

## Working flow 2 — live tracking

```mermaid
sequenceDiagram
    participant T as XCSoar / tracker
    participant TS as tracking (UDP :5597)
    participant DB as PostgreSQL
    participant API as web (Flask /api)
    participant U as Browser (Ember)

    T->>TS: UDP binary fix (id, lat/lon, alt, CRC)
    TS->>TS: validate CRC, decode
    TS->>DB: insert TrackingFix / TrackingSession
    U->>API: GET /api/live or /api/live/<user_ids>
    API->>DB: query recent fixes
    API-->>U: JSON positions -> OpenLayers/Cesium map
```

## Codebase map

```
skylines/            # Main Python package
├── app.py           # Flask app factory (create_app, create_api_app, ...)
├── database.py      # Flask-SQLAlchemy db instance
├── model/           # ORM models (User, Flight, Club, Airport, TrackingFix, ...)
├── api/             # REST API
│   ├── views/       # Flask blueprints — 17 resource modules
│   ├── oauth.py     # OAuth 2 provider (access/refresh tokens)
│   └── cache.py     # Flask-Caching
├── frontend/views/  # Serves built Ember SPA + static files + LiveTrack24
├── lib/             # Utilities (geo, IGC parsing, xcsoar analysis, SQL helpers)
├── schemas/         # Request validation (voluptuous/webargs)
├── worker/          # Celery tasks (analyse_flight, find_meetings, upload_to_weglide)
├── tracking/        # UDP tracking server (gevent DatagramServer)
└── commands/        # CLI subcommands for manage.py

ember/               # Ember.js frontend SPA
config/              # Python app config (default.py, testing.py, docker.py)
migrations/          # Alembic migration versions
mapproxy/            # MapProxy config (mapproxy.yaml)
mapserver/           # MapServer map files (airspace, airports, MWP)
```

## Deployment (processes)

Production requires four long-running processes plus a migration step:

| Process | Command | Protocol | Notes |
| --- | --- | --- | --- |
| `web` | Gunicorn `wsgi_skylines:application` | HTTP | Ember static + `/api` in one app |
| `worker` | `manage.py celery runworker` | — (Redis) | Flight analysis, meetings, WeGlide |
| `tracking` | `manage.py tracking runserver` | UDP 5597 | XCSoar live fixes |
| `mapproxy` | Gunicorn `wsgi_mapproxy:application` | HTTP 9109 | Tiles/WMS in front of MapServer |
| `migrate` | `manage.py migrate upgrade` | — | One-shot before the others start |

Docker Compose (`docker-compose.yml`) orchestrates all of them together with
PostGIS, Redis, and Caddy as the reverse proxy.
