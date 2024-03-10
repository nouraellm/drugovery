from sqlalchemy.orm import Session
from app.models.compound import Compound, CompoundVersion
from app.models.user import User


def create_compound_version(
    db: Session,
    compound: Compound,
    user_id: int,
    change_type: str = "update"
) -> CompoundVersion:
    """Create a version snapshot of a compound"""
    version = CompoundVersion(
        compound_id=compound.id,
        version=compound.version,
        name=compound.name,
        smiles=compound.smiles,
        properties=compound.properties,
        changed_by=user_id,
        change_type=change_type
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def get_compound_versions(
    db: Session,
    compound_id: int,
    skip: int = 0,
    limit: int = 100
):
    """Get version history for a compound"""
    return db.query(CompoundVersion).filter(
        CompoundVersion.compound_id == compound_id
    ).order_by(
        CompoundVersion.version.desc()
    ).offset(skip).limit(limit).all()


def rollback_compound(
    db: Session,
    compound_id: int,
    version: int,
    user_id: int
) -> Compound:
    """Rollback a compound to a previous version"""
    compound = db.query(Compound).filter(Compound.id == compound_id).first()
    if not compound:
        raise ValueError("Compound not found")
    
    version_data = db.query(CompoundVersion).filter(
        CompoundVersion.compound_id == compound_id,
        CompoundVersion.version == version
    ).first()
    
    if not version_data:
        raise ValueError("Version not found")
    
    # Create version of current state
    create_compound_version(db, compound, user_id, "rollback_from")
    
    # Restore from version
    compound.name = version_data.name
    compound.smiles = version_data.smiles
    compound.properties = version_data.properties
    compound.version += 1
    
    # Create version for rollback
    create_compound_version(db, compound, user_id, "rollback_to")
    
    db.commit()
    db.refresh(compound)
    return compound
