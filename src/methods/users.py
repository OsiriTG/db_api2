from typing import Any

from datetime import datetime

from ..database import db
from ..utils import http_error, check_names, check_username, check_language_code

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
) -> dict[str, Any]:
    """
    Stores user's data.

    Source: https://docs.aiogram.dev/en/v3.28.2/api/types/user.html

    :param zoneinfo: *Optional*. The string that will be used to fill ZoneInfo (Source: https://docs.python.org/3/library/zoneinfo.html#the-zoneinfo-class).
    :return: On success will return dict of :class:`aiogram.types.user.User` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    if str(id).startswith("-100"):
        return http_error(400, "User ID cannot start with '-100'", "id", "invalid_id_format")

    data = locals().copy()

    data['first_name'] = first_name.strip()
    if last_name: data['last_name'] = last_name.strip()
    if username: data['username'] = username.strip().strip("@")
    err = check_names(data['first_name'], data['last_name'], data['username'])
    if err:
        return err

    if language_code:
        data['language_code'] = language_code.strip()
        err = check_language_code(data['language_code'])
        if err:
            return err

    new_user, err = await db.user_create_update(**data)
    if err:
        return err
    return dict(vars(new_user))

async def get_user(
    id_or_username: int | str
) -> dict[str, Any]:
    """
    Returns user's data.

    :param id_or_username: The user's ID or username whose data needs to be obtained.
    :return: On success will return dict of :class:`aiogram.types.user.User` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    if str(id_or_username).isdigit() and str(id_or_username).strip().startswith("-100"):
        return http_error(400, "User ID cannot start with '-100'", "id", "invalid_id_format")
    if str(id_or_username).strip().startswith("@"):
        id_or_username = id_or_username.strip().strip("@")
        err = check_username(id_or_username)
        if err:
            return err

    user, err = await db.user_read(id_or_username)
    if err:
        return err
    return dict(vars(user))

async def change_language_code(
    id_or_username: int | str,
    new_language_code: str
) -> dict[str, Any]:
    """
    Updates user's language_code.

    :param id_or_username: The user's ID or username whose data needs to be updated.
    :param new_language_code: New value of language code.
    :return: On success will return dict of :class:`aiogram.types.user.User` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    if str(id_or_username).isdigit() and str(id_or_username).strip().startswith("-100"):
        return http_error(400, "User ID cannot start with '-100'", "id", "invalid_id_format")
    if str(id_or_username).strip().startswith("@"):
        id_or_username = id_or_username.strip().strip("@")
        err = check_username(id_or_username)
        if err:
            return err

    new_language_code = new_language_code.strip()
    err = check_language_code(new_language_code)
    if err:
        return err

    user, err = await db.user_read(id_or_username)
    if err:
        return err
    setattr(user, "language_code", new_language_code)
    user = dict(vars(user))

    _, err = await db.user_create_update(**user)
    if err:
        return err
    return user

async def change_zoneinfo(
    id_or_username: int | str,
    new_zoneinfo: str
) -> dict[str, Any]:
    """
    Updates user's zoneinfo.

    :param id_or_username: The user's ID or username whose data needs to be updated.
    :param new_zoneinfo: New value of zoneinfo (Source: https://docs.python.org/3/library/zoneinfo.html#the-zoneinfo-class).
    :return: On success will return dict of :class:`aiogram.types.user.User` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    if str(id_or_username).isdigit() and str(id_or_username).strip().startswith("-100"):
        return http_error(400, "User ID cannot start with '-100'", "id", "invalid_id_format")
    if str(id_or_username).strip().startswith("@"):
        id_or_username = id_or_username.strip().strip("@")
        err = check_username(id_or_username)
        if err:
            return err

    new_zoneinfo = new_zoneinfo.strip()
    if not new_zoneinfo:
        return http_error(400, "The zoneinfo field is empty", "zoneinfo", "missing_required_field")

    user, err = await db.user_read(id_or_username)
    if err:
        return err
    setattr(user, "zoneinfo", new_zoneinfo)
    user = dict(vars(user))

    _, err = await db.user_create_update(**user)
    if err:
        return err
    return user

async def unrecord_user(
    id_or_username: int | str
) -> dict[str, bool | Any]:
    """
    Deletes user's data.

    :param id_or_username: The user's ID or username whose data needs to be deleted.
    :return: On success will return :code:`True` or if rowcount is stil 0 - :code:`False` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    if str(id_or_username).isdigit() and str(id_or_username).strip().startswith("-100"):
        return http_error(400, "User ID cannot start with '-100'", "id", "invalid_id_format")
    if str(id_or_username).strip().startswith("@"):
        id_or_username = id_or_username.strip().strip("@")
        err = check_username(id_or_username)
        if err:
            return err

    res, err = await db.user_delete(id_or_username)
    if err:
        return err
    return {
        "result": res,
        "timestamptz": datetime.now()
    }