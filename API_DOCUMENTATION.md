# VitalSync API Documentation

Base URL: `http://localhost:8000`

## Authentication
Currently no authentication required (add JWT/API keys for production)

---

## Endpoints

### 1. Health Check
**GET** `/health`

Check if the server is running.

**Response:**
```json
{
  "status": "ok",
  "service": "VitalSync"
}
```

---

### 2. IoT Data Ingestion
**POST** `/api/v1/iot/daily-vitals`

Receive daily vitals from ESP32 IoT device.

**Request Body:**
```json
{
  "patientId": "patient_001",
  "heartRateAvg": 75.5,
  "spo2Avg": 98.2,
  "steps": 8500,
  "sleepHours": 7.5,
  "temperatureAvg": 36.8,
  "date": "2024-03-24"
}
```

**Validation Rules:**
- `heartRateAvg`: 0-300 bpm
- `spo2Avg`: 0-100%
- `steps`: >= 0
- `sleepHours`: 0-24 hours
- `temperatureAvg`: 30-45°C
- `date`: YYYY-MM-DD format

**Response:**
```json
{
  "success": true,
  "message": "Vitals data received and stored successfully",
  "data": {
    "patientId": "patient_001",
    "date": "2024-03-24"
  }
}
```

---

### 3. Get Daily Vitals
**GET** `/api/v1/health/daily-vitals/{patientId}?days=7`

Retrieve patient vitals for last N days.

**Parameters:**
- `patientId` (path): Patient identifier
- `days` (query): Number of days (1-90, default: 7)

**Response:**
```json
{
  "success": true,
  "patientId": "patient_001",
  "count": 7,
  "data": [
    {
      "heartRateAvg": 75.5,
      "spo2Avg": 98.2,
      "steps": 8500,
      "sleepHours": 7.5,
      "temperatureAvg": 36.8,
      "date": "2024-03-24",
      "timestamp": "2024-03-24T10:30:00"
    }
  ]
}
```

---

### 4. Health Check Simulation
**POST** `/api/v1/health/check/{patientId}`

Simulate real-time health check (frontend-triggered).

**Parameters:**
- `patientId` (path): Patient identifier

**Behavior:**
- Adds 1-2 second delay (simulates sensor reading)
- Returns latest stored data OR generates mock vitals
- Does NOT call IoT device

**Response:**
```json
{
  "success": true,
  "message": "Health check completed",
  "patientId": "patient_001",
  "vitals": {
    "heartRateAvg": 75.5,
    "spo2Avg": 98.2,
    "steps": 8500,
    "sleepHours": 7.5,
    "temperatureAvg": 36.8,
    "date": "2024-03-24",
    "timestamp": "2024-03-24T10:30:00"
  },
  "simulatedReading": true
}
```

---

### 5. Health Report
**GET** `/api/v1/health/report/{patientId}?days=7`

Generate comprehensive health analytics.

**Parameters:**
- `patientId` (path): Patient identifier
- `days` (query): Report period (1-90, default: 7)

**Response:**
```json
{
  "success": true,
  "report": {
    "patientId": "patient_001",
    "period": "Last 7 days",
    "dataPoints": 7,
    "avgHeartRate": 74.2,
    "avgSpo2": 97.8,
    "totalSteps": 52000,
    "avgStepsPerDay": 7428,
    "avgSleepHours": 7.3,
    "avgTemperature": 36.7,
    "vitalsData": [...]
  }
}
```

---

### 6. Emergency SOS Alert
**POST** `/api/v1/emergency/sos`

Create emergency alert with severity-based actions.

**Request Body:**
```json
{
  "patientId": "patient_001",
  "type": "HIGH_HEART_RATE",
  "severity": "HIGH",
  "location": {
    "lat": 28.6139,
    "lng": 77.2090
  }
}
```

**Alert Types:**
- `FALL`
- `LOW_SPO2`
- `HIGH_HEART_RATE`
- `MANUAL_SOS`

**Severity Levels & Actions:**
- `LOW`: SMS only
- `MEDIUM`: SMS + emergency call
- `HIGH`: SMS + emergency call

**Twilio Contact Fields (optional, but required for real delivery):**
- `doctorNumber`: single E.164 number (example `+919876543210`)
- `familyNumbers`: list of E.164 numbers
- `customMessage`: override auto-generated emergency message
- `soundUrl`, `voice`, `language`: call voice customization

**Response:**
```json
{
  "success": true,
  "message": "Emergency alert processed successfully",
  "alertId": "uuid-here",
  "actions_taken": [
    "SMS sent",
    "Emergency call initiated",
    "High priority alert"
  ]
}
```

---

### 7. Get Patient Alerts
**GET** `/api/v1/alerts/{patientId}`

Retrieve all alerts for a patient.

**Parameters:**
- `patientId` (path): Patient identifier

**Response:**
```json
{
  "success": true,
  "patientId": "patient_001",
  "count": 3,
  "alerts": [
    {
      "alertId": "uuid-here",
      "patientId": "patient_001",
      "type": "HIGH_HEART_RATE",
      "severity": "HIGH",
      "status": "active",
      "location": {
        "lat": 28.6139,
        "lng": 77.2090
      },
      "timestamp": "2024-03-24T10:30:00"
    }
  ]
}
```

---

### 8. Update Alert Status
**PATCH** `/api/v1/alerts/{alertId}?patient_id=patient_001`

Update alert status (typically to mark as resolved).

**Parameters:**
- `alertId` (path): Alert identifier
- `patient_id` (query): Patient identifier

**Request Body:**
```json
{
  "status": "resolved"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Alert uuid-here updated to resolved",
  "alertId": "uuid-here",
  "status": "resolved"
}
```

---

### 9. Send SMS (Twilio)
**POST** `/sms` or `/api/v1/communication/sms`

**Request Body:**
```json
{
  "phone_numbers": ["+919876543210"],
  "message": "Test SMS from VitalSync."
}
```

---

### 10. Make Call (Twilio)
**POST** `/call` or `/api/v1/communication/call`

**Request Body:**
```json
{
  "phone_numbers": ["+919876543210"],
  "message": "This is a test call from VitalSync."
}
```

---

### 11. SOS Notify (Priority-Based Twilio)
**POST** `/sos` or `/api/v1/communication/sos`

**Behavior:**
- `priority=LOW`: SMS only
- `priority=MEDIUM/HIGH`: SMS + call

**Request Body:**
```json
{
  "patient_name": "John Doe",
  "location": "28.6139, 77.2090",
  "emergency_type": "FALL",
  "priority": "MEDIUM",
  "doctor_number": "+919876543210",
  "family_numbers": ["+919812345678"]
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message here"
}
```

**Common Status Codes:**
- `200`: Success
- `400`: Bad Request (validation error)
- `404`: Not Found
- `500`: Internal Server Error

---

## Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI with interactive testing.
