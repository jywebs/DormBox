"""Amazon URL enrichment service."""
import re
from typing import Optional, Dict
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl

class EnrichmentResponse(BaseModel):
    """Enrichment response model."""
    title: Optional[str] = None
    imageUrl: Optional[HttpUrl] = None
    asin: Optional[str] = None

class EnrichmentService:
    """Service for enriching Amazon URLs with product data."""

    ALLOWED_DOMAINS = ["amazon.com", "www.amazon.com"]
    ASIN_PATTERNS = [
        r"/dp/([A-Z0-9]{10})",
        r"/gp/product/([A-Z0-9]{10})",
        r"/product/([A-Z0-9]{10})",
    ]

    @staticmethod
    def validate_amazon_url(url: str) -> bool:
        """Validate if the URL is from Amazon."""
        try:
            parsed = urlparse(url)
            return parsed.netloc in EnrichmentService.ALLOWED_DOMAINS
        except:
            return False

    @staticmethod
    def extract_asin(url: str) -> Optional[str]:
        """Extract ASIN from Amazon URL."""
        for pattern in EnrichmentService.ASIN_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    async def enrich_url(url: str) -> EnrichmentResponse:
        """Fetch and parse product data from Amazon URL."""
        if not EnrichmentService.validate_amazon_url(url):
            raise ValueError("Invalid Amazon URL")

        timeout = httpx.Timeout(5.0, connect=2.0)
        headers = {
            "User-Agent": "DormBox/1.0",
            "Accept": "text/html,application/xhtml+xml",
        }

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            try:
                # First try a HEAD request to check content type
                head_resp = await client.head(url, headers=headers)
                if not head_resp.headers.get("content-type", "").startswith("text/html"):
                    raise ValueError("URL does not return HTML content")

                # Then get the full page
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                # Extract Open Graph data
                title = (
                    soup.find("meta", property="og:title") or
                    soup.find("meta", attrs={"name": "title"}) or
                    soup.find("title")
                )
                image = (
                    soup.find("meta", property="og:image") or
                    soup.find("meta", attrs={"name": "image"})
                )

                return EnrichmentResponse(
                    title=title["content"] if title and title.has_attr("content") 
                          else title.text if title else None,
                    imageUrl=image["content"] if image and image.has_attr("content") 
                             else None,
                    asin=EnrichmentService.extract_asin(url)
                )
            except httpx.TimeoutException:
                raise ValueError("Request timed out")
            except httpx.HTTPError as e:
                raise ValueError(f"HTTP error: {str(e)}")
            except Exception as e:
                raise ValueError(f"Error fetching product data: {str(e)}")