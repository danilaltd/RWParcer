# RWParcer

**RWParcer** is a .NET application that parses rw.by data and provides train subscriptions with notifications on changing seats.

---

## Project Structure

- `RWParcer/` — bot application, command routing, configuration, and session integration.
- `RWParcerCore/` — domain logic, entities, repositories, services, interfaces, and database infrastructure.
- `RWParcerCore.Tests/` — unit tests.
- `proxy-manager/` — lightweight proxy health-check and routing service used by the main app.
- `docker-compose.yml` — single deployment file for local, dev, and production environments via environment overrides.
- `Dockerfile` — main application image build instructions.
- `env/` — example configuration (appsettings, data, logging).

---

## Key Technologies

- .NET (C#)
- Entity Framework Core (migrations and database access)
- PostgreSQL
- Docker + docker-compose

---

## Quick Start (Local Deployment)

### 1) Prerequisites

1. Make sure you have installed:
   - Docker & Docker Compose

2. Review / update configuration in `env/appsettings.json` as needed.

### 2) Run with Docker Compose

For local development:

```sh
git clone https://github.com/danilaltd/RWParcer
cd RWParcer
docker compose -f docker-compose.yml up --build
```

This starts:
- the main `parcer` service (built from `Dockerfile`)
- the `proxy-manager` service (built from `proxy-manager/Dockerfile`)

For dev/prod deployment, set the environment variables you need and run:

```sh
docker compose -f docker-compose.yml up -d
```

Examples:
- `DATA_DIR=/var/lib/rwparcer-dev/data PROXY_FILE_PATH=/var/lib/rwparcer-dev/proxies.txt docker compose -f docker-compose.yml up -d`
- `PARSER_IMAGE=ghcr.io/<owner>/rwparcer:dev-latest PROXY_MANAGER_IMAGE=ghcr.io/<owner>/rwparcer-proxy-manager:dev-latest docker compose -f docker-compose.yml up -d`

> To stop the stack, run `docker compose -f docker-compose.yml down`.

---

## How the Project Works (High-Level)

1. `Program.cs` initializes DI, loads configuration, and registers services.
2. `BotService` (or `CommandRouter`) handles incoming commands and calls into `RWParcerCore`.
3. `RWParcerCore` contains business logic, domain entities, and repository implementations.
4. Sessions/state are persisted to the database (PostgreSQL/SQLite) via `SessionDbContext`.

---

## CI/CD Pipeline (GitHub Actions)

The project uses **GitHub Actions** with a three-stage workflow defined in `.github/workflows/main.yml`:

### Pipeline Overview

```
Push to main branch
    ↓
[ci-checks] (github-hosted ubuntu-latest)
  - Secret detection (Gitleaks)
  - .NET build check
  - Optional: Unit tests
    ↓
[build] (github-hosted ubuntu-latest)
  - Build Docker images
  - Push to GitHub Container Registry (ghcr.io)
    ↓
[deploy] (self-hosted runner)
  - Pull and deploy using docker-compose
  - Apply runtime configuration from secrets
```

### Stage Details

#### 1. `ci-checks` Job (GitHub-hosted Ubuntu)

Runs code quality and build validation:

- **Secret Detection** — Gitleaks scans for accidentally committed secrets.
- **Setup .NET** — Uses .NET 8.0.x SDK.
- **Restore & Build** — Restores NuGet dependencies and builds in Release mode.

#### 2. `build` Job (GitHub-hosted Ubuntu)

Builds and publishes Docker images:

```yaml
- Builds two images:
  - ghcr.io/<owner>/rwparcer:<env>-latest (main application)
  - ghcr.io/<owner>/rwparcer-proxy-manager:<env>-latest (proxy-manager service)
- Waits for ci-checks job to pass
- Pushes both images to GitHub Container Registry
- Requires GITHUB_TOKEN permissions
```

#### 3. `deploy` Job (Self-hosted Runner)

Deploys the application to production:

- Checks out code
- Creates `./env/` directory
- Injects `appsettings.json` from GitHub Secrets
- Pulls latest images from ghcr.io
- Runs `docker compose -f docker-compose.yml up -d` to deploy/update services

---

## Self-Hosted Runner Setup

### Prerequisites

The self-hosted runner must be configured on a **production/staging server** with:

1. **Docker & Docker Compose** installed
2. **GitHub Runner** installed and registered

### Environment & Permissions

Ensure the runner can:
- Execute `docker` and `docker compose` commands
- Read/write to `/var/lib/rwparcer/data` and `/var/lib/rwparcer/proxies.txt`
- Access GitHub Container Registry (via `docker login`)

---

## GitHub Secrets Configuration

The CI/CD pipeline requires these secrets configured in **GitHub Settings → Secrets and variables → Actions**:

### Required Secrets

#### `GITHUB_TOKEN` (auto-provided)
- Default token, used for:
  - Container registry authentication
  - Wait-on-check workflow step

#### `PROD_APP_SETTINGS_JSON` / `DEV_APP_SETTINGS_JSON` (manual setup required)
- Complete `appsettings.json` content as a multiline secret for the corresponding environment
- Example structure:
  ```json
  {
    "BotSettings": {
      "Token": "your-bot-token"
    },
    "DatabaseSettings": {
      "ConnectionString": "Server=parcer-db;..."
    },
    "ProxySettings": {
      "ProxyRotationEnabled": true
    },
    "Logging": {
      "LogLevel": {
        "Default": "Information",
        "Microsoft": "Warning"
      }
    }
  }
  ```

### Setup Steps

1. Go to **GitHub Repository → Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `PROD_APP_SETTINGS_JSON` (production) or `DEV_APP_SETTINGS_JSON` (development)
4. Value: Paste the full `appsettings.json` content for that environment
5. Save

---

## Proxy Manager Service

### Role

`proxy-manager` is the current proxy-routing component used to:
- health-check and score available proxies
- choose a working proxy for each outgoing request
- report failures back to the proxy pool

### Architecture

In `docker-compose.yml`, the service is configured as:

```yaml
services:
  proxy-manager:
    image: ghcr.io/danilaltd/rwparcer-proxy-manager:prod-latest
    volumes:
      - /var/lib/rwparcer/proxies.txt:/app/proxies.txt:ro
    environment:
      PROXY_MANAGER_PORT: 8080
      HEALTH_CHECK_INTERVAL: 30
    restart: always
```

### How It Works

- `proxy-manager` loads proxies from `proxy-manager/proxies.txt`.
- It periodically checks each proxy with TCP health checks and updates scores.
- The main app reaches it via `PROXY_MANAGER_URL` and uses the returned proxy for HTTP requests.

### Integration with Main Application

The main `parcer` service communicates with the manager through:

```yaml
services:
  parcer:
    environment:
      PROXY_MANAGER_URL: http://proxy-manager:8080
```

The application code in `RWParcerCore/Infrastructure` uses `HttpClientFactoryWithProxyRotation` to:
1. ask the manager for the next healthy proxy
2. route the request through it
3. report success/failure back to the manager for score updates

---

## Deployment Flow (End-to-End)

### Local Development

```bash
docker compose -f docker-compose.local.yml up --build
```

Starts both `proxy-manager` and `parcer` locally for development.

### CI/CD Deployment

1. **Developer** pushes to `main` branch
2. **GitHub Actions** triggered automatically:
   - Runs `ci-checks` (linting, build)
   - Builds Docker images (`rwparcer` + `rwparcer-proxy-manager`)
   - Pushes to ghcr.io
3. **Self-hosted runner** pulls latest images
4. **Production deployment** via `docker compose pull && docker compose up -d`

### Rollback

If deployment fails:
```bash
# On self-hosted machine
docker compose down
docker compose up -d --remove-orphans
```