from fastapi import APIRouter
from app.api.v1 import auth, compounds, predictions, experiments, reports

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(compounds.router, prefix="/compounds", tags=["compounds"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
