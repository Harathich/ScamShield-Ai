from fastapi import APIRouter, UploadFile, File, HTTPException
import filetype

from app.models.ocr_models import OCRResponse
from app.services.ocr.ocr_service import OCRService

router = APIRouter(
    prefix="/ocr",
    tags=["OCR Analysis"]
)

ocr_service = OCRService()

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]

@router.post("/", response_model=OCRResponse)
async def process_ocr(file: UploadFile = File(...)):
    # 1. Validate empty file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    # 2. Validate MIME type explicitly sent by client
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}. Supported types are JPEG, PNG, and WEBP.")

    # 3. Read bytes and validate file size safely
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size of {MAX_FILE_SIZE_MB}MB.")

    # 4. Validate actual file type using magic bytes (file signature)
    kind = filetype.guess(file_bytes)
    if kind is None or kind.mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File content does not match a supported image format.")

    # 5. Extract text via OCRService
    result = ocr_service.extract_text(file_bytes)

    # 6. Return response
    if not result.get("success"):
        return OCRResponse(
            success=False,
            error=result.get("error")
        )

    return OCRResponse(
        success=True,
        extracted_text=result.get("extracted_text"),
        confidence=result.get("confidence"),
        language=result.get("language")
    )
