from dotenv import load_dotenv; load_dotenv()
from os import getenv

DB_HOST: str = getenv("DB_HOST", "localhost")
DB_DBNAME: str = getenv("DB_DBNAME", "postgres")
DB_PORT: str = getenv("DB_PORT", "5432")
DB_USER: str = getenv("DB_USER", "postgres")
DB_PASSWORD: str = getenv("DB_PASSWORD", "1234")

API_KEY_LEN: int = int(getenv("API_KEY_LEN", "12"))