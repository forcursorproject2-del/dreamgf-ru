import httpx
import json
import os
import asyncio
import uuid
from utils.cache import Cache, get_prompt_hash
from utils.watermark import add_watermark, image_to_bytes
from config.settings import IMAGE_TIMEOUT, OPENROUTER_API_KEY
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)

async def generate_image_async(prompt: str, character_lora: str, cache: Cache = None, is_vip: bool = False, user=None) -> str:
    """Generate image via OpenRouter API"""
    try:
        # Check cache first
        if cache:
            prompt_hash = get_prompt_hash(prompt, character_lora)
            cached = await cache.get_image_cache(0, prompt_hash)  # Global cache
            if cached:
                logger.info("Using cached image")
                # Save cached image to temp file
                temp_filename = f"temp/photo_{uuid.uuid4()}.jpg"
                os.makedirs("temp", exist_ok=True)
                with open(temp_filename, "wb") as f:
                    f.write(cached)
                return temp_filename

        # Prepare prompt
        full_prompt = f"Russian girl 19 y.o., {prompt}, realistic, 4k, nsfw"

        async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "black-forest-labs/flux-dev",
                    "prompt": full_prompt,
                    "n": 1,
                    "size": "1024x1024"
                }
            )

            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return None

            data = response.json()
            image_url = data["data"][0]["url"]

            # Download image
            image_response = await client.get(image_url)
            if image_response.status_code != 200:
                logger.error(f"Failed to download image: {image_response.status_code}")
                return None

            image_bytes = image_response.content

            # Process image
            image = Image.open(io.BytesIO(image_bytes))

            # Add watermark if not VIP and trial ended
            if not is_vip and user and user.trial_ended:
                image = add_watermark(image, "DreamGF.ru — VIP 990₽")

            # Convert to bytes
            image_bytes = image_to_bytes(image)

            # Save to temp file
            temp_filename = f"temp/photo_{uuid.uuid4()}.jpg"
            os.makedirs("temp", exist_ok=True)
            with open(temp_filename, "wb") as f:
                f.write(image_bytes)

            # Cache the result
            if cache and image_bytes:
                await cache.set_image_cache(0, prompt_hash, image_bytes)

            return temp_filename

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        return None

def download_lora(url: str, filename: str):
    """Download LoRA from URL"""
    try:
        import requests
        os.makedirs("lora", exist_ok=True)
        response = requests.get(url)
        with open(f"lora/{filename}", "wb") as f:
            f.write(response.content)
        logger.info(f"LoRA downloaded: {filename}")
    except Exception as e:
        logger.error(f"Failed to download LoRA: {e}")
