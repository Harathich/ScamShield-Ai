from typing import Optional, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
import filetype
import io
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.models.orchestrator_models import FullAnalysisRequest, FullAnalysisResponse, NormalizedMetadata
from app.graph.workflow import scamshield_workflow
from app.services.ocr.ocr_service import OCRService
from app.database.connection import get_db
from app.models.db_models import User, ScanHistory
from app.utils.auth_dependency import get_optional_current_user

router = APIRouter(
    prefix="/analyze-all",
    tags=["Full Analysis Pipeline"]
)

ocr_service = OCRService()

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]
ALLOWED_PDF_MIME_TYPES = ["application/pdf"]


def to_dict(obj: Any) -> Any:
    """Helper to convert Pydantic objects, dicts, or lists to JSON serializable dicts."""
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(x) for x in obj]
    return obj


def _save_scan_to_history(
    current_user: Optional[User],
    db: Session,
    input_type: str,
    input_content: str,
    response: FullAnalysisResponse
):
    """Outer-layer helper to persist scan history for authenticated users."""
    if not current_user or not db:
        return
    try:
        agent_results = {
            "contributing_factors": response.contributing_factors,
            "confidence": response.confidence,
            "normalized_metadata": to_dict(response.normalized_metadata),
            "agent_summary": to_dict(response.agent_summary),
            "report": to_dict(response.report),
            "threat_result": to_dict(response.threat_result),
            "language_result": to_dict(response.language_result),
            "identity_result": to_dict(response.identity_result),
            "domain_result": to_dict(response.domain_result),
            "recruitment_result": to_dict(response.recruitment_result)
        }
        scan_record = ScanHistory(
            user_id=current_user.id,
            input_type=input_type,
            input_content=input_content[:5000] if input_content else "Scanned Content",
            overall_risk_score=response.overall_risk_score,
            overall_threat_level=response.overall_threat_level,
            agent_results=agent_results
        )
        db.add(scan_record)
        db.commit()
    except Exception as err:
        print(f"[Warning] Failed to persist scan history: {err}")
        db.rollback()


