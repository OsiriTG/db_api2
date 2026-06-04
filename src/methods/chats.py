from typing import Any, Literal

from ..config import TYPE_STATES, TITLE_MAX_LEN
from ..database import db
from . import check_names, check_language_code

async def record_chat(
    id: int,
    type: str,
    title: str | None = None,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    is_forum: bool | None = None,
    is_direct_messages: bool | None = None,
    language_code: str | None = None,
    owner_id: int | None = None,
    zoneinfo: str | None = None,
) -> dict[str, Any | str]:
    """
    
    """
    type = type.strip()
    if not type:
        return {"error": "Method error. The type field is empty"}
    if type not in TYPE_STATES:
        return {"error": f"Method error. Chat type must be in {TYPE_STATES}"}

    title = title.strip()
    if not title:
        return {"error": "Methods error. The title field is empty"}
    if len(title) > TITLE_MAX_LEN:
        return {"error": f"Method error. The title field should be maximum {TITLE_MAX_LEN} letters lengh"}

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

    if owner_id:
        _, err = await db.user_read(owner_id)
        if err:
            return {"error": err}

    if zoneinfo:
        zoneinfo = zoneinfo.strip()
        if not zoneinfo:
            return {"error": "Method error. The zoneinfo field is empty"}

    new_chat, err = await db.chat_create(**locals().copy())
    if err:
        return {"error": err}
    return dict(vars(new_chat))

async def get_chat(
    id_or_username: int | str
) -> dict[str, Any | str]:
    """
    
    """
    chat, err = await db.chat_read(id_or_username)
    if err:
        return {"error": err}
    return dict(vars(chat))

async def update_chat_language_code(
    id_or_username: int | str,
    new_language_code: str
) -> dict[str, str | Literal[True]]:
    new_language_code = new_language_code.strip()
    err = check_language_code(new_language_code)
    if err:
        return {"error": err}

    chat, err = await db.chat_read(id_or_username)
    if err:
        return {"error": err}

    setattr(chat, "language_code", new_language_code)
    chat = dict(vars(chat))

    _, err = await db.chat_create(**chat)
    if err:
        return {"error": err}
    return chat

async def update_chat_zoneinfo(
    id_or_username: int | str,
    new_zoneinfo: str
) -> dict[str, str | Literal[True]]:
    new_zoneinfo = new_zoneinfo.strip()
    if not new_zoneinfo:
        return {"error": "Method error. The zoneinfo field is empty"}

    chat, err = await db.chat_read(id_or_username)
    if err:
        return {"error": err}

    setattr(chat, "zoneinfo", new_zoneinfo)
    chat = dict(vars(chat))

    _, err = await db.chat_create(**chat)
    if err:
        return {"error": err}
    return chat

async def unrecord_chat(
    id_or_username: int | str
) -> dict[str, Any | str]:
    """
    
    """
    res, err = await db.chat_delete(id_or_username)
    if err:
        return {"error": err}
    if not res:
        return {"error": "Method error. Given chat already doesn't exist"}
    return {"result": res}