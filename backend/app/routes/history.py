from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.models.db_models import User, ScanHistory
from app.models.auth_models import ScanHistoryResponse
from app.utils.auth_dependency import get_current_user

router = APIRouter(
    prefix="/history",
    tags=["Scan History"]
)


@router.get("", response_model=List[ScanHistoryResponse])
@router.get("/", response_model=List[ScanHistoryResponse])
def get_user_scan_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve scan history exclusively belonging to the currently authenticated user."""
    scans = (
        db.query(ScanHistory)
        .filter(ScanHistory.user_id == current_user.id)
        .order_by(ScanHistory.created_at.desc())
        .all()
    )
    return [ScanHistoryResponse.model_validate(s) for s in scans]


@router.get("/{scan_id}", response_model=ScanHistoryResponse)
def get_scan_by_id(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve an individual scan result with strict user ownership authorization."""
    scan = db.query(ScanHistory).filter(ScanHistory.id == scan_id).first()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan record not found."
        )

    # Strict IDOR / Authorization Check
    if scan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not have permission to view this scan."
        )

    return ScanHistoryResponse.model_validate(scan)


@router.delete("/{scan_id}")
def delete_scan_by_id(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a scan result with strict user ownership authorization."""
    scan = db.query(ScanHistory).filter(ScanHistory.id == scan_id).first()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan record not found."
        )

    # Strict IDOR / Authorization Check
    if scan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not have permission to delete this scan."
        )

    db.delete(scan)
    db.commit()

    return {"message": "Scan record deleted successfully", "id": scan_id}
