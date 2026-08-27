from fastapi import APIRouter, HTTPException, UploadFile, File
import filetype

from app.models.orchestrator_models import FullAnalysisRequest, FullAnalysisResponse, NormalizedMetadata
from app.graph.workflow import scamshield_workflow
from app.services.ocr.ocr_service import OCRService


router = APIRouter(
    prefix="/analyze-all",
    tags=["Full Analysis Pipeline"]
)

ocr_service = OCRService()

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]


@router.post("/", response_model=FullAnalysisResponse)
def full_analysis(request: FullAnalysisRequest):
    """
    Run the full ScamShield multi-agent analysis pipeline with input preprocessing.

    Accepts any format or key name (e.g. `text`, `message`, `content`, `url`, `body`, raw string).
    Cleans noise/obfuscation, extracts URLs/emails/phones, executes all 5 agents,
    evaluates overall risk through Risk Manager, and generates a user-friendly report.
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

        return FullAnalysisResponse(
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

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis pipeline error: {str(e)}"
        )


@router.post("/image", response_model=FullAnalysisResponse)
async def analyze_image_upload(file: UploadFile = File(...)):
    """
    Run the full ScamShield multi-agent analysis pipeline on an uploaded screenshot or image.

    1. Validates image format and safety constraints.
    2. Runs secure OCR extraction using EasyOCR.
    3. Passes extracted text through the ContentPreprocessor and all specialized agents.
    4. Returns the complete unified scam analysis report.
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
    return full_analysis(FullAnalysisRequest(text=extracted_text))
