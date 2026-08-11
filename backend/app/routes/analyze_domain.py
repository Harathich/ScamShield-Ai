from fastapi import APIRouter, HTTPException
from app.models.domain_models import DomainAnalyzeRequest, DomainAnalyzeResponse
import validators
from app.agents.domain.agent import DomainAgent

router = APIRouter(
    prefix="/analyze-domain",
    tags=["Domain Analysis"]
)

domain_agent = DomainAgent()

@router.post("/", response_model=DomainAnalyzeResponse)
def analyze_domain(request: DomainAnalyzeRequest):
    url_to_test = request.url.strip()
    if not url_to_test.startswith('http://') and not url_to_test.startswith('https://'):
        url_to_test = 'https://' + url_to_test
        
    if validators.url(url_to_test) is not True:
        raise HTTPException(status_code=400, detail="Invalid URL format.")

    try:
        result = domain_agent.analyze(request.url)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
