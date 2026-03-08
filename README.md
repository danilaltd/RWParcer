# RWParcer

**RWParcer** is a .NET application that parses rw.by data and provides train subscriptions with notifications on changing seats.

---

## Project Structure

- `RWParcer/` — application containing the bot, command routing, configuration, and session store integration.
- `RWParcerCore/` — domain logic, entities, repositories, services, interfaces, and database infrastructure.
- `RWParcerCore.Tests/` — unit tests.
- `docker-compose.yml` — environment definition for running app and required proxies.
- `Dockerfile` / `Dockerfile.psiphon` — application image build instructions.
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

```sh
git clone https://github.com/danilaltd/RWParcer
cd RWParcer
docker compose up --build
```

This will start:
- the application service (built from `Dockerfile`)
- required proxies

> To stop, run `docker compose down`.

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
  - ghcr.io/<owner>/rwparcer:latest (main application)
  - ghcr.io/<owner>/rwparcer-psiphon:latest (proxy service)
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
- Runs `docker compose up -d` to deploy/update services

---

## Self-Hosted Runner Setup

### Prerequisites

The self-hosted runner must be configured on a **production/staging server** with:

1. **Docker & Docker Compose** installed
2. **GitHub Runner** installed and registered

### Environment & Permissions

Ensure the runner can:
- Execute `docker` and `docker compose` commands
- Read/write to `/var/lib/rwparcer/data`
- Access GitHub Container Registry (via `docker login`)

---

## GitHub Secrets Configuration

The CI/CD pipeline requires these secrets configured in **GitHub Settings → Secrets and variables → Actions**:

### Required Secrets

#### `GITHUB_TOKEN` (auto-provided)
- Default token, used for:
  - Container registry authentication
  - Wait-on-check workflow step

#### `APP_SETTINGS_JSON` (manual setup required)
- Complete `appsettings.json` content as a multiline secret
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
3. Name: `APP_SETTINGS_JSON`
4. Value: Paste full `appsettings.json` content
5. Save

---

## Psiphon Proxy Service

### Role

Psiphon is a **proxy/VPN service** used to:
- Rotate IP addresses for web scraping (rw.by requires proxy rotation)
- Distribute requests across multiple proxy instances
- Bypass IP-based rate limiting

### Architecture

In `docker-compose.yml`, the Psiphon service is configured with:

```yaml
services:
  psiphon:
    image: ghcr.io/danilaltd/rwparcer-psiphon:latest
    volumes:
      - /var/lib/rwparcer/data:/app/data
    environment:
      NODE_ID_FROM_HOSTNAME: "1"
      replicas: 10          # 10 parallel proxy instances
    restart: always
```

### How It Works

- **10 Replicas** — 10 independent proxy nodes running in parallel
- **Shared Data Volume** — All replicas share `/var/lib/rwparcer/data` for state/logging
- **NODE_ID_FROM_HOSTNAME** — Each replica gets a unique ID from its hostname
- **Always Restart** — Automatically restarts if a replica fails

### Integration with Main Application

The main `parcer` service communicates with Psiphon replicas:

```yaml
services:
  parcer:
    environment:
      PSIPHON_REPLICAS: 10     # Number of proxy instances to connect to
```

The application code (in `RWParcerCore/Infrastructure`) uses `HttpClientFactoryWithProxyRotation` to:
1. Select a random Psiphon replica
2. Route HTTP requests through it
3. Rotate to next replica on next request (load balancing)

---

## Deployment Flow (End-to-End)

### Local Development

```bash
docker compose up --build
```

Starts both `psiphon` (10 replicas) and `parcer` (main app) locally.

### CI/CD Deployment

1. **Developer** pushes to `main` branch
2. **GitHub Actions** triggered automatically:
   - Runs `ci-checks` (linting, build)
   - Builds Docker images (`rwparcer` + `rwparcer-psiphon`)
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