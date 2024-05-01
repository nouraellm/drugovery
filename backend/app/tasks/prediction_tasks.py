from celery import Celery
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.compound import Compound
from app.models.experiment import Prediction
from app.services.ml_service import (
    predict_solubility,
    predict_toxicity,
    predict_drug_target_interaction,
)

# Initialize Celery
celery_app = Celery(
    "drug_discovery",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery_app.task(name="run_batch_prediction")
def run_batch_prediction_task(
    compound_ids: list,
    model_type: str,
    model_name: str = None,
    user_id: int = None
):
    """Background task for batch predictions"""
    db: Session = SessionLocal()
    try:
        predictions_created = []
        
        for compound_id in compound_ids:
            compound = db.query(Compound).filter(Compound.id == compound_id).first()
            if not compound:
                continue
            
            # Run prediction
            if model_type == "solubility":
                result = predict_solubility(compound.smiles, model_name)
            elif model_type == "toxicity":
                result = predict_toxicity(compound.smiles, model_name)
            elif model_type == "dti":
                result = predict_drug_target_interaction(compound.smiles, model_name=model_name)
            else:
                continue
            
            if "error" in result:
                continue
            
            # Create prediction record
            prediction = Prediction(
                compound_id=compound_id,
                user_id=user_id,
                model_type=model_type,
                model_name=model_name or result.get("prediction_details", {}).get("model_name"),
                prediction_value=result.get("prediction_value"),
                prediction_confidence=result.get("prediction_confidence"),
                prediction_details=result.get("prediction_details", {})
            )
            db.add(prediction)
            predictions_created.append(compound_id)
        
        db.commit()
        return {
            "status": "completed",
            "predictions_created": len(predictions_created),
            "compound_ids": predictions_created
        }
    except Exception as e:
        db.rollback()
        return {
            "status": "failed",
            "error": str(e)
        }
    finally:
        db.close()
