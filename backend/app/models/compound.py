from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Compound(Base):
    __tablename__ = "compounds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    smiles = Column(String, nullable=False, index=True)
    inchi = Column(String, nullable=True)
    inchi_key = Column(String, nullable=True, index=True)
    molecular_formula = Column(String, nullable=True)
    molecular_weight = Column(Float, nullable=True)
    properties = Column(JSON, nullable=True)  # Store additional properties as JSON
    external_id = Column(String, nullable=True)  # ChEMBL/PubChem ID
    external_source = Column(String, nullable=True)  # "chembl" or "pubchem"
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    version = Column(Integer, default=1)

    # Relationships
    created_by_user = relationship("User", back_populates="compounds")
    versions = relationship("CompoundVersion", back_populates="compound")
    predictions = relationship("Prediction", back_populates="compound")


class CompoundVersion(Base):
    __tablename__ = "compound_versions"

    id = Column(Integer, primary_key=True, index=True)
    compound_id = Column(Integer, ForeignKey("compounds.id"), nullable=False)
    version = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    smiles = Column(String, nullable=False)
    properties = Column(JSON, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_type = Column(String, nullable=False)  # "create", "update", "delete"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    compound = relationship("Compound", back_populates="versions")
    changed_by_user = relationship("User")
