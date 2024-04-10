from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.compound import Compound
from app.models.experiment import Prediction
from app.schemas.prediction import (
    PredictionCreate,
    PredictionResponse,
    BatchPredictionRequest,
    PredictionResult,
)
from app.services.ml_service import (
    predict_solubility,
    predict_toxicity,
    predict_drug_target_interaction,
    validate_smiles,
)
from app.tasks.prediction_tasks import run_batch_prediction_task

router = APIRouter()


@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def create_prediction(
    prediction: PredictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a single prediction"""
    # Verify compound exists
    compound = db.query(Compound).filter(Compound.id == prediction.compound_id).first()
    if not compound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compound not found"
        )
    
    # Run prediction based on model type
    if prediction.model_type == "solubility":
        result = predict_solubility(compound.smiles, prediction.model_name)
    elif prediction.model_type == "toxicity":
        result = predict_toxicity(compound.smiles, prediction.model_name)
    elif prediction.model_type == "dti":
        result = predict_drug_target_interaction(compound.smiles, model_name=prediction.model_name)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown model type: {prediction.model_type}"
        )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    # Create prediction record
    db_prediction = Prediction(
        compound_id=prediction.compound_id,
        experiment_id=prediction.experiment_id,
        user_id=current_user.id,
        model_type=prediction.model_type,
        model_name=prediction.model_name or result.get("prediction_details", {}).get("model_name"),
        prediction_value=result.get("prediction_value"),
        prediction_confidence=result.get("prediction_confidence"),
        prediction_details=result.get("prediction_details", {})
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction


@router.post("/batch", status_code=status.HTTP_202_ACCEPTED)
def create_batch_prediction(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create batch predictions (async)"""
    # Verify all compounds exist
    compounds = db.query(Compound).filter(Compound.id.in_(request.compound_ids)).all()
    if len(compounds) != len(request.compound_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some compounds not found"
        )
    
    # Queue background task
    task_id = f"batch_pred_{current_user.id}_{len(request.compound_ids)}"
    background_tasks.add_task(
        run_batch_prediction_task,
        compound_ids=request.compound_ids,
        model_type=request.model_type,
        model_name=request.model_name,
        user_id=current_user.id
    )
    
    return {
        "message": "Batch prediction task queued",
        "task_id": task_id,
        "compound_count": len(request.compound_ids)
    }


@router.get("/", response_model=List[PredictionResponse])
def list_predictions(
    skip: int = 0,
    limit: int = 100,
    model_type: str = None,
    compound_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List predictions"""
    query = db.query(Prediction).filter(Prediction.user_id == current_user.id)
    
    if model_type:
        query = query.filter(Prediction.model_type == model_type)
    
    if compound_id:
        query = query.filter(Prediction.compound_id == compound_id)
    
    predictions = query.order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()
    return predictions


@router.get("/{prediction_id}", response_model=PredictionResponse)
def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a prediction by ID"""
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id
    ).first()
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    return prediction


@router.get("/compound/{compound_id}", response_model=List[PredictionResponse])
def get_compound_predictions(
    compound_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all predictions for a compound"""
    compound = db.query(Compound).filter(Compound.id == compound_id).first()
    if not compound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compound not found"
        )
    
    predictions = db.query(Prediction).filter(
        Prediction.compound_id == compound_id,
        Prediction.user_id == current_user.id
    ).order_by(Prediction.created_at.desc()).all()
    
    return predictions
