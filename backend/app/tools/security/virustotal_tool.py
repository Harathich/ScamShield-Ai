import base64
import requests
import os

# Assume config/settings.py has VIRUSTOTAL_API_KEY, but fallback to os.getenv if missing
try:
    from app.config.settings import VIRUSTOTAL_API_KEY
except ImportError:
    VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

class VirusTotalTool:
    """
    VirusTotal URL Reputation Checker.
    """

    BASE_URL = "https://www.virustotal.com/api/v3"

    def __init__(self):
        self.api_key = VIRUSTOTAL_API_KEY
        self.headers = {}
        if self.api_key:
            self.headers["x-apikey"] = self.api_key

    @staticmethod
    def _encode_url(url: str) -> str:
        """
        VirusTotal identifies URLs using URL-safe Base64 encoding without padding.
        """
        encoded = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        return encoded

    def analyze_url(self, url: str) -> dict:
        if not self.api_key:
            return {
                "known": False,
                "malicious": 0,
                "suspicious": 0,
                "harmless": 0,
                "undetected": 0,
                "error": "VirusTotal API Key is missing. Reputation data unavailable."
            }

        try:
            url_id = self._encode_url(url)
            
            # This is an external API call to VirusTotal, so SSRF restrictions for internal IPs don't apply to this specific outbound request to www.virustotal.com
            response = requests.get(
                f"{self.BASE_URL}/urls/{url_id}",
                headers=self.headers,
                timeout=10,
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
