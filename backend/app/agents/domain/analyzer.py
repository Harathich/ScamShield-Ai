import ssl
import socket
import whois
import tldextract
import validators
import requests
from urllib.parse import urlparse
import ipaddress
from datetime import datetime
import re

from app.tools.security.virustotal_tool import VirusTotalTool

SUSPICIOUS_TLDS = {'.xyz', '.top', '.club', '.online', '.site', '.click', '.cc'}
URL_SHORTENERS = {'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly'}
KNOWN_BRANDS = ['amazon', 'google', 'paytm', 'apple', 'microsoft', 'facebook', 'netflix', 'paypal', 'bankofamerica', 'chase', 'wellsfargo']

class DomainAnalyzer:
    def __init__(self):
        self.vt_tool = VirusTotalTool()

    def analyze(self, url: str) -> dict:
        result = {}
        
        # 1. URL Validation & Normalization
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
            
        is_valid = (validators.url(url) is True)
        result['url_valid'] = is_valid
        
        if not is_valid:
            result['error'] = "Invalid URL structure."
            return result
            
        parsed_url = urlparse(url)
        domain_name = parsed_url.netloc
        
        # 2. Domain Extraction
        extracted = tldextract.extract(url)
        root_domain = f"{extracted.domain}.{extracted.suffix}"
        result['domain'] = root_domain
        result['subdomain'] = extracted.subdomain
        
        # 3 & 5. WHOIS Information and Domain Age
        result['whois'] = self._get_whois_info(root_domain)
        result['domain_age'] = self._calculate_domain_age(result['whois'].get('creation_date'))
        
        # 4. SSL Certificate Analysis
        result['ssl'] = self._get_ssl_info(domain_name)
        
        # 6. URL Structure Analysis
        result['structure_analysis'] = self._analyze_structure(url, domain_name, root_domain, extracted.subdomain)
        
        # 7. Brand Impersonation
        result['brand_impersonation'] = self._check_brand_impersonation(extracted.domain)
        
        # 8. HTTP Accessibility Check
        result['http_accessibility'] = self._check_http_accessibility(url)
        
        # 9. Reputation Layer (VirusTotal)
        result['reputation'] = self.vt_tool.analyze_url(url)
        
        return result

    def _get_whois_info(self, domain: str) -> dict:
        try:
            w = whois.whois(domain)
            creation_date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
            expiration_date = w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date
            return {
                'registrar': w.registrar,
                'country': w.country,
                'creation_date': creation_date.isoformat() if isinstance(creation_date, datetime) else str(creation_date),
                'expiration_date': expiration_date.isoformat() if isinstance(expiration_date, datetime) else str(expiration_date),
                'name_servers': w.name_servers
            }
        except Exception as e:
            return {'error': f"WHOIS lookup failed: {str(e)}"}

    def _calculate_domain_age(self, creation_date) -> str:
        if not creation_date or creation_date == "None":
            return "Unknown"
        try:
            if isinstance(creation_date, str):
                creation_date = datetime.fromisoformat(creation_date)
            now = datetime.now()
            age_timedelta = now - creation_date
            days = age_timedelta.days
            if days < 30:
                return f"{days} days (Very Recent)"
            elif days < 365:
                return f"{days // 30} months"
            else:
                return f"{days // 365} years"
        except Exception:
            return "Unknown"

    def _get_ssl_info(self, hostname: str) -> dict:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    issuer = dict(x[0] for x in cert['issuer'])
                    return {
                        'valid': True,
                        'issuer': issuer.get('organizationName', 'Unknown'),
                        'expiry': cert.get('notAfter', 'Unknown')
                    }
        except ssl.SSLError:
            return {'valid': False, 'error': 'SSL Certificate Error (Invalid/Expired)'}
        except socket.timeout:
            return {'valid': False, 'error': 'Connection Timeout'}
        except Exception as e:
            return {'valid': False, 'error': f"Failed to retrieve SSL: {str(e)}"}

    def _analyze_structure(self, url: str, domain_name: str, root_domain: str, subdomain: str) -> dict:
        flags = []
        # Long URL
        if len(url) > 75:
            flags.append("Long URL")
            
        # Subdomains
        sub_parts = subdomain.split('.') if subdomain else []
        if len(sub_parts) > 2:
            flags.append("Too many subdomains")
            
        # IP-based
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain_name):
            flags.append("IP-based URL")
            
        # Suspicious TLD
        if any(root_domain.endswith(tld) for tld in SUSPICIOUS_TLDS):
            flags.append("Suspicious TLD")
            
        # Shortener
        if root_domain in URL_SHORTENERS:
            flags.append("URL Shortener")
            
        # Special/Encoded characters (e.g. '@', '%')
        if '@' in url:
            flags.append("Contains '@' symbol (Credential inclusion)")
            
        return {
            'red_flags': flags,
            'is_suspicious': len(flags) > 0
        }

    def _check_brand_impersonation(self, domain_part: str) -> bool:
        domain_lower = domain_part.lower()
        # Look for leetspeak or typos (basic heuristic)
        # Replacing common leetspeak characters
        normalized = domain_lower.replace('0', 'o').replace('1', 'l').replace('3', 'e')
        
        for brand in KNOWN_BRANDS:
            # Exact match (if they don't own the domain, but for simplicity here we just check if it's identical or typo)
            if brand in normalized and normalized != brand:
                return True
        return False

    def _is_safe_ip(self, hostname: str) -> bool:
        try:
            ip = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved or ip_obj.is_unspecified:
                return False
            return True
        except socket.gaierror:
            return False
        except ValueError:
            return False

    def _check_http_accessibility(self, url: str) -> dict:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname or not self._is_safe_ip(hostname):
            return {'accessible': False, 'error': 'Security restriction: Cannot request internal or private IPs.'}
            
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            # Disabling redirects to prevent redirect-based SSRF to internal networks
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=False)
            if response.status_code in [200, 301, 302, 307, 308]:
                return {'accessible': True, 'status_code': response.status_code, 'note': 'Site is accessible.'}
            elif response.status_code in [403, 401]:
                return {'accessible': False, 'status_code': response.status_code, 'note': 'Access blocked (e.g., Cloudflare, WAF, or Auth required).'}
            else:
                return {'accessible': False, 'status_code': response.status_code, 'note': f'Site returned HTTP {response.status_code}'}
        except requests.exceptions.Timeout:
            return {'accessible': False, 'error': 'Connection timed out.'}
        except requests.exceptions.RequestException as e:
            return {'accessible': False, 'error': 'Failed to connect (Host down or blocked).'}
