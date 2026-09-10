# MiniSOC API

A lightweight defensive Security Operations Center (SOC) API built with Python and FastAPI.

MiniSOC is a portfolio-grade blue-team project that demonstrates security event ingestion, detection engineering, risk scoring, alert generation, API authentication, testing, and containerization.

## Architecture

```text
Windows Event Log
        |
        v
PowerShell Collector
        |
        v
  POST /api/v1/events
        |
        v
+-------------------+
| Detection Engine  |
| Risk + Severity   |
+-------------------+
        |
   +----+----+
   |         |
 Event DB   Alert DB
   |         |
   +----+----+
        |
        v
 GET /api/v1/alerts
```

## Features

- Security event ingestion
- Windows Security Event Log collector
- Failed-login and brute-force detection
- Risk scoring and severity classification
- SOC alert generation
- MITRE ATT&CK mapping (`T1110` — Brute Force)
- API key authentication with `X-API-Key`
- Event and alert filtering
- SQLite development database
- Pydantic input validation
- Automated tests
- OpenAPI/Swagger documentation
- Docker and GitHub Actions support

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/hackura/minisocAPI.git
cd minisocAPI
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS/WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set the API key

Windows PowerShell:

```powershell
$env:MINISOC_API_KEY="dev-minisoc-key"
```

Linux/macOS/WSL:

```bash
export MINISOC_API_KEY="dev-minisoc-key"
```

For production, use a long random secret and never commit it to GitHub.

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

The API will normally be available at `http://127.0.0.1:8000`.

## How to get/use the APIs

FastAPI automatically generates interactive API documentation.

Once the server is running, open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

In Swagger UI, click **Authorize** and provide the API key in the `X-API-Key` header. You can then execute requests directly from the browser.

### Health check

```bash
curl http://127.0.0.1:8000/health
```

### Send a security event

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/events" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-minisoc-key" \
  -d '{
    "event_type": "failed_login",
    "username": "admin",
    "source_ip": "198.51.100.10",
    "message": "SSH authentication failed"
  }'
```

### View events

```bash
curl "http://127.0.0.1:8000/api/v1/events?limit=20" \
  -H "X-API-Key: dev-minisoc-key"
```

### View alerts

```bash
curl "http://127.0.0.1:8000/api/v1/alerts" \
  -H "X-API-Key: dev-minisoc-key"
```

### Filter events

```text
GET /api/v1/events?severity=critical&limit=20
```

### Filter alerts

```text
GET /api/v1/alerts?severity=critical&status=open
```

## Windows log collector

MiniSOC includes a PowerShell collector at `collector/windows_collector.ps1`.

The collector reads recent Windows **Security** event logs and converts selected Windows events into the normalized MiniSOC event format.

Currently:

- Event ID `4625` → `failed_login`
- Event ID `4624` → `successful_login`
- Other Security events → `windows_security_event`

### Run the collector

Start MiniSOC first, then in an elevated PowerShell window:

```powershell
$env:MINISOC_API_KEY="dev-minisoc-key"
Set-ExecutionPolicy -Scope Process Bypass
.\collector\windows_collector.ps1
```

Optional parameters:

```powershell
.\collector\windows_collector.ps1 `
  -ApiUrl "http://127.0.0.1:8000/api/v1/events" `
  -ApiKey "dev-minisoc-key" `
  -MaxEvents 50 `
  -HoursBack 2
```

The collector is intended for a controlled lab environment. Windows Security log access may require administrator privileges and appropriate local audit policy configuration.

## API endpoints

| Method | Endpoint | Authentication | Purpose |
|---|---|---|---|
| GET | `/health` | No | Service health check |
| POST | `/api/v1/events` | API key | Ingest a security event |
| GET | `/api/v1/events` | API key | List/filter events |
| GET | `/api/v1/alerts` | API key | List/filter SOC alerts |

## Detection logic

MiniSOC tracks failed authentication events by source IP within a rolling 10-minute window.

- 1–2 failures: low risk
- 3–4 failures: medium risk
- 5+ failures: critical risk and a SOC alert

The brute-force alert is mapped to MITRE ATT&CK technique `T1110`.

## Testing

```bash
pytest -q
```

## Docker

```bash
docker compose up --build
```

## Example integration

MiniSOC can receive events from Windows event collectors, Linux authentication logs, endpoint scripts, network sensors, or another application. A collector only needs to send normalized JSON to `POST /api/v1/events` with the API key.

## Project status

🚧 Active development. The current release is the secure API foundation plus a Windows Security Event Log collector; future milestones include JWT/RBAC, richer detection rules, IP reputation enrichment, persistent rule configuration, dashboards, PostgreSQL deployment, and production observability.

## License

MIT