@router.post("/", response_model=FullAnalysisResponse)
@router.post("/analyze", response_model=FullAnalysisResponse)
def full_analysis(
    request: FullAnalysisRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Run the full ScamShield multi-agent analysis pipeline with input preprocessing.
    """
    if not (request.text or "").strip() and not (request.url or "").strip():
        raise HTTPException(
            status_code=422,
            detail="Provide non-empty text or a URL to analyze.",
        )

    try:
        initial_state = {
            "input_text": request.text or "",
            "input_url": request.url,
            "normalized_content": None,
            "threat_result": None,
            "language_result": None,
            "identity_result": None,
            "domain_result": None,
            "recruitment_result": None,
            "risk_manager_result": None,
            "report": None,
            "overall_risk_score": None,
            "overall_threat_level": None,
            "agent_summary": None,
        }

        result = scamshield_workflow.invoke(initial_state)

        risk_manager_result = result.get("risk_manager_result", {})
        norm = result.get("normalized_content", {})

        normalized_metadata = NormalizedMetadata(
            detected_format=norm.get("detected_format", "plain_text"),
            extracted_urls=norm.get("extracted_urls", []),
            extracted_emails=norm.get("extracted_emails", []),
            extracted_phones=norm.get("extracted_phones", [])
        ) if norm else None

        response = FullAnalysisResponse(
            overall_risk_score=result.get("overall_risk_score", 0),
            overall_threat_level=result.get("overall_threat_level", "LOW"),
            contributing_factors=risk_manager_result.get("contributing_factors", []),
            confidence=risk_manager_result.get("confidence", 0),
            normalized_metadata=normalized_metadata,
            agent_summary=result.get("agent_summary", {}),
            report=result.get("report"),
            threat_result=result.get("threat_result"),
            language_result=result.get("language_result"),
            identity_result=result.get("identity_result"),
            domain_result=result.get("domain_result"),
            recruitment_result=result.get("recruitment_result"),
        )

        # Non-intrusive outer layer scan persistence
        input_type = "url" if request.url else "text"
        input_content = request.url if request.url else request.text
        _save_scan_to_history(current_user, db, input_type, input_content, response)

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis pipeline error: {str(e)}"
        )


@router.post("/image", response_model=FullAnalysisResponse)
async def analyze_image_upload(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Run the full ScamShield multi-agent analysis pipeline on an uploaded screenshot or image.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Supported types are JPEG, PNG, and WEBP."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size of {MAX_FILE_SIZE_MB}MB.")

    kind = filetype.guess(file_bytes)
    if kind is None or kind.mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File content does not match a supported image format.")

    # Run OCR extraction
    ocr_result = ocr_service.extract_text(file_bytes)
    if not ocr_result.get("success"):
        raise HTTPException(status_code=400, detail=ocr_result.get("error", "OCR extraction failed."))

    extracted_text = ocr_result.get("extracted_text", "")
    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="No readable text could be extracted from the uploaded image.")

    # Feed extracted OCR text through the full multi-agent pipeline
    initial_state = {
        "input_text": extracted_text,
        "input_url": None,
        "normalized_content": None,
        "threat_result": None,
        "language_result": None,
        "identity_result": None,
        "domain_result": None,
        "recruitment_result": None,
        "risk_manager_result": None,
        "report": None,
        "overall_risk_score": None,
        "overall_threat_level": None,
        "agent_summary": None,
    }

    result = scamshield_workflow.invoke(initial_state)

    risk_manager_result = result.get("risk_manager_result", {})
    norm = result.get("normalized_content", {})

    normalized_metadata = NormalizedMetadata(
        detected_format=norm.get("detected_format", "image_ocr_text"),
        extracted_urls=norm.get("extracted_urls", []),
        extracted_emails=norm.get("extracted_emails", []),
        extracted_phones=norm.get("extracted_phones", [])
    ) if norm else None

    response = FullAnalysisResponse(
        overall_risk_score=result.get("overall_risk_score", 0),
        overall_threat_level=result.get("overall_threat_level", "LOW"),
        contributing_factors=risk_manager_result.get("contributing_factors", []),
        confidence=risk_manager_result.get("confidence", 0),
        normalized_metadata=normalized_metadata,
        agent_summary=result.get("agent_summary", {}),
        report=result.get("report"),
        threat_result=result.get("threat_result"),
        language_result=result.get("language_result"),
        identity_result=result.get("identity_result"),
        domain_result=result.get("domain_result"),
        recruitment_result=result.get("recruitment_result"),
    )

    # Save to scan history with OCR context
    input_content = f"[Image OCR ({file.filename})]: {extracted_text}"
    _save_scan_to_history(current_user, db, "image", input_content, response)

    return response


@router.post("/pdf", response_model=FullAnalysisResponse)
async def analyze_pdf_upload(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Run the full ScamShield multi-agent analysis pipeline on an uploaded PDF document.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    if file.content_type not in ALLOWED_PDF_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Only PDF is supported."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty PDF file uploaded.")
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size of {MAX_FILE_SIZE_MB}MB.")

    kind = filetype.guess(file_bytes)
    if kind is not None and kind.mime not in ALLOWED_PDF_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File content does not match a PDF format.")

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        extracted_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"
    except PdfReadError:
        raise HTTPException(status_code=400, detail="Corrupted or invalid PDF file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

    if not extracted_text.strip():
        # Fallback to OCR if it's a scanned PDF
        ocr_result = ocr_service.extract_text(file_bytes)
        if ocr_result.get("success"):
            extracted_text = ocr_result.get("extracted_text", "")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="No readable text could be extracted from the uploaded PDF.")

    # Feed extracted PDF text through the full multi-agent pipeline
    initial_state = {
        "input_text": extracted_text,
        "input_url": None,
        "normalized_content": None,
        "threat_result": None,
        "language_result": None,
        "identity_result": None,
        "domain_result": None,
        "recruitment_result": None,
        "risk_manager_result": None,
        "report": None,
        "overall_risk_score": None,
        "overall_threat_level": None,
        "agent_summary": None,
    }

    result = scamshield_workflow.invoke(initial_state)

    risk_manager_result = result.get("risk_manager_result", {})
    norm = result.get("normalized_content", {})

    normalized_metadata = NormalizedMetadata(
        detected_format=norm.get("detected_format", "pdf_text"),
        extracted_urls=norm.get("extracted_urls", []),
        extracted_emails=norm.get("extracted_emails", []),
        extracted_phones=norm.get("extracted_phones", [])
    ) if norm else None

    response = FullAnalysisResponse(
        overall_risk_score=result.get("overall_risk_score", 0),
        overall_threat_level=result.get("overall_threat_level", "LOW"),
        contributing_factors=risk_manager_result.get("contributing_factors", []),
        confidence=risk_manager_result.get("confidence", 0),
        normalized_metadata=normalized_metadata,
        agent_summary=result.get("agent_summary", {}),
        report=result.get("report"),
        threat_result=result.get("threat_result"),
        language_result=result.get("language_result"),
        identity_result=result.get("identity_result"),
        domain_result=result.get("domain_result"),
        recruitment_result=result.get("recruitment_result"),
    )

    # Save to scan history with PDF context
    input_content = f"[PDF Document ({file.filename})]: {extracted_text}"
    _save_scan_to_history(current_user, db, "pdf", input_content, response)

    return response
