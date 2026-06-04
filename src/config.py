from string import ascii_letters, digits

base64 = ascii_letters + digits + "_" + "-"


from dotenv import load_dotenv
from os import getenv

load_dotenv()

DB_HOST: str = getenv("DB_HOST", "localhost")
DB_DBNAME: str = getenv("DB_DBNAME", "postgres")
DB_PORT: str = getenv("DB_PORT", "5432")
DB_USER: str = getenv("DB_USER", "postgres")
DB_PASSWORD: str = getenv("DB_PASSWORD", "1234")

API_KEY_LEN: int = int(getenv("API_KEY_LEN", "12"))
PERMISSIONS_MAX_LEN: int = 4

NAMES_MAX_LEN: int = 64
USERNAME_MAX_LEN: int = 32
LANGUAGE_CODE_MAX_LEN: int = 2
TYPE_STATES: tuple[str] = ("private", "group", "supergroup", "channel")
TITLE_MAX_LEN: int = 128