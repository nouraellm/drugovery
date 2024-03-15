from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.compound import Compound
from app.schemas.compound import (
    CompoundCreate,
    CompoundUpdate,
    CompoundResponse,
    CompoundSearch,
    CompoundVersionResponse,
)
from app.services.versioning_service import (
    create_compound_version,
    get_compound_versions,
    rollback_compound,
)
from app.services.chembl_service import search_chembl_compound, get_chembl_compound_by_id
from app.services.ml_service import validate_smiles, calculate_molecular_properties

router = APIRouter()


@router.post("/", response_model=CompoundResponse, status_code=status.HTTP_201_CREATED)
def create_compound(
    compound: CompoundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new compound"""
    # Validate SMILES
    if not validate_smiles(compound.smiles):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SMILES string"
        )
    
    # Calculate properties if not provided
    if not compound.properties:
        compound.properties = calculate_molecular_properties(compound.smiles)
        if compound.properties:
            compound.molecular_weight = compound.properties.get("molecular_weight")
    
    # Check for duplicates by SMILES
    existing = db.query(Compound).filter(Compound.smiles == compound.smiles).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Compound with this SMILES already exists"
        )
    
    db_compound = Compound(
        **compound.dict(),
        created_by=current_user.id
    )
    db.add(db_compound)
    db.commit()
    db.refresh(db_compound)
    
    # Create initial version
    create_compound_version(db, db_compound, current_user.id, "create")
    
    return db_compound


@router.get("/", response_model=List[CompoundResponse])
def list_compounds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    min_mw: Optional[float] = None,
    max_mw: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List compounds with optional filtering"""
    query = db.query(Compound)
    
    if search:
        query = query.filter(
            or_(
                Compound.name.ilike(f"%{search}%"),
                Compound.smiles.ilike(f"%{search}%"),
                Compound.molecular_formula.ilike(f"%{search}%")
            )
        )
    
    if min_mw is not None:
        query = query.filter(Compound.molecular_weight >= min_mw)
    
    if max_mw is not None:
        query = query.filter(Compound.molecular_weight <= max_mw)
    
    compounds = query.order_by(Compound.created_at.desc()).offset(skip).limit(limit).all()
    return compounds


@router.get("/{compound_id}", response_model=CompoundResponse)
def get_compound(
    compound_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a compound by ID"""
    compound = db.query(Compound).filter(Compound.id == compound_id).first()
    if not compound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compound not found"
        )
    return compound


@router.put("/{compound_id}", response_model=CompoundResponse)
def update_compound(
    compound_id: int,
    compound_update: CompoundUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a compound"""
    compound = db.query(Compound).filter(Compound.id == compound_id).first()
    if not compound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compound not found"
        )
    
    # Create version before update
    create_compound_version(db, compound, current_user.id, "update")
    
    # Update fields
    update_data = compound_update.dict(exclude_unset=True)
    if "smiles" in update_data:
        if not validate_smiles(update_data["smiles"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid SMILES string"
            )
        # Recalculate properties if SMILES changed
        new_properties = calculate_molecular_properties(update_data["smiles"])
        if new_properties:
            update_data["properties"] = new_properties
            update_data["molecular_weight"] = new_properties.get("molecular_weight")
    
    for field, value in update_data.items():
        setattr(compound, field, value)
    
    compound.version += 1
    db.commit()
    db.refresh(compound)
    
    return compound


@router.delete("/{compound_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_compound(
    compound_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a compound"""
    compound = db.query(Compound).filter(Compound.id == compound_id).first()
    if not compound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compound not found"
        )
    
    # Create version for deletion
    create_compound_version(db, compound, current_user.id, "delete")
    
    db.delete(compound)
    db.commit()
    return None


@router.get("/{compound_id}/versions", response_model=List[CompoundVersionResponse])
def get_compound_version_history(
    compound_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get version history for a compound"""
    compound = db.query(Compound).filter(Compound.id == compound_id).first()
    if not compound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compound not found"
        )
    
    versions = get_compound_versions(db, compound_id, skip, limit)
    return versions


@router.post("/{compound_id}/rollback/{version}", response_model=CompoundResponse)
def rollback_compound_version(
    compound_id: int,
    version: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Rollback a compound to a previous version"""
    try:
        compound = rollback_compound(db, compound_id, version, current_user.id)
        return compound
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/import/chembl/{chembl_id}", response_model=CompoundResponse)
async def import_chembl_compound(
    chembl_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Import a compound from ChEMBL"""
    chembl_data = await get_chembl_compound_by_id(chembl_id)
    if not chembl_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compound not found in ChEMBL"
        )
    
    # Check if already exists
    existing = db.query(Compound).filter(
        Compound.external_id == chembl_id,
        Compound.external_source == "chembl"
    ).first()
    if existing:
        return existing
    
    # Create compound
    compound = Compound(
        name=chembl_data["name"],
        smiles=chembl_data.get("smiles", ""),
        external_id=chembl_data["external_id"],
        external_source=chembl_data["external_source"],
        properties=chembl_data.get("properties", {}),
        created_by=current_user.id
    )
    
    if compound.smiles:
        props = calculate_molecular_properties(compound.smiles)
        if props:
            compound.properties = {**(compound.properties or {}), **props}
            compound.molecular_weight = props.get("molecular_weight")
    
    db.add(compound)
    db.commit()
    db.refresh(compound)
    
    create_compound_version(db, compound, current_user.id, "create")
    
    return compound
