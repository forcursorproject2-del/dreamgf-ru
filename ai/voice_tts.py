import torch
import io
from config.settings import VOICE_TIMEOUT
import logging

logger = logging.getLogger(__name__)

# Global model cache
_model = None
_device = torch.device('cpu')

def load_model():
    """Load Silero TTS model"""
    global _model
    if _model is None:
        try:
            _model = torch.hub.load(
                'snakers4/silero-models',
                'silero_tts',
                language='ru',
                speaker='v5_ru',
                verbose=False
            )
            _model.to(_device)
            logger.info("Silero TTS model loaded")
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            _model = None
    return _model

async def generate_voice(text: str, speaker: str = 'xenia', user=None) -> io.BytesIO:
    """Generate voice from text"""
    try:
        model = load_model()
        if model is None:
            return None

        # SSML for emotions
        ssml_text = f'<speak><prosody rate="slow" pitch="+2st">{text}</prosody></speak>'

        # Generate audio
        audio = model.apply_tts(
            text=ssml_text,
            speaker=speaker,
            sample_rate=24000
        )

        # Convert to bytes
        buffer = io.BytesIO()
        torch.save(audio, buffer)
        buffer.seek(0)

        return buffer

    except Exception as e:
        logger.error(f"Voice generation failed: {e}")
        return None

async def generate_voice_async(text: str, speaker: str = 'xenia', user=None) -> io.BytesIO:
    """Async wrapper for generate_voice"""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_voice_sync, text, speaker, user)

def generate_voice_sync(text: str, speaker: str = 'xenia', user=None) -> io.BytesIO:
    """Sync version for background execution"""
    try:
        model = load_model()
        if model is None:
            return None

        # SSML for emotions
        ssml_text = f'<speak><prosody rate="slow" pitch="+2st">{text}</prosody></speak>'

        # Generate audio
        audio = model.apply_tts(
            text=ssml_text,
            speaker=speaker,
            sample_rate=24000
        )

        # Convert to bytes
        buffer = io.BytesIO()
        torch.save(audio, buffer)
        buffer.seek(0)

        return buffer

    except Exception as e:
        logger.error(f"Voice generation failed: {e}")
        return None

def get_available_speakers() -> list:
    """Get list of available speakers"""
    return ['xenia', 'baya', 'kseniya']
