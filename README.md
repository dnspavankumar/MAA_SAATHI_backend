# VitalSync - Smart Health Monitoring System Backend

Production-quality backend for IoT-based healthcare platform using ESP32 smart ring.

## Features

- IoT data ingestion from ESP32 devices
- Health check simulation (frontend-triggered)
- Health analytics and reporting
- Severity-based emergency alert system
- Firebase Firestore database
- RESTful API with FastAPI

## Tech Stack

- Python 3.10+
- FastAPI
- Firebase Admin SDK
- Uvicorn
- Pydantic

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Firebase:
   - Download your Firebase service account key
   - Save as `serviceAccountKey.json` in project root

3. Create `.env` file:
```bash
cp .env.example .env
```

Add Twilio values in `.env` to enable call/SMS features:

```env
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000

## API Documentation

Interactive docs: http://localhost:8000/docs

### Endpoints

- `POST /api/v1/iot/daily-vitals` - Receive vitals from IoT device
- `GET /api/v1/health/daily-vitals/{patientId}` - Get patient vitals
- `POST /api/v1/health/check/{patientId}` - Simulate health check
- `GET /api/v1/health/report/{patientId}` - Generate health report
- `POST /api/v1/emergency/sos` - Create emergency alert
- `GET /api/v1/alerts/{patientId}` - Get patient alerts
- `PATCH /api/v1/alerts/{alertId}` - Update alert status
- `POST /sms` and `POST /api/v1/communication/sms` - Send SMS
- `POST /call` and `POST /api/v1/communication/call` - Make voice calls
- `POST /sos` and `POST /api/v1/communication/sos` - Priority-based SOS notify
- `GET /health` - Health check

## Project Structure

```
app/
├── routes/          # API endpoints
├── controllers/     # Request handlers
├── services/        # Business logic
├── schemas/         # Pydantic models
├── config/          # Configuration
└── utils/           # Utilities
```

## Architecture

- PUSH-BASED IoT model (devices send data to backend)
- Backend never calls IoT devices
- Health check is simulated (UX-driven)
- Frontend uses GET APIs (refresh-based)

## License

MIT
