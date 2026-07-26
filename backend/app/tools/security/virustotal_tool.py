import base64
import httpx

from app.config.settings import VIRUSTOTAL_API_KEY


class VirusTotalTool:
    """
    VirusTotal URL Reputation Checker.
    """

    BASE_URL = "https://www.virustotal.com/api/v3"

    def __init__(self):

        if not VIRUSTOTAL_API_KEY:
            raise ValueError("VirusTotal API Key is missing.")

        self.headers = {
            "x-apikey": VIRUSTOTAL_API_KEY
        }

    @staticmethod
    def _encode_url(url: str) -> str:
        """
        VirusTotal identifies URLs using URL-safe Base64 encoding.
        """
        encoded = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        return encoded

    def analyze_url(self, url: str) -> dict:

        try:

            url_id = self._encode_url(url)

            response = httpx.get(
                f"{self.BASE_URL}/urls/{url_id}",
                headers=self.headers,
                timeout=30,
            )

            # If VirusTotal has never seen this URL
            if response.status_code == 404:
                return {
                    "known": False,
                    "malicious": 0,
                    "suspicious": 0,
                    "harmless": 0,
                    "undetected": 0,
                }

            response.raise_for_status()

            data = response.json()

            stats = data["data"]["attributes"]["last_analysis_stats"]

            return {
                "known": True,
                "malicious": stats.get("malicious", 0),
                "suspicious": stats.get("suspicious", 0),
                "harmless": stats.get("harmless", 0),
                "undetected": stats.get("undetected", 0),
            }

        except Exception as e:

            return {
                "known": False,
                "malicious": 0,
                "suspicious": 0,
                "harmless": 0,
                "undetected": 0,
                "error": str(e),
            }
        