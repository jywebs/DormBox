"""QR code generation service."""
import qrcode
import io
import base64
from typing import Optional
from pydantic import BaseModel

class QRResponse(BaseModel):
    """QR code response model."""
    base64_image: str
    url: str
    slug: str

class QRService:
    """Service for generating QR codes."""

    @staticmethod
    def generate_qr(
        slug: str,
        base_url: str = "https://dormbox.app/boxes/qr/",
        size: int = 10,
        border: int = 4
    ) -> QRResponse:
        """Generate a QR code for a box."""
        url = f"{base_url.rstrip('/')}/{slug}"
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        
        # Add data
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return QRResponse(
            base64_image=img_str,
            url=url,
            slug=slug
        )