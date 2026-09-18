# Docker Production Deployment Guide

This guide covers deploying SkyLines in production using Docker Compose.

## Overview

SkyLines runs as a set of containerized services:

| Service | Purpose | Protocol | Port |
|---------|---------|----------|------|
| `api` | Flask web app (Ember SPA + REST API) | HTTP | 5000 (internal) |
| `worker` | Celery background tasks (flight analysis) | — | — |
| `tracking` | XCSoar live tracking server | UDP | 5597 |
| `mapproxy` | Tile server (MapServer backend) | HTTP | 9109 (internal) |
| `db` | PostgreSQL + PostGIS | TCP | 5432 (internal) |
| `redis` | Celery broker and cache | TCP | 6379 (internal) |
| `caddy` | Reverse proxy with TLS | TCP | 80, 443 |

## Prerequisites

- Linux server (Ubuntu 22.04+, Debian 11+, or similar)
- Docker Engine 24.0+ and Docker Compose v2.20+
- External reverse proxy for TLS termination (nginx, AWS ALB, Cloudflare, etc.)
- At least 2GB RAM, 20GB disk space

### Install Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/skylines-project/skylines.git
cd skylines
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set the required values:

```bash
# Generate a secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Set a strong database password
POSTGRES_PASSWORD=$(openssl rand -hex 16)

# External proxy mode (default): TLS handled by your reverse proxy
DOMAIN=localhost
TLS_EMAIL=
```

### 3. Start services

```bash
docker compose -f docker-compose.prod.yml up -d
```

### 4. Verify deployment

```bash
# Check service status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Test the API (via your external proxy, or directly on port 80)
curl -A "test-agent" http://localhost/api/
```

## Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_PASSWORD` | Database password | `your-secure-password` |
| `SECRET_KEY` | Flask session secret | `openssl rand -hex 32` |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOMAIN` | `localhost` | Domain for in-compose Caddy (use `localhost` with external proxy) |
| `TLS_EMAIL` | (empty) | Let's Encrypt email; empty = no auto-TLS (external proxy mode) |

| `POSTGRES_USER` | `skylines` | Database username |
| `POSTGRES_DB` | `skylines` | Database name |
| `GUNICORN_WORKERS` | `4` | API worker processes |
| `MAPPROXY_WORKERS` | `4` | MapProxy worker processes |
| `SMTP_SERVER` | `localhost` | SMTP server for emails |
| `EMAIL_FROM` | `SkyLines <no-reply@skylines.aero>` | Email sender address |
| `HTTP_PORT` | `80` | HTTP port |
| `HTTPS_PORT` | `443` | HTTPS port |
| `TRACKING_PORT` | `5597` | UDP tracking port |

## TLS Configuration

The default configuration expects an **external reverse proxy** (nginx, AWS ALB,
Cloudflare, Traefik, etc.) to handle TLS termination and forward plain HTTP to
the compose stack on port 80.

### External TLS Termination (Default)

Use the default settings:

```bash
DOMAIN=localhost
TLS_EMAIL=
```

Configure your external reverse proxy to:
- Terminate TLS and forward HTTP to the compose stack on port 80
- Forward UDP 5597 for live tracking (if using a network load balancer)

The in-compose Caddy container still provides routing, health checks, and
security headers, but does not handle TLS.

### Optional: Automatic TLS via Caddy

If you prefer Caddy to obtain Let's Encrypt certificates directly (no external
proxy), set `DOMAIN` and `TLS_EMAIL`:

```bash
DOMAIN=skylines.example.com
TLS_EMAIL=admin@example.com
```

**Requirements:**
- Ports 80 and 443 must be directly accessible from the internet
- DNS must point to your server
- Valid email address for certificate notifications

### Optional: Custom Certificates

Mount your certificates and modify `docker/Caddyfile.prod`:

```caddy
your-domain.com {
    tls /path/to/cert.pem /path/to/key.pem
    # ... rest of config
}
```

## Network Ports

Ensure these ports are accessible:

| Port | Protocol | Purpose |
|------|----------|---------|
| 80 | TCP | HTTP (plain; TLS handled by external proxy) |
| 443 | TCP | HTTPS (only if using in-compose Caddy auto-TLS) |
| 5597 | UDP | XCSoar live tracking |

For cloud deployments, add these to your security group or firewall rules.

## Persistent Data

Data is stored in Docker volumes:

| Volume | Contents | Backup Priority |
|--------|----------|-----------------|
| `postgres_data` | PostgreSQL database | **Critical** |
| `files_data` | IGC flight files | **Critical** |
| `caddy_data` | TLS certificates | Recommended |
| `caddy_config` | Caddy config cache | Low |

### Backup Strategy

```bash
# Backup PostgreSQL
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U skylines skylines > backup-$(date +%Y%m%d).sql

