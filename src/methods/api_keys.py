from typing import Any, Literal

from ..config import API_KEY_LEN, PERMISSIONS_MAX_LEN
from ..database import db


def check_api_key(
    api_key: str
) -> str | None:
    if not api_key:
        return "Method error. The API key field is empty"
    if len(api_key) != API_KEY_LEN:
        return f"Method error. API key is need to be {API_KEY_LEN} letters length"
    return None

def check_permissions(
    permissions: str
) -> str | None:
    if not permissions:
        return "Method error. The permissions field is empty"
    if len(permissions) > PERMISSIONS_MAX_LEN:
        return "Method error. The permissions field should be maximum 4 letter length"
    if not set(permissions).issubset(set('crud')):
        return "Method error. The permissions field should only contain the letters c, r, u and d"
    return None


async def activate_api_key(
    permissions: str = 'r',
    is_superkey: bool = False,
    owner_id: int | None = None
) -> dict[str, Any]:
    """
    Register an API key in the system.

    :param permissions: Permissions of the API key in format (example): 'cud', 'rd', 'cd', etc. Full rights would be 'crud'.
    :param is_superkey: Superkey can CRUD (based on superkey's *permissions*) other API keys.
    :param owner_id: *Optional* Telegram ID of the API key's owner.
    :return: On success returns dict with new API key data. Otherwise, :code:`{"error": str}`
    """
    permissions = permissions.strip()
    err = check_permissions(permissions)
    if err:
        return {"error": err}

    if is_superkey is None:
        is_superkey = False

    _, err = await db.user_read(owner_id)
    if err:
        return {"error": err}

    new_api_key, err = await db.api_key_create(
        permissions=permissions,
        is_superkey=is_superkey,
        owner_id=owner_id
    )
    if err:
        return {"error": err}
    return dict(vars(new_api_key))

#async def api_key_get(
#    self,
#    api_key: str
#) -> dict[str, Any]:
#
# I think the "read api key" func is a security breach.
# I won't be creating it for a public or even private API, so at this point i don't need this function.
#

async def change_api_key_permissions(
    api_key: str,
    new_permissions: str = 'r'
) -> dict[str, str | Literal[True]]:
    """
    
    """
    api_key = api_key.strip()
    err = check_api_key(api_key)
    if err:
        return {"error": err}

    new_permissions = new_permissions.strip()
    err = check_permissions(new_permissions)
    if err:
        return {"error": err}

    res, err = await db.api_key_update_permissions(
        api_key=api_key,
        new_permissions=new_permissions
    )
    if err:
        return {"error": err}
    if not res:
        return {"error": "Method error. Existing permissions and the new given permissions are exactly the same"}
    return {"result": res}

async def change_api_key_owner(
    api_key: str,
    new_owner_id: int | None = None
) -> dict[str, str | Literal[True]]:
    """
    
    """
    api_key = api_key.strip()
    err = check_api_key(api_key)
    if err:
        return {"error": err}

    _, err = await db.user_read(new_owner_id)
    if err:
        return {"error": err}

    res, err = await db.api_key_update_owner_id(
        api_key,
        new_owner_id
    )
    if err:
        return {"error": err}
    if not res:
        return {"error": "Method error. Existing owner and the new given owner are exactly the same"}
    return {"result": res}

async def superkey(
    api_key: str
) -> dict[str, str | Literal[True]]:
    """
    
    """
    res, err = await db.api_key_update_is_superkey(
        api_key,
        True
    )
    if err:
        return {"error": err}
    if not res:
        return {"error": "Method error. Existing superkey status and the new given one are exactly the same"}
    return {"result": res}

async def unsuperkey(
    api_key: str
) -> dict[str, str | Literal[True]]:
    """
    
    """
    res, err = await db.api_key_update_is_superkey(api_key)
    if err:
        return {"error": err}
    if not res:
        return {"error": "Method error. Existing superkey status and the new given one are exactly the same"}
    return {"result": res}

async def deactivate_api_key(
    api_key: str
) -> dict[str, str | Literal[True]]:
    res, err = await db.api_key_delete(api_key)
    if err:
        return {"error": err}
    if not res:
        return {"error": "Method error. Given API key already doesn't exist"}
    return {"result": res}