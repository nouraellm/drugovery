from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class CompoundBase(BaseModel):
    name: str
    smiles: str
    inchi: Optional[str] = None
    inchi_key: Optional[str] = None
    molecular_formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    properties: Optional[Dict[str, Any]] = None
    external_id: Optional[str] = None
    external_source: Optional[str] = None


class CompoundCreate(CompoundBase):
    pass


class CompoundUpdate(BaseModel):
    name: Optional[str] = None
    smiles: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class CompoundResponse(CompoundBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    version: int

    class Config:
        from_attributes = True


class CompoundVersionResponse(BaseModel):
    id: int
    compound_id: int
    version: int
    name: str
    smiles: str
    properties: Optional[Dict[str, Any]]
    change_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class CompoundSearch(BaseModel):
    query: Optional[str] = None
    min_molecular_weight: Optional[float] = None
    max_molecular_weight: Optional[float] = None
    external_source: Optional[str] = None
    skip: int = 0
    limit: int = 100
