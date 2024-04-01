import mlflow
import numpy as np
from typing import Dict, Any, List, Optional
from rdkit import Chem
from rdkit.Chem import Descriptors
from app.core.config import settings

# MLflow will be initialized lazily when needed
_mlflow_initialized = False

def _ensure_mlflow_initialized():
    """Lazily initialize MLflow connection"""
    global _mlflow_initialized
    if not _mlflow_initialized:
        try:
            mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
            mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)
            _mlflow_initialized = True
        except Exception:
            # MLflow not available, continue without it
            pass


def validate_smiles(smiles: str) -> bool:
    """Validate SMILES string"""
    try:
        mol = Chem.MolFromSmiles(smiles)
        return mol is not None
    except:
        return False


def calculate_molecular_properties(smiles: str) -> Dict[str, Any]:
    """Calculate basic molecular properties from SMILES"""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {}
        
        return {
            "molecular_weight": Descriptors.MolWt(mol),
            "logp": Descriptors.MolLogP(mol),
            "num_atoms": mol.GetNumAtoms(),
            "num_bonds": mol.GetNumBonds(),
            "num_rings": Descriptors.RingCount(mol),
            "num_aromatic_rings": Descriptors.NumAromaticRings(mol),
            "num_rotatable_bonds": Descriptors.NumRotatableBonds(mol),
            "tpsa": Descriptors.TPSA(mol),  # Topological Polar Surface Area
            "hbd": Descriptors.NumHDonors(mol),  # Hydrogen Bond Donors
            "hba": Descriptors.NumHAcceptors(mol),  # Hydrogen Bond Acceptors
        }
    except Exception as e:
        print(f"Error calculating properties: {e}")
        return {}


def predict_solubility(smiles: str, model_name: str = "solubility_model") -> Dict[str, Any]:
    """
    Predict solubility using a simple QSAR model
    In production, this would load a trained model from MLflow
    """
    try:
        properties = calculate_molecular_properties(smiles)
        if not properties:
            return {"error": "Invalid SMILES"}
        
        # Simple rule-based prediction (replace with actual ML model)
        # Higher logP and molecular weight typically reduce solubility
        logp = properties.get("logp", 0)
        mw = properties.get("molecular_weight", 0)
        
        # Simple heuristic (not a real model, just for demonstration)
        solubility_score = 1.0 / (1.0 + np.exp((logp - 2.0) / 2.0)) * (1.0 / (1.0 + mw / 500.0))
        solubility_mg_ml = solubility_score * 100  # Convert to mg/mL
        
        return {
            "prediction_value": float(solubility_mg_ml),
            "prediction_confidence": 0.75,  # Placeholder
            "prediction_details": {
                "model_type": "qsar",
                "model_name": model_name,
                "properties_used": properties,
                "units": "mg/mL"
            }
        }
    except Exception as e:
        return {"error": str(e)}


def predict_toxicity(smiles: str, model_name: str = "toxicity_model") -> Dict[str, Any]:
    """
    Predict toxicity using a simple QSAR model
    In production, this would load a trained model from MLflow
    """
    try:
        properties = calculate_molecular_properties(smiles)
        if not properties:
            return {"error": "Invalid SMILES"}
        
        # Simple rule-based prediction (replace with actual ML model)
        # Higher molecular weight and certain structural features increase toxicity risk
        mw = properties.get("molecular_weight", 0)
        num_rings = properties.get("num_rings", 0)
        
        # Simple heuristic (not a real model, just for demonstration)
        toxicity_score = min(1.0, (mw / 1000.0) * 0.3 + (num_rings / 10.0) * 0.2)
        is_toxic = toxicity_score > 0.5
        
        return {
            "prediction_value": float(toxicity_score),
            "prediction_confidence": 0.70,  # Placeholder
            "prediction_details": {
                "model_type": "toxicity",
                "model_name": model_name,
                "is_toxic": is_toxic,
                "properties_used": properties,
                "risk_level": "high" if is_toxic else "low"
            }
        }
    except Exception as e:
        return {"error": str(e)}


def predict_drug_target_interaction(
    smiles: str,
    target_id: Optional[str] = None,
    model_name: str = "dti_model"
) -> Dict[str, Any]:
    """
    Predict drug-target interaction
    In production, this would use a GNN or other advanced model
    """
    try:
        properties = calculate_molecular_properties(smiles)
        if not properties:
            return {"error": "Invalid SMILES"}
        
        # Simple rule-based prediction (replace with actual GNN model)
        # This is a placeholder - real DTI models are much more complex
        mw = properties.get("molecular_weight", 0)
        logp = properties.get("logp", 0)
        
        # Simple heuristic (not a real model)
        interaction_score = 1.0 / (1.0 + np.exp(-(logp - 1.0))) * (1.0 / (1.0 + abs(mw - 300) / 100))
        
        return {
            "prediction_value": float(interaction_score),
            "prediction_confidence": 0.65,  # Placeholder
            "prediction_details": {
                "model_type": "dti",
                "model_name": model_name,
                "target_id": target_id or "unknown",
                "properties_used": properties,
                "interaction_probability": float(interaction_score)
            }
        }
    except Exception as e:
        return {"error": str(e)}


def log_prediction_to_mlflow(
    run_name: str,
    model_type: str,
    parameters: Dict[str, Any],
    metrics: Dict[str, Any],
    predictions: List[Dict[str, Any]]
) -> str:
    """Log prediction run to MLflow"""
    _ensure_mlflow_initialized()
    try:
        with mlflow.start_run(run_name=run_name):
            mlflow.log_params(parameters)
            mlflow.log_metrics(metrics)
            mlflow.log_dict(predictions, "predictions.json")
            return mlflow.active_run().info.run_id
    except Exception as e:
        # If MLflow is not available, return a placeholder
        print(f"Warning: Could not log to MLflow: {e}")
        return f"local-{run_name}"
