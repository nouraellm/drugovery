from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ExperimentBase(BaseModel):
    name: str
    description: Optional[str] = None
    model_type: str
    model_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ExperimentCreate(ExperimentBase):
    pass


class ExperimentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class ExperimentResponse(ExperimentBase):
    id: int
    mlflow_run_id: Optional[str]
    metrics: Optional[Dict[str, Any]]
    status: str
    user_id: int
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
