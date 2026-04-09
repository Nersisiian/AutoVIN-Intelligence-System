## AutoVIN Intelligence System

Production-ready full-stack VIN decoding platform.

### Features
- **VIN decode**: `POST /decode-vin` (17-char validation, async)
- **Local decode**: WMI/VDS/VIS parsing + country + model-year inference
- **External decode**: NHTSA VPIC integration (free) + VINDecoder (paid if key, deterministic mock if not)
- **AI fallback**: embedded ML estimator to fill gaps when data is sparse
- **Caching**: Redis (24h TTL)
- **Rate limiting**: global per-IP limits
- **Persistence**: PostgreSQL stores decode records
- **Frontend**: React + Tailwind dashboard UI
- **DevOps**: Docker + docker-compose, GitHub Actions CI/CD
- **CLI**: `vin-decoder <VIN>` (calls the API)

### Architecture (high level)
```mermaid
flowchart LR
  U[User] --> F[React + Tailwind Frontend]
  F -->|POST /decode-vin| B[FastAPI Backend]
  B --> R[(Redis Cache)]
  B --> P[(PostgreSQL)]
  B --> N[NHTSA VPIC API]
  B --> V[VINDecoder API or Mock]
  B --> A[AI Estimator (sklearn)]
```

### Screenshot
![Dashboard screenshot](docs/dashboard-screenshot.svg)

### Quick start (one command)
Copy env file:

```bash
cp .env.example .env
```

Run everything:

```bash
docker-compose up --build
```

Then open:
- **Frontend**: `http://localhost:15173`
- **Backend**: `http://localhost:18000/docs`

### API usage
Decode a VIN:

```bash
curl -sX POST "http://localhost:18000/decode-vin" \
  -H "Content-Type: application/json" \
  -d "{\"vin\":\"1HGCM82633A004352\"}" | jq
```

### CLI usage
From the backend container or locally (python installed):

```bash
vin-decoder 1HGCM82633A004352 --pretty
```

If the API is not on localhost:

```bash
AUTOVIN_API_URL=http://localhost:18000 vin-decoder 1HGCM82633A004352 --pretty
```

### Notes on recall / accident history
The API response includes fields (`recalls`, `accident_history`) for future providers. You can plug in additional services in `backend/app/services/`.

