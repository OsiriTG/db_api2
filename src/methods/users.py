from typing import Any, Literal

from ..database import db
from . import check_names, check_language_code

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
    new_zoneinfo: str
) -> dict[str, str | Literal[True]]:
    new_zoneinfo = new_zoneinfo.strip()
    if not new_zoneinfo:
        return {"error": "Method error. The zoneinfo field is empty"}

    user, err = await db.user_read(id_or_username)
    if err:
        return {"error": err}

    setattr(user, "zoneinfo", new_zoneinfo)
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