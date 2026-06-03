from typing import Any, Literal

from ..config import NAMES_MAX_LEN, USERNAME_MAX_LEN, LANGUAGE_CODE_MAX_LEN
from ..database import db


def check_names(
    first_name: str,
    last_name: str | None = None,
    username: str | None = None
) -> str | None:
    """Checks the validity of the first name, last name and username fields."""
    data = locals().copy(); data.pop("username")

    for var in data:
        if var is not None and not var:
            return f"Method error. The first name or last name fields are empty"
        if len(var) > NAMES_MAX_LEN:
            return f"Method error. The first name or last name fields should be maximum {NAMES_MAX_LEN} letters lengh"

    if username is not None and not username:
        return f"Method error. The username field is empty"
    if len(username) > USERNAME_MAX_LEN:
        return f"Method error. The username field should be maximum {USERNAME_MAX_LEN} letters lengh"

    return None

def check_language_code(
    language_code: str
) -> str | None:
    """Checks the validity of the language code field."""
    if not language_code:
        return f"Method error. The language code field is empty"
    if len(language_code) > LANGUAGE_CODE_MAX_LEN:
        return f"Method error. The language code field should be maximum {LANGUAGE_CODE_MAX_LEN} letters lengh"
    return None


async def record_user(
    id: int,
    first_name: str,
    last_name: str | None = None,
    username: str | None = None,
    language_code: str | None = None,
    is_premium: bool | None = None,
    added_to_attachment_menu: bool | None = None,
    can_join_groups: bool | None = None,
    can_read_all_group_messages: bool | None = None,
    supports_guest_queries: bool | None = None,
    supports_inline_queries: bool | None = None,
    can_connect_to_business: bool | None = None,
    has_main_web_app: bool | None = None,
    has_topics_enabled: bool | None = None,
    allows_users_to_create_topics: bool | None = None,
    can_manage_bots: bool | None = None,
    zoneinfo: str | None = None,
) -> dict[str, Any | str]:
    """
    
    """
    if str(id).startswith("-100"):
        return {"error": "Method error. User ID cannot start with '-100'"}

    first_name = first_name.strip()
    if last_name: last_name = last_name.strip()
    if username: username = username.strip()
    err = check_names(first_name, last_name, username)
    if err:
        return {"error": err}

    if language_code:
        err = check_language_code(language_code)
        if err:
            return {"error": err}

    new_user, err = await db.user_create(**locals().copy())
    if err:
        return {"error": err}
    return dict(vars(new_user))

async def get_user(
    id_or_username: int | str
) -> dict[str, Any | str]:
    """
    
    """
    if str(id_or_username).isdigit() and str(id_or_username).startswith("-100"):
        return {"error": "Method error. User ID cannot start with '-100'"}

    user, err = await db.user_read(id_or_username)
    if err:
        return {"error": err}
    return dict(vars(user))

async def update_language_code(
    id_or_username: int | str,
    new_language_code: str
) -> dict[str, str | Literal[True]]:
    new_language_code = new_language_code.strip()
    err = check_language_code(new_language_code)
    if err:
        return {"error": err}

    user, err = await db.user_read(id_or_username)
    if err:
        return {"error": err}

    setattr(user, "language_code", new_language_code)
    user = dict(vars(user))

    _, err = await db.user_create(**user)
    if err:
        return {"error": err}
    return user

async def update_timezone(
    id_or_username: int | str,
    new_timezone: str
) -> dict[str, str | Literal[True]]:
    new_timezone = new_timezone.strip()
    if not new_timezone:
        return {"error": "Method error. The timezone field is empty"}

    user, err = await db.user_read(id_or_username)
    if err:
        return {"error": err}

    setattr(user, "timezone", new_timezone)
    user = dict(vars(user))

    _, err = await db.user_create(**user)
    if err:
        return {"error": err}
    return user

async def unrecord_user(
    id_or_username: int | str
) -> dict[str, Any | str]:
    """
    
    """
    if str(id_or_username).isdigit() and str(id_or_username).startswith("-100"):
        return {"error": "Method error. User ID cannot start with '-100'"}

    res, err = await db.user_delete(id_or_username)
    if err:
        return {"error": err}
    if not res:
        return {"error": "Method error. Given user already doesn't exist"}
    return {"result": res}