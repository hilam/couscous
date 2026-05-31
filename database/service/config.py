import os

from dotenv import load_dotenv

load_dotenv()

host = os.getenv("COUSCOUS_DATABASE_HOST", "localhost")
port = os.getenv("COUSCOUS_DATABASE_PORT", "5432")
user = os.getenv("COUSCOUS_DATABASE_USER", "couscous")
password = os.getenv("COUSCOUS_DATABASE_PASS", "couscous")
database = os.getenv("COUSCOUS_DATABASE_NAME", "couscous")

DB_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
