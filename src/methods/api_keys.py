from typing import Any

from datetime import datetime

from ..config import API_KEY_LEN, PERMISSIONS_MAX_LEN
from ..database import db
from ..utils import http_error


def check_api_key(
    api_key: str
) -> dict[str, str | int] | None:
    """Checks the validity of the API key field."""
    if not api_key:
        return http_error(400, "The API key field is empty", "api_key", "missing_required_field")
    if len(api_key) != API_KEY_LEN:
        return http_error(400, f"The API key field can be only {API_KEY_LEN} letters in length", "api_key", "api_key_uncorrect_len")
    return None

def check_permissions(
    permissions: str
) -> dict[str, str | int] | None:
    """Checks the validity of the pemissions field for API keys."""
    if not permissions:
        return http_error(400, "The permissions field is empty", "permissions", "missing_field")
    if len(permissions) > PERMISSIONS_MAX_LEN:
        return http_error(400, f"The permissions field can be a maximum of {PERMISSIONS_MAX_LEN} letters in length", "permissions", "permissions_too_long")
    if not set(permissions).issubset(set('crud')):
        return http_error(400, f"The permissions field can only contain the letters c, r, u and d", "permissions", "permissions_uncorrect_chars")
    return None


async def activate_api_key(
    permissions: str = 'r',
    is_superkey: bool = False,
    owner_id: int | None = None
) -> dict[str, Any]:
    """
    Registers the API key.

    :param permissions: Permissions of the API key in format (example): 'cud', 'rd', 'cd', etc. Full rights would be 'crud'.
    :param is_superkey: Superkey can CRUD (based on superkey's *permissions*) other API keys.
    :param owner_id: *Optional* Telegram ID of the API key's owner.
    :return: On success will return dict of :class:`..types.api_key.ApiKey` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    permissions = permissions.strip()
    err = check_permissions(permissions)
    if err:
        return err

    #if is_superkey is None:
    #    is_superkey = False

    if owner_id:
        _, err = await db.user_read(owner_id)
        if err:
            return err

    new_api_key, err = await db.api_key_create(
        permissions=permissions,
        is_superkey=is_superkey,
        owner_id=owner_id
    )
    if err:
        return err
    return dict(vars(new_api_key))

async def get_api_key(
   api_key: str
) -> dict[str, Any]:
    """
    Returns the API key's data.

    :param api_key: The API key whose data needs to be obtained.
    :return: On success will return dict of :class:`..types.api_key.ApiKey` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    api_key = api_key.strip()
    err = check_api_key(api_key)
    if err:
        return err

    api_key, err = await db.api_key_read(api_key)
    if err:
        return err
    return dict(vars(api_key))

async def change_api_key_permissions(
    api_key: str,
    new_permissions: str = 'r'
) -> dict[str, Any]:
    """
    Updates the API key's permissions.

    :param api_key: The API key whose data needs to be obtained.
    :param new_permissions: New value of permissions.
    :return: On success will return :code:`True` or if rowcount is stil 0 - :code:`False` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    api_key = api_key.strip()
    err = check_api_key(api_key)
    if err:
        return err

    new_permissions = new_permissions.strip()
    err = check_permissions(new_permissions)
    if err:
        return err

    res, err = await db.api_key_update_permissions(
        api_key=api_key,
        new_permissions=new_permissions
    )
    if err:
        return err
    return {
        "result": res,
        "timestamptz": datetime.now()
    }

async def change_api_key_owner(
    api_key: str,
    new_owner_id: int | None = None
) -> dict[str, Any]:
    """
    Updates the API key's owner (telegram user ID).

    :param api_key: The API key whose data needs to be obtained.
    :param new_owner_id: New value of owner id.
    :return: On success will return :code:`True` or if rowcount is stil 0 - :code:`False` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    api_key = api_key.strip()
    err = check_api_key(api_key)
    if err:
        return err

    if new_owner_id:
        _, err = await db.user_read(new_owner_id)
        if err:
            return err

    res, err = await db.api_key_update_owner_id(
        api_key,
        new_owner_id
    )
    if err:
        return err
    return {
        "result": res,
        "timestamptz": datetime.now()
    }

async def superkey(
    api_key: str
) -> dict[str, Any]:
    """
    Turns the API key into a superkey.

    :param api_key: The API key that should become the superkey.
    :return: On success will return :code:`True` or if rowcount is stil 0 - :code:`False` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    api_key = api_key.strip()
    err = check_api_key(api_key)
    if err:
        return err

    res, err = await db.api_key_update_is_superkey(
        api_key,
        True
    )
    if err:
        return err
    return {
        "result": res,
        "timestamptz": datetime.now()
    }

async def unsuperkey(
    api_key: str
) -> dict[str, Any]:
    """
    Takes away the superkey rights from the API key.

    :param api_key: The API key that should stop being a superkey.
    :return: On success will return :code:`True` or if rowcount is stil 0 - :code:`False` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    api_key = api_key.strip()
    err = check_api_key(api_key)
    if err:
        return err

    res, err = await db.api_key_update_is_superkey(api_key)
    if err:
        return err
    return {
        "result": res,
        "timestamptz": datetime.now()
    }

async def deactivate_api_key(
    api_key: str
) -> dict[str, Any]:
    """
    Deactivates the API Key.

    :param api_key: The API key whose data needs to be deleted.
    :return: On success will return :code:`True` or if rowcount is stil 0 - :code:`False` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
    """
    api_key = api_key.strip()
    err = check_api_key(api_key)
    if err:
        return err

    res, err = await db.api_key_delete(api_key)
    if err:
        return err
    return {
        "result": res,
        "timestamptz": datetime.now()
    }