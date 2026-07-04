import os
from dataclasses import dataclass
from functools import lru_cache

import certifi
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


@dataclass(frozen=True)
class Settings:
    groq_api_key: str | None
    groq_model: str
    database_url: str | None
    app_env: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        database_url=os.getenv("DATABASE_URL"),
        app_env=os.getenv("APP_ENV", "development").lower(),
    )


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    settings = get_settings()

    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your environment or .env file.")

    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
    )
