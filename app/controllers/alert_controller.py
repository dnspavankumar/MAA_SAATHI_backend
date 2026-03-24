from fastapi import HTTPException
from app.schemas.alert_schema import SOSRequest, SOSResponse, AlertUpdateRequest
from app.services.firestore_service import firestore_service
from app.services.alert_service import alert_service
from app.utils.logger import logger

class AlertController:
    """Handle emergency alerts and SOS requests"""
    
    async def create_sos_alert(self, sos_request: SOSRequest) -> SOSResponse:
        """Process emergency SOS alert"""
        try:
            alert_data = {
                "patientId": sos_request.patientId,
                "type": sos_request.type,
                "severity": sos_request.severity,
                "location": sos_request.location.model_dump(),
                "doctorNumber": sos_request.doctorNumber,
                "familyNumbers": sos_request.familyNumbers,
            }
            if sos_request.customMessage:
                alert_data["customMessage"] = sos_request.customMessage
            
            # Store alert in Firestore
            alert_id = await firestore_service.store_alert(
                patient_id=sos_request.patientId,
                alert_data=alert_data
            )
            
            # Process alert based on severity
            actions = alert_service.process_alert(
                severity=sos_request.severity,
                patient_id=sos_request.patientId,
                alert_type=sos_request.type,
                location=alert_data["location"],
                doctor_number=sos_request.doctorNumber,
                family_numbers=sos_request.familyNumbers,
                custom_message=sos_request.customMessage,
                sound_url=str(sos_request.soundUrl) if sos_request.soundUrl else None,
                voice=sos_request.voice,
                language=sos_request.language,
            )
            
            logger.info(f"SOS alert {alert_id} created for patient {sos_request.patientId}")
            
            return SOSResponse(
                success=True,
                message="Emergency alert processed successfully",
                alertId=alert_id,
                actions_taken=actions
            )
            
        except Exception as e:
            logger.error(f"Error processing SOS alert: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_patient_alerts(self, patient_id: str):
        """Retrieve all alerts for a patient"""
        try:
            alerts = await firestore_service.get_alerts(patient_id)
            
            return {
                "success": True,
                "patientId": patient_id,
                "count": len(alerts),
                "alerts": alerts
            }
            
        except Exception as e:
            logger.error(f"Error fetching alerts: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_alert(self, patient_id: str, alert_id: str, update_data: AlertUpdateRequest):
        """Update alert status"""
        try:
            success = await firestore_service.update_alert_status(
                patient_id=patient_id,
                alert_id=alert_id,
                status=update_data.status
            )
            
            if not success:
                raise HTTPException(status_code=404, detail="Alert not found")
            
            return {
                "success": True,
                "message": f"Alert {alert_id} updated to {update_data.status}",
                "alertId": alert_id,
                "status": update_data.status
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating alert: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

alert_controller = AlertController()
