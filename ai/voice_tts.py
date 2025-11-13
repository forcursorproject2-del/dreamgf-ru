import asyncio
import io
import os
from typing import Optional
import logging
import torch
import soundfile as sf
from config.settings import VOICE_TIMEOUT

logger = logging.getLogger(__name__)

# Global TTS model cache
_tts_model = None
_device = torch.device("cpu")

def load_tts_model():
    """Load Silero TTS model"""
    global _tts_model
    if _tts_model is None:
        try:
            _tts_model = torch.hub.load("snakers4/silero-models", "silero_tts", language="ru", speaker="v3_1_ru")
            _tts_model.to(_device)
            logger.info("Silero TTS model loaded")
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            _tts_model = None
    return _tts_model

async def generate_voice_async(text: str, speaker: str = "xenia", user=None) -> Optional[bytes]:
    """Generate voice using Silero TTS with SSML support"""
    try:
        # Check trial limits
        if user and not user.is_vip and user.trial_voice_used:
            return None

        model = load_tts_model()
        if model is None:
            return None

        # Add SSML for better voice
        ssml_text = f'<prosody rate="1.1">{text}</prosody>'

        # Generate audio
        audio = model.apply_tts(
            text=ssml_text,
            speaker=speaker,
            sample_rate=48000
        )

        # Convert to bytes
        buffer = io.BytesIO()
        sf.write(buffer, audio.numpy(), 48000, format='OGG')
        audio_bytes = buffer.getvalue()

        # Mark trial as used
        if user and not user.is_vip:
            user.trial_voice_used = True

        return audio_bytes

    except Exception as e:
        logger.error(f"Voice generation failed: {e}")
        return None

def get_available_speakers() -> list:
    """Get list of available speakers"""
    return ['xenia', 'baya', 'kseniya']
