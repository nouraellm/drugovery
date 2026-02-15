from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
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


@router.post("/import/file", status_code=status.HTTP_200_OK)
async def import_compounds_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Import compounds from CSV or Excel file"""
    import pandas as pd
    from io import BytesIO

    if not file.filename.endswith(('.csv', '.xls', '.xlsx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be CSV or Excel"
        )

    contents = await file.read()
    buffer = BytesIO(contents)

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(buffer)
        else:
            df = pd.read_excel(buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    # 1. Identify Model Fields
    model_columns = {c.name.lower(): c.name for c in Compound.__table__.columns}
    # Add common aliases for core fields
    field_aliases = {
        'name': ['name', 'compound name', 'compound', 'label', 'title', 'compound_name', 'id', 'id_compound'],
        'smiles': ['smiles', 'smile', 'structure', 'canonical smiles', 'isomeric smiles', 'canonical_smiles', 'mol'],
        'molecular_formula': ['molecular_formula', 'formula', 'mol_formula', 'm_formula', 'mf'],
        'molecular_weight': ['molecular_weight', 'molecular weight', 'mw', 'mol weight', 'molweight'],
        'inchi': ['inchi'],
        'inchi_key': ['inchi_key', 'inchi key'],
        'external_id': ['external_id', 'external id', 'source id', 'source_id'],
        'external_source': ['external_source', 'external source', 'source']
    }

    # 2. Intelligent Column Mapping
    col_map = {c.lower().replace('_', ' ').strip(): c for c in df.columns}
    field_to_col = {}
    
    # Try mapping by header
    for field, aliases in field_aliases.items():
        for alias in aliases:
            if alias.replace('_', ' ') in col_map:
                field_to_col[field] = col_map[alias.replace('_', ' ')]
                break

    # 3. Content-based detection for SMILES (if not found by header)
    if 'smiles' not in field_to_col:
        for col in df.columns:
            # Check first 5 non-null rows
            sample = df[col].dropna().head(5)
            if not sample.empty:
                valid_count = sum(1 for s in sample if validate_smiles(str(s).strip()))
                if valid_count >= len(sample) * 0.8: # 80% of sample are valid SMILES
                    field_to_col['smiles'] = col
                    break

    if 'smiles' not in field_to_col:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not detect a SMILES column. Please ensure your file has a column with SMILES structures."
        )

    # 4. Fallback for Name
    if 'name' not in field_to_col:
        # Pick first column that is not the SMILES column and has type object/string
        for col in df.columns:
            if col != field_to_col['smiles'] and df[col].dtype == 'object':
                field_to_col['name'] = col
                break
    
    # Final fallback for name: use SMILES column itself
    if 'name' not in field_to_col:
        field_to_col['name'] = field_to_col['smiles']

    results: dict = {
        "total": len(df),
        "imported": 0,
        "updated": 0,
        "skipped": 0,
        "errors": []
    }
    
    for idx, row in df.iterrows():
        try:
            # Extract data using the mapping
            smiles = str(row[field_to_col['smiles']]).strip()
            if not smiles or pd.isna(row[field_to_col['smiles']]):
                continue

            if not validate_smiles(smiles):
                results["errors"].append(f"Row {idx}: Invalid SMILES string.")
                continue

            name = str(row[field_to_col['name']]).strip() if not pd.isna(row[field_to_col['name']]) else smiles
            
            # Check if compound exists
            existing = db.query(Compound).filter(Compound.smiles == smiles).first()
            
            # Prepare properties
            extra_props = {}
            mapped_cols = set(field_to_col.values())
            for col in df.columns:
                if col not in mapped_cols:
                    val = row[col]
                    if not pd.isna(val):
                        extra_props[col] = val

            # Calculate theoretical properties
            calculated_props = calculate_molecular_properties(smiles) or {}
            
            # Decide if we update or create
            db_compound = existing
            is_new = False
            if not db_compound:
                db_compound = Compound(smiles=smiles, created_by=current_user.id)
                is_new = True
            else:
                # Create a version before update
                create_compound_version(db, db_compound, current_user.id, "update")
                db_compound.version += 1
            
            # Update fields from CSV
            db_compound.name = name
            
            # Map other fields if present in CSV
            for field in ['molecular_formula', 'molecular_weight', 'inchi', 'inchi_key', 'external_id', 'external_source']:
                if field in field_to_col:
                    val = row[field_to_col[field]]
                    if not pd.isna(val):
                        if field == 'molecular_weight':
                            try:
                                db_compound.molecular_weight = float(val)
                            except: pass
                        else:
                            setattr(db_compound, field, str(val).strip())
            
            # Auto-fill missing fields from calculated props
            if not db_compound.molecular_formula:
                db_compound.molecular_formula = calculated_props.get('molecular_formula')
            if not db_compound.molecular_weight:
                db_compound.molecular_weight = calculated_props.get('molecular_weight')
            
            # Merge properties
            # We preserve existing extra props if updating? 
            # "Take from CSV correct values" -> overwrite properties with new CSV data + calculated props
            db_compound.properties = {**calculated_props, **extra_props}
            
            if is_new:
                db.add(db_compound)
                db.commit()
                db.refresh(db_compound)
                create_compound_version(db, db_compound, current_user.id, "create")
                results["imported"] += 1
            else:
                db.commit()
                db.refresh(db_compound)
                results["updated"] += 1
            
        except Exception as e:
            db.rollback()
            results["errors"].append(f"Row {idx}: {str(e)}")
            
    return results
