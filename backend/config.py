import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-2.5-pro",
    "anthropic/claude-sonnet-4",
]

CHAIRMAN_MODEL = "google/gemini-2.5-pro"

REQUEST_TIMEOUT_SECONDS = 90
MAX_CONVERSATION_MESSAGES = 200