# Backup IGC files (find volume mount point)
docker volume inspect skylines_files_data --format '{{ .Mountpoint }}'
# Then backup that directory
```

### Restore from Backup

```bash
# Restore PostgreSQL
docker compose -f docker-compose.prod.yml exec -T db \
  psql -U skylines skylines < backup.sql
```

## Managing Services

```bash
# Start all services
docker compose -f docker-compose.prod.yml up -d

# Stop all services
docker compose -f docker-compose.prod.yml down

# Restart a specific service
docker compose -f docker-compose.prod.yml restart api

# View logs
docker compose -f docker-compose.prod.yml logs -f api

# Scale workers (if needed)
docker compose -f docker-compose.prod.yml up -d --scale worker=2

# Update to latest image
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

## Database Migrations

Migrations run automatically on startup via the `migrate` service. For manual operations:

```bash
# Run migrations
docker compose -f docker-compose.prod.yml run --rm api \
  python manage.py migrate upgrade

# Create fresh database (destructive!)
docker compose -f docker-compose.prod.yml run --rm api \
  python manage.py db create
```

## Importing Data

SkyLines uses external datasets for airspace, airports, and terrain:

```bash
# Import airspace data (OpenAir format)
docker compose -f docker-compose.prod.yml run --rm api \
  python manage.py import airspace /path/to/airspace.txt

# Import Welt2000 airport database
docker compose -f docker-compose.prod.yml run --rm api \
  python manage.py import welt2000 /path/to/WELT2000.TXT

# Import Mountain Wave Project data
docker compose -f docker-compose.prod.yml run --rm api \
  python manage.py import mwp /path/to/mwp.txt
```

## Monitoring

### Health Checks

All services include health checks. View status:

```bash
docker compose -f docker-compose.prod.yml ps
```

Caddy exposes a `/health` endpoint:

```bash
curl http://localhost/health
```

### Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f api

# With timestamps
docker compose -f docker-compose.prod.yml logs -f -t api
```

### Resource Usage

```bash
docker stats
```

## Troubleshooting

### Services not starting

```bash
# Check service status
docker compose -f docker-compose.prod.yml ps

# Check logs for errors
docker compose -f docker-compose.prod.yml logs api
docker compose -f docker-compose.prod.yml logs db
```

### Database connection issues

```bash
# Verify database is running
docker compose -f docker-compose.prod.yml exec db pg_isready

# Test connection
docker compose -f docker-compose.prod.yml exec api \
  python -c "from skylines.database import db; print(db.engine.execute('SELECT 1').scalar())"
```

### TLS certificate issues

```bash
# Check Caddy logs
docker compose -f docker-compose.prod.yml logs caddy

# Verify certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

### Live tracking not working

Ensure UDP port 5597 is open:

```bash
# From another machine
nc -u your-server-ip 5597
```

Check firewall rules allow UDP traffic.

## Upgrading

### Minor updates

```bash
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

### Database migrations

Migrations run automatically. For major upgrades, backup first:

```bash
# Backup
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U skylines skylines > backup-pre-upgrade.sql

# Upgrade
docker compose -f docker-compose.prod.yml down
git pull
docker compose -f docker-compose.prod.yml up -d

# Verify
docker compose -f docker-compose.prod.yml logs migrate
```

## Security Considerations

1. **Never commit `.env`** — It contains secrets
2. **Use strong passwords** — Generate with `openssl rand -hex 32`
3. **Keep Docker updated** — Regularly update Docker and base images
4. **Limit network access** — Only expose required ports
5. **Enable firewall** — Use ufw or iptables to restrict access
6. **Regular backups** — Automate PostgreSQL and file backups
7. **Monitor logs** — Watch for suspicious activity

## Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| Compose file | `docker-compose.yml` | `docker-compose.prod.yml` |
| Caddyfile | `docker/Caddyfile` | `docker/Caddyfile.prod` |
| TLS | Disabled | External proxy (default) or Caddy auto-TLS |
| Debug mode | Enabled | Disabled |
| Credentials | Hardcoded | Environment variables |
| Restart policy | `on-failure` | `unless-stopped` |
| Volumes | Source mounts | Named volumes only |
