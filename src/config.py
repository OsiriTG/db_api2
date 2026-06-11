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

API_DOMAIN: str = getenv("API_DOMAIN", "127.0.0.1")
API_PORT: int = int(getenv("API_PORT", "8000"))
API_PROTOCOL: str = getenv("API_PROTOCOL", "http")
API_KEY_LEN: int = int(getenv("API_KEY_LEN", "12"))

PERMISSIONS_MAX_LEN: int = 4 # Table "api_keys"
NAMES_MAX_LEN: int = 64 # Table "users" & "chats"
USERNAME_MAX_LEN: int = 32 # Table "users" & "chats"
LANGUAGE_CODE_MAX_LEN: int = 2 # Table "users" & "chats"
TYPE_STATES: tuple[str] = ("private", "group", "supergroup", "channel") # Table "chats"
TITLE_MAX_LEN: int = 128 # Table "chats"


from pydantic import BaseModel, Field

class ChangeLanguageCode(BaseModel):
    id_or_username: int | str
    new_language_code: str = Field(..., max_length=LANGUAGE_CODE_MAX_LEN)

class ChangeZoneinfo(BaseModel):
    id_or_username: int | str
    new_zoneinfo: str