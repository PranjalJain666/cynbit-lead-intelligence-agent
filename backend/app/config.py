import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root or backend folder
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
env_path = ROOT_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

class Settings:
    PROJECT_NAME: str = "Cynbit Lead Intelligence Agent"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = (
        "AI-powered project inquiry analysis, requirement extraction, "
        "and explainable lead qualification for Cynbit."
    )
    API_PREFIX: str = "/api/v1"
    
    # Groq Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_FALLBACK_MODEL: str = os.getenv("GROQ_FALLBACK_MODEL", "llama-3.1-8b-instant")
    
    # Database Configuration
    DATABASE_PATH: str = os.getenv(
        "DATABASE_PATH", str(ROOT_DIR / "backend" / "inquiries.db")
    )
    
    # Server configuration
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

settings = Settings()
