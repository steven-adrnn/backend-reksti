import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Settings(BaseSettings):
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    supabase_bucket: str = os.getenv("SUPABASE_BUCKET", "user-videos")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    jwt_algorithm: str = "HS256"
    websocket_host: str = os.getenv("WEBSOCKET_HOST", "0.0.0.0")
    websocket_port: int = int(os.getenv("WEBSOCKET_PORT", 8000))

settings = Settings()
