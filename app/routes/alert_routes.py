from fastapi import APIRouter
from app.schemas.alert_schema import SOSRequest, SOSResponse, AlertUpdateRequest
from app.controllers.alert_controller import alert_controller

router = APIRouter(prefix="/api/v1", tags=["Alerts"])

@router.post("/emergency/sos", response_model=SOSResponse)
async def create_sos_alert(sos_request: SOSRequest):
    """
    Create emergency SOS alert
    
    - Accepts alert with type, severity, and location
    - Stores in Firestore
    - Triggers severity-based actions:
      - LOW: SMS only
      - MEDIUM/HIGH: SMS + emergency call
    - Include doctorNumber/familyNumbers for real Twilio delivery
    """
    return await alert_controller.create_sos_alert(sos_request)

@router.get("/alerts/{patient_id}")
async def get_patient_alerts(patient_id: str):
    """
    Retrieve all alerts for a patient
    
    - Returns alerts sorted by timestamp (latest first)
    - Includes alert status and details
    """
    return await alert_controller.get_patient_alerts(patient_id)

@router.patch("/alerts/{alert_id}")
async def update_alert(alert_id: str, patient_id: str, update_data: AlertUpdateRequest):
    """
    Update alert status
    
    - Typically used to mark alerts as resolved
    - Requires patient_id as query parameter for security
    """
    return await alert_controller.update_alert(patient_id, alert_id, update_data)
