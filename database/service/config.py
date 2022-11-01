import os

from dotenv import load_dotenv

load_dotenv()

db_type = os.getenv('COUSCOUS_DATABASE_TYPE')

if db_type == 'asyncpg':
    driver, host, port, user, password, database = (
        "postgresql+asyncpg",
        os.getenv("COUSCOUS_DATABASE_HOST"),
        os.getenv("COUSCOUS_DATABASE_PORT", "5432"),
        os.getenv("COUSCOUS_DATABASE_USER"),
        os.getenv("COUSCOUS_DATABASE_PASS"),
        os.getenv("COUSCOUS_DATABASE_NAME")
    )
    DB_URL = f"{driver}://{user}:{password}@{host}:{port}/{database}"
else:
    driver, database = (
        "sqlite",
        os.getenv("COUSCOUS_DATABASE_NAME")
    )
    DB_URL = f"{driver}:///{database}.sqlite"
