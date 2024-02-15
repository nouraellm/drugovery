from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    mlflow_run_id = Column(String, unique=True, nullable=True, index=True)
    model_type = Column(String, nullable=False)  # "qsar", "dti", etc.
    model_name = Column(String, nullable=True)
    parameters = Column(JSON, nullable=True)  # Model parameters
    metrics = Column(JSON, nullable=True)  # Model metrics
    status = Column(String, default="running")  # "running", "completed", "failed"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="experiments")
    predictions = relationship("Prediction", back_populates="experiment")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    compound_id = Column(Integer, ForeignKey("compounds.id"), nullable=False)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model_type = Column(String, nullable=False)  # "solubility", "toxicity", "dti"
    model_name = Column(String, nullable=True)
    prediction_value = Column(Float, nullable=True)
    prediction_confidence = Column(Float, nullable=True)
    prediction_details = Column(JSON, nullable=True)  # Additional prediction data
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    compound = relationship("Compound", back_populates="predictions")
    experiment = relationship("Experiment", back_populates="predictions")
    user = relationship("User", back_populates="predictions")
