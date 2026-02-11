from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Confluence Docling RAG"
    
    # Auth (Override via .env)
    CONFLUENCE_URL: str = ""
    CONFLUENCE_USERNAME: str = ""
    CONFLUENCE_API_TOKEN: str = ""
    
    # Processing
    OUTPUT_DIR: Path = Path("/app/output")
    RATE_LIMIT_DELAY: float = 1.5
    
    class Config:
        env_file = ".env"

settings = Settings()
for d in ["html", "images", "chunks"]:
    (settings.OUTPUT_DIR / d).mkdir(parents=True, exist_ok=True)