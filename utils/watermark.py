from PIL import Image, ImageDraw, ImageFont
import io
from config.settings import WATERMARK_TEXT
import logging

logger = logging.getLogger(__name__)

def add_watermark(image: Image.Image, text: str = WATERMARK_TEXT) -> Image.Image:
    """Add watermark to image"""
    try:
        # Create a copy of the image
        img = image.copy()

        # Create drawing context
        draw = ImageDraw.Draw(img)

        # Try to load a font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        # Get text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Position watermark at bottom right
        x = img.width - text_width - 10
        y = img.height - text_height - 10

        # Add semi-transparent background
        draw.rectangle(
            [x-5, y-5, x + text_width + 5, y + text_height + 5],
            fill=(0, 0, 0, 128)
        )

        # Add text
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 200))

        return img

    except Exception as e:
        logger.error(f"Failed to add watermark: {e}")
        return image

def image_to_bytes(image: Image.Image, format: str = "JPEG") -> bytes:
    """Convert PIL Image to bytes"""
    try:
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Failed to convert image to bytes: {e}")
        return None

def bytes_to_image(data: bytes) -> Image.Image:
    """Convert bytes to PIL Image"""
    try:
        buffer = io.BytesIO(data)
        return Image.open(buffer)
    except Exception as e:
        logger.error(f"Failed to convert bytes to image: {e}")
        return None
