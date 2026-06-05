import os

from dotenv import load_dotenv

load_dotenv()

host = os.getenv("COUSCOUS_DATABASE_HOST", "localhost")
port = os.getenv("COUSCOUS_DATABASE_PORT", "5432")
user = os.getenv("COUSCOUS_DATABASE_USER", "couscous")
password = os.getenv("COUSCOUS_DATABASE_PASS", "couscous")
database = os.getenv("COUSCOUS_DATABASE_NAME", "couscous")

DB_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"

# OAuth
GOOGLE_CLIENT_ID = os.getenv("COUSCOUS_GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("COUSCOUS_GOOGLE_CLIENT_SECRET")
GITHUB_CLIENT_ID = os.getenv("COUSCOUS_GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("COUSCOUS_GITHUB_CLIENT_SECRET")
OAUTH_REDIRECT_URI = os.getenv(
    "COUSCOUS_OAUTH_REDIRECT_URI", "http://localhost:8550/oauth/callback"
)
