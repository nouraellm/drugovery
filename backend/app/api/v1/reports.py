from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from io import BytesIO
import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.compound import Compound
from app.models.experiment import Prediction
from app.models.experiment import Experiment

router = APIRouter()


@router.get("/compounds/csv")
def export_compounds_csv(
    compound_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export compounds to CSV"""
    if compound_ids:
        compounds = db.query(Compound).filter(Compound.id.in_(compound_ids)).all()
    else:
        compounds = db.query(Compound).all()
    
    output = BytesIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "ID", "Name", "SMILES", "Molecular Formula", "Molecular Weight",
        "External ID", "External Source", "Created At"
    ])
    
    # Write data
    for compound in compounds:
        writer.writerow([
            compound.id,
            compound.name,
            compound.smiles,
            compound.molecular_formula or "",
            compound.molecular_weight or "",
            compound.external_id or "",
            compound.external_source or "",
            compound.created_at.isoformat() if compound.created_at else ""
        ])
    
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=compounds.csv"}
    )


@router.get("/predictions/csv")
def export_predictions_csv(
    experiment_id: Optional[int] = None,
    compound_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export predictions to CSV"""
    query = db.query(Prediction).filter(Prediction.user_id == current_user.id)
    
    if experiment_id:
        query = query.filter(Prediction.experiment_id == experiment_id)
    if compound_id:
        query = query.filter(Prediction.compound_id == compound_id)
    
    predictions = query.all()
    
    output = BytesIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "ID", "Compound ID", "Compound Name", "Model Type", "Model Name",
        "Prediction Value", "Confidence", "Created At"
    ])
    
    # Write data
    for pred in predictions:
        compound = db.query(Compound).filter(Compound.id == pred.compound_id).first()
        writer.writerow([
            pred.id,
            pred.compound_id,
            compound.name if compound else "",
            pred.model_type,
            pred.model_name or "",
            pred.prediction_value or "",
            pred.prediction_confidence or "",
            pred.created_at.isoformat() if pred.created_at else ""
        ])
    
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=predictions.csv"}
    )


@router.get("/experiment/{experiment_id}/pdf")
def generate_experiment_pdf(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate PDF report for an experiment"""
    experiment = db.query(Experiment).filter(
        Experiment.id == experiment_id,
        Experiment.user_id == current_user.id
    ).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    # Get predictions
    predictions = db.query(Prediction).filter(
        Prediction.experiment_id == experiment_id
    ).all()
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"Experiment Report: {experiment.name}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Experiment details
    story.append(Paragraph("Experiment Details", styles['Heading2']))
    details_data = [
        ["ID", str(experiment.id)],
        ["Name", experiment.name],
        ["Model Type", experiment.model_type],
        ["Model Name", experiment.model_name or "N/A"],
        ["Status", experiment.status],
        ["Created At", experiment.created_at.strftime("%Y-%m-%d %H:%M:%S") if experiment.created_at else "N/A"],
    ]
    if experiment.description:
        details_data.append(["Description", experiment.description])
    
    details_table = Table(details_data, colWidths=[150, 400])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(details_table)
    story.append(Spacer(1, 12))
    
    # Predictions
    story.append(Paragraph(f"Predictions ({len(predictions)})", styles['Heading2']))
    if predictions:
        pred_data = [["Compound ID", "Compound Name", "Value", "Confidence"]]
        for pred in predictions[:50]:  # Limit to 50 for PDF
            compound = db.query(Compound).filter(Compound.id == pred.compound_id).first()
            pred_data.append([
                str(pred.compound_id),
                compound.name if compound else "N/A",
                f"{pred.prediction_value:.4f}" if pred.prediction_value else "N/A",
                f"{pred.prediction_confidence:.2f}" if pred.prediction_confidence else "N/A"
            ])
        
        pred_table = Table(pred_data, colWidths=[100, 200, 100, 100])
        pred_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(pred_table)
    else:
        story.append(Paragraph("No predictions found.", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=experiment_{experiment_id}_report.pdf"}
    )
