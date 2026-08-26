from urllib.parse import urlparse


class URLUtils:
    """
    Utility class for URL normalization and domain extraction.
    """

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Ensures every URL has a scheme.

        Example:
            google.com
            -> https://google.com
        """

        url = url.strip()

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        return url

    @staticmethod
    def extract_domain(url: str) -> str:
        """
        Extracts the domain name from a URL.

        Example:
            https://www.google.com/search

        Returns:
            google.com
        """

        normalized_url = URLUtils.normalize_url(url)

        parsed = urlparse(normalized_url)

        domain = parsed.netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain