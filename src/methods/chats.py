from typing import Any

from datetime import datetime

from ..config import TYPE_STATES, TITLE_MAX_LEN
from ..database import db
from ..utils import http_error, check_names, check_language_code

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
    Stores chat's data.

    Source: https://docs.aiogram.dev/en/v3.28.2/api/types/chat.html

    :param zoneinfo: *Optional*. The string that will be used to fill ZoneInfo (Source: https://docs.python.org/3/library/zoneinfo.html#the-zoneinfo-class).
    :return: On success will return dict of :class:`aiogram.types.chat.Chat` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    data = locals().copy()

    data['type'] = type.strip()
    if not data['type']:
        return http_error(400, "The type field is empty", "type", "missing_required_field")
    if data['type'] not in TYPE_STATES:
        return http_error(400, f"Chat type must be in {', '.join(TYPE_STATES)}", "type", "invalid_value")

    if title is not None:
        data['title'] = title.strip()
        if not data['title']:
            return http_error(400, "The title field is empty", "title", "missing_field")
        if len(data['title']) > TITLE_MAX_LEN:
            return http_error(400, f"The title field can be a maximum of {TITLE_MAX_LEN} letters in length", "title", "title_too_long")

    data['first_name'] = first_name.strip()
    if last_name: data['last_name'] = last_name.strip()
    if username: data['username'] = username.strip()
    err = check_names(data['first_name'], data['last_name'], data['username'])
    if err:
        return err

    if language_code:
        data['language_code'] = language_code.strip()
        err = check_language_code(data['language_code'])
        if err:
            return err

    if owner_id:
        _, err = await db.user_read(owner_id)
        if err:
            return err

    if zoneinfo:
        data['zoneinfo'] = zoneinfo.strip()
        if not data['zoneinfo']:
            return http_error(400, "The zoneinfo field is empty", "zoneinfo", "missing_field")

    new_chat, err = await db.chat_create_update(**data)
    if err:
        return err
    return dict(vars(new_chat))

async def get_chat(
    id_or_username: int | str
) -> dict[str, Any | str]:
    """
    Returns chat's data.

    :param id_or_username: The chat's ID or username whose data needs to be obtained.
    :return: On success will return dict of :class:`aiogram.types.chat.Chat` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    chat, err = await db.chat_read(id_or_username)
    if err:
        return err
    return dict(vars(chat))

async def change_chat_language_code(
    id_or_username: int | str,
    new_language_code: str
) -> dict[str, Any]:
    """
    Updates chat's language_code.

    :param id_or_username: The chat's ID or username whose data needs to be updated.
    :param new_language_code: New value of language code.
    :return: On success will return dict of :class:`aiogram.types.chat.Chat` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    new_language_code = new_language_code.strip()
    err = check_language_code(new_language_code)
    if err:
        return err

    chat, err = await db.chat_read(id_or_username)
    if err:
        return err
    setattr(chat, "language_code", new_language_code)
    chat = dict(vars(chat))

    _, err = await db.chat_create_update(**chat)
    if err:
        return err
    return chat

async def change_chat_zoneinfo(
    id_or_username: int | str,
    new_zoneinfo: str
) -> dict[str, Any]:
    """
    Updates chat's zoneinfo.

    :param id_or_username: The chat's ID or username whose data needs to be updated.
    :param new_zoneinfo: New value of zoneinfo (Source: https://docs.python.org/3/library/zoneinfo.html#the-zoneinfo-class).
    :return: On success will return dict of :class:`aiogram.types.chat.Chat` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    new_zoneinfo = new_zoneinfo.strip()
    if not new_zoneinfo:
        return http_error(400, "The zoneinfo field is empty", "zoneinfo", "missing_required_field")

    chat, err = await db.chat_read(id_or_username)
    if err:
        return err
    setattr(chat, "zoneinfo", new_zoneinfo)
    chat = dict(vars(chat))

    _, err = await db.chat_create_update(**chat)
    if err:
        return err
    return chat

async def unrecord_chat(
    id_or_username: int | str
) -> dict[str, bool | Any]:
    """
    Deletes chat's data.

    :param id_or_username: The chat's ID or username whose data needs to be deleted.
    :return: On success will return :code:`True` or if rowcount is stil 0 - :code:`False` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    res, err = await db.chat_delete(id_or_username)
    if err:
        return err
    return {
        "result": res,
        "timestamptz": datetime.now()
    }