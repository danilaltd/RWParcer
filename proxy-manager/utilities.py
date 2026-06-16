import re
from urllib.parse import urlparse
from ProxyTypes import ProxyType

def normalize_proxy(raw: str, type: ProxyType) -> str | None:
        candidate = raw.strip()
        if not candidate:
            return None

        if "://" not in candidate:
            match type:
                case ProxyType.HTTP:
                    candidate = f"http://{candidate}"
                case ProxyType.SOCKS4:
                    candidate = f"socks4://{candidate}"
                case ProxyType.SOCKS5:
                    candidate = f"socks5://{candidate}"
        
        candidate = re.sub(r'^https://', 'http://', candidate)
        candidate = re.sub(r':[a-zA-Z\s]*$', '', candidate)
        parsed = urlparse(candidate)
        if not parsed.scheme or not parsed.hostname:
            return None

        if parsed.scheme not in {"http", "https", "socks4", "socks5", "socks5h"}:
            return None

        return candidate