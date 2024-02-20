from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class PredictionBase(BaseModel):
    model_type: str  # "solubility", "toxicity", "dti"
    model_name: Optional[str] = None
    prediction_value: Optional[float] = None
    prediction_confidence: Optional[float] = None
    prediction_details: Optional[Dict[str, Any]] = None


class PredictionCreate(PredictionBase):
    compound_id: int
    experiment_id: Optional[int] = None


class PredictionResponse(PredictionBase):
    id: int
    compound_id: int
    experiment_id: Optional[int]
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BatchPredictionRequest(BaseModel):
    compound_ids: List[int]
    model_type: str
    model_name: Optional[str] = None


class PredictionResult(BaseModel):
    compound_id: int
    compound_name: str
    smiles: str
    prediction: PredictionResponse
