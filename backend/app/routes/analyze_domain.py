import validators
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException
from app.models.domain_models import DomainAnalyzeRequest, DomainAnalyzeResponse
from app.agents.domain.agent import DomainAgent

router = APIRouter(
    prefix="/analyze-domain",
    tags=["Domain Analysis"]
)

domain_agent = DomainAgent()


@router.post("/", response_model=DomainAnalyzeResponse)
@router.post("/analyze", response_model=DomainAnalyzeResponse)
def analyze_domain(request: DomainAnalyzeRequest):
    if not request.url or not request.url.strip():
        raise HTTPException(status_code=422, detail="Provide a non-empty URL or domain to analyze.")

    url_to_test = request.url.strip()
    if not url_to_test.startswith('http://') and not url_to_test.startswith('https://'):
        url_to_test = 'https://' + url_to_test

    parsed = urlparse(url_to_test)
    hostname = parsed.hostname or ""
    # Allow normal URLs, or localhost/IPs (which validators.url might reject but we want SSRF to block)
    is_ip_or_local = hostname == 'localhost' or hostname == '[::1]' or all(c in '0123456789.' for c in hostname)

    if validators.url(url_to_test) is not True and not is_ip_or_local:
        raise HTTPException(status_code=400, detail="Invalid URL format.")

    try:
        result = domain_agent.analyze(url_to_test)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Domain analysis failed: {str(e)}"
        )
