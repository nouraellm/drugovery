from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.experiment import Experiment
from app.schemas.experiment import (
    ExperimentCreate,
    ExperimentUpdate,
    ExperimentResponse,
)
from app.services.ml_service import log_prediction_to_mlflow

router = APIRouter()


@router.post("/", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
def create_experiment(
    experiment: ExperimentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new experiment"""
    db_experiment = Experiment(
        **experiment.dict(),
        user_id=current_user.id,
        status="running"
    )
    db.add(db_experiment)
    db.commit()
    db.refresh(db_experiment)
    
    return db_experiment


@router.get("/", response_model=List[ExperimentResponse])
def list_experiments(
    skip: int = 0,
    limit: int = 100,
    model_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List experiments"""
    query = db.query(Experiment).filter(Experiment.user_id == current_user.id)
    
    if model_type:
        query = query.filter(Experiment.model_type == model_type)
    
    experiments = query.order_by(Experiment.created_at.desc()).offset(skip).limit(limit).all()
    return experiments


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get an experiment by ID"""
    experiment = db.query(Experiment).filter(
        Experiment.id == experiment_id,
        Experiment.user_id == current_user.id
    ).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    return experiment


@router.put("/{experiment_id}", response_model=ExperimentResponse)
def update_experiment(
    experiment_id: int,
    experiment_update: ExperimentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an experiment"""
    experiment = db.query(Experiment).filter(
        Experiment.id == experiment_id,
        Experiment.user_id == current_user.id
    ).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    update_data = experiment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(experiment, field, value)
    
    if experiment_update.status == "completed":
        experiment.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(experiment)
    return experiment


@router.post("/{experiment_id}/log-to-mlflow", response_model=ExperimentResponse)
def log_experiment_to_mlflow(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Log experiment to MLflow"""
    experiment = db.query(Experiment).filter(
        Experiment.id == experiment_id,
        Experiment.user_id == current_user.id
    ).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    if experiment.mlflow_run_id:
        return experiment  # Already logged
    
    # Get predictions for this experiment
    from app.models.experiment import Prediction
    predictions = db.query(Prediction).filter(
        Prediction.experiment_id == experiment_id
    ).all()
    
    # Prepare data for MLflow
    predictions_data = [{
        "compound_id": p.compound_id,
        "prediction_value": p.prediction_value,
        "prediction_confidence": p.prediction_confidence,
    } for p in predictions]
    
    # Log to MLflow
    run_id = log_prediction_to_mlflow(
        run_name=experiment.name,
        model_type=experiment.model_type,
        parameters=experiment.parameters or {},
        metrics=experiment.metrics or {},
        predictions=predictions_data
    )
    
    experiment.mlflow_run_id = run_id
    db.commit()
    db.refresh(experiment)
    
    return experiment
