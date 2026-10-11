import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_ID: str = os.getenv("PROJECT_ID", "sipsense-ai-demo")
    REGION: str = os.getenv("REGION", "asia-south1")
    VERTEX_LOCATION: str = os.getenv("VERTEX_LOCATION", "us-central1")
    INSTANCE_CONNECTION_NAME: str = os.getenv("INSTANCE_CONNECTION_NAME", "sipsense-ai-demo:asia-south1:sipsense-pg")
    
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "sipsense")
    DB_USER: str = os.getenv("DB_USER", "sipsense_app")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "Asdf@6891")
    
    # Gemini
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Credentials
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    if GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    @property
    def database_url(self) -> str:
        import urllib.parse
        encoded_password = urllib.parse.quote_plus(self.DB_PASSWORD)
        unix_socket_dir = f"/cloudsql/{self.INSTANCE_CONNECTION_NAME}"
        if os.path.exists(unix_socket_dir):
            return f"postgresql+psycopg2://{self.DB_USER}:{encoded_password}@/{self.DB_NAME}?host={unix_socket_dir}"
        return f"postgresql+psycopg2://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
