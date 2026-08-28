import whois
from datetime import datetime


class WhoisTool:
    """
    Performs WHOIS lookups and returns normalized domain information.
    """

    @staticmethod
    def _parse_creation_date(creation_date):
        """
        Normalize WHOIS creation date.

        Some WHOIS servers return:
        - a single datetime
        - a list of datetimes
        - None
        """

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        return creation_date

    @staticmethod
    def lookup(domain: str) -> dict:
        """
        Performs a WHOIS lookup and returns structured information.
        """

        try:
            data = whois.whois(domain)

            creation_date = WhoisTool._parse_creation_date(
                data.creation_date
            )

            domain_age_days = None

            if isinstance(creation_date, datetime):

                # Handle timezone-aware and timezone-naive datetimes
                if creation_date.tzinfo is not None:
                    current_time = datetime.now(creation_date.tzinfo)
                else:
                    current_time = datetime.now()

                domain_age_days = (
                    current_time - creation_date
                ).days

            return {
                "registered": True,
                "domain": domain,
                "registrar": data.registrar,
                "creation_date": (
                    creation_date.isoformat()
                    if isinstance(creation_date, datetime)
                    else None
                ),
                "domain_age_days": domain_age_days,
            }

        except Exception as e:
            return {
                "registered": False,
                "domain": domain,
                "registrar": None,
                "creation_date": None,
                "domain_age_days": None,
                "error": str(e),
            }