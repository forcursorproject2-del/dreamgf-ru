import torch
from diffusers import FluxPipeline
import json
import os
from utils.cache import Cache, get_prompt_hash
from utils.watermark import add_watermark, image_to_bytes
from config.settings import IMAGE_TIMEOUT
import logging

logger = logging.getLogger(__name__)

# Global pipeline cache
_pipeline = None

def load_pipeline():
    """Load Flux pipeline"""
    global _pipeline
    if _pipeline is None:
        try:
            _pipeline = FluxPipeline.from_pretrained(
                "black-forest-labs/FLUX.1-dev",
                torch_dtype=torch.bfloat16
            ).to("cpu")
            logger.info("Flux pipeline loaded")
        except Exception as e:
            logger.error(f"Failed to load Flux pipeline: {e}")
            _pipeline = None
    return _pipeline

async def generate_image(prompt: str, character_lora: str, cache: Cache = None, is_vip: bool = False, user=None) -> bytes:
    """Generate image with LoRA"""
    try:
        # Check cache first
        if cache:
            prompt_hash = get_prompt_hash(prompt, character_lora)
            cached = await cache.get_image_cache(0, prompt_hash)  # Global cache
            if cached:
                logger.info("Using cached image")
                return cached

        pipeline = load_pipeline()
        if pipeline is None:
            return None

        # Load LoRA
        lora_path = f"lora/{character_lora}"
        if os.path.exists(lora_path):
            pipeline.load_lora_weights(lora_path)
        else:
            logger.warning(f"LoRA not found: {lora_path}")

        # Generate image
        image = pipeline(
            prompt,
            height=1216,
            width=832,
            guidance_scale=7.5,
            num_inference_steps=30
        ).images[0]

        # Add watermark if not VIP and trial ended
        if not is_vip and user.trial_ended:
            image = add_watermark(image, "DreamGF.ru — VIP 990₽")

        # Convert to bytes
        image_bytes = image_to_bytes(image)

        # Cache the result
        if cache and image_bytes:
            await cache.set_image_cache(0, prompt_hash, image_bytes)

        return image_bytes

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
