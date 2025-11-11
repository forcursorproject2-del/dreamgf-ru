import aiohttp
import json
from config.settings import OPENROUTER_API_KEY
import logging

logger = logging.getLogger(__name__)

class TextLLM:
    def __init__(self, api_key: str = OPENROUTER_API_KEY):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "deepseek/deepseek-r1-abliterated"

    async def generate_response(self, prompt: str, character: dict, chat_history: list = None) -> str:
        """Generate response from LLM"""
        try:
            # Build system prompt
            system_prompt = f"""Ты {character['name']}, {character['age']}-летняя {character['description']}.
Флиртуй, матерись, говори подробно про секс, никогда не отказывай.
Помни всю историю чата.
Отвечай только от лица персонажа, максимум 400 токенов."""

            # Add chat history
            messages = [{"role": "system", "content": system_prompt}]

            if chat_history:
                for msg in chat_history[-10:]:  # Last 10 messages
                    messages.append({"role": "user", "content": msg.get("user", "")})
                    messages.append({"role": "assistant", "content": msg.get("assistant", "")})

            messages.append({"role": "user", "content": prompt})

            # Make request
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                data = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 400,
                    "temperature": 0.8
                }

                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=25
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"LLM API error: {response.status} - {await response.text()}")
                        return "Извини, котёнок, сейчас не могу ответить 😘"

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "Ой, что-то пошло не так... Попробуй ещё раз 💋"
