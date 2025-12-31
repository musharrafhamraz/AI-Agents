
from src.config.settings import settings
import os

print(f"LLM_PROVIDER: '{settings.LLM_PROVIDER}'")
print(f"ENABLE_VECTOR_SEARCH: {settings.ENABLE_VECTOR_SEARCH}")
print(f"EMBEDDING_MODEL: '{settings.EMBEDDING_MODEL}'")
print(f"OPENAI_API_KEY present: {bool(settings.OPENAI_API_KEY)}")
print(f"GROQ_API_KEY present: {bool(settings.GROQ_API_KEY)}")
if settings.GROQ_API_KEY:
    print(f"GROQ_API_KEY preview: {settings.GROQ_API_KEY[:4]}...")

print(f"Environment variables:")
print(f"LLM_PROVIDER env: {os.environ.get('LLM_PROVIDER')}")
