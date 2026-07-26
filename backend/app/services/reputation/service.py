from app.tools.security.url_utils import URLUtils
from app.tools.security.whois_tool import WhoisTool
from app.tools.security.virustotal_tool import VirusTotalTool


class ReputationService:
    """
    Service responsible for collecting reputation evidence
    from multiple cybersecurity sources.

    This service contains NO LLM logic.
    """

    def __init__(self):
        self.whois = WhoisTool()
        self.virustotal = VirusTotalTool()

    def collect(self, url: str) -> dict:
        """
        Collect reputation evidence for a URL.

        Returns a structured dictionary that will later
        be passed to the LLM.
        """

        domain = URLUtils.extract_domain(url)

        whois_result = self.whois.lookup(domain)

        vt_result = self.virustotal.analyze_url(url)

        return {
            "url": url,
            "domain": domain,
            "whois": whois_result,
            "virustotal": vt_result,
        }