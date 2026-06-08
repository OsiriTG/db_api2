from fastapi import APIRouter, HTTPException, Header

from pydantic import BaseModel, Field
from typing import Dict, Optional, Any

from ..config import API_KEY_LEN, PERMISSIONS_MAX_LEN
from ..methods import (
    activate_api_key, deactivate_api_key,
    get_api_key,
    change_api_key_permissions, change_api_key_owner
)
from ..custom_types import ApiKey

router = APIRouter(prefix="api_keys")


class Activate(BaseModel):
    permissions: str = Field(..., max_length=PERMISSIONS_MAX_LEN)
    is_superkey: bool = False

class ChangePermissions(BaseModel):
    api_key: str = Field(..., min_length=API_KEY_LEN, max_length=API_KEY_LEN)
    new_permissions: str = Field(..., max_length=PERMISSIONS_MAX_LEN)

class ChangeOwner(BaseModel):
    api_key: str = Field(..., min_length=API_KEY_LEN, max_length=API_KEY_LEN)
    new_owner_id: Optional[int] = Field(None, max_length=PERMISSIONS_MAX_LEN)


@router.post("/api_keys/activate")
async def api_keys_activate(
    request: Activate,
    api_key: str = Header(..., alias="your_api_key", min_length=API_KEY_LEN, max_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    your_api_key = ApiKey(**your_api_key)

    if not your_api_key.is_superkey:
        raise HTTPException(403, "Not enough rights (is_superkey)")
    missing_permissions: list[str] = [p.lower() for p in request.permissions if p not in your_api_key.permissions]
    if missing_permissions:
        return HTTPException(403, f"Not enough rights ({', '.join(missing_permissions)})")

    new_api_key = await activate_api_key(**dict(vars(request)))
    if "error" in new_api_key:
        raise HTTPException(new_api_key['error']['code'], new_api_key)
    return new_api_key

@router.post("/api_keys/deactivate")
async def api_keys_deactivate(
    target_api_key: str = Header(..., alias="target_api_key", min_length=API_KEY_LEN, max_length=API_KEY_LEN),
    api_key: str = Header(..., alias="your_api_key", min_length=API_KEY_LEN, max_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    your_api_key = ApiKey(**your_api_key)

    if not your_api_key.is_superkey:
        raise HTTPException(403, "Not enough rights (is_superkey)")
    if not "d" in your_api_key.permissions:
        return HTTPException(403, f"Not enough rights (d)")

    res = await deactivate_api_key(target_api_key)
    if "error" in res:
        raise HTTPException(res['error']['code'], res)
    return res

@router.get("/api_keys/get")
async def api_keys_get(
    target_api_key: str = Header(..., alias="target_api_key", min_length=API_KEY_LEN, max_length=API_KEY_LEN),
    api_key: str = Header(..., alias="your_api_key", min_length=API_KEY_LEN, max_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    your_api_key = ApiKey(**your_api_key)

    if not your_api_key.is_superkey:
        raise HTTPException(403, "Not enough rights (is_superkey)")
    if not "r" in your_api_key.permissions:
        return HTTPException(403, f"Not enough rights (r)")

    t_api_key = await get_api_key(target_api_key)
    if "error" in t_api_key:
        raise HTTPException(t_api_key['error']['code'], t_api_key)
    return t_api_key

@router.post("/api_keys/change/permissions")
async def api_keys_change_permissions(
    request = ChangePermissions,    
    api_key: str = Header(..., alias="your_api_key", min_length=API_KEY_LEN, max_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    your_api_key = ApiKey(**your_api_key)

    if not your_api_key.is_superkey:
        raise HTTPException(403, "Not enough rights (is_superkey)")
    if not "u" in your_api_key.permissions:
        return HTTPException(403, f"Not enough rights (u)")

    res = await change_api_key_permissions(**dict(vars(request)))
    if "error" in res:
        raise HTTPException(res['error']['code'], res)
    return res

@router.post("/api_keys/change/owner")
async def api_keys_change_owner(
    request = ChangeOwner,    
    api_key: str = Header(..., alias="your_api_key", min_length=API_KEY_LEN, max_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    your_api_key = ApiKey(**your_api_key)

    if not your_api_key.is_superkey:
        raise HTTPException(403, "Not enough rights (is_superkey)")
    if not "u" in your_api_key.permissions:
        return HTTPException(403, f"Not enough rights (u)")

    res = await change_api_key_owner(**dict(vars(request)))
    if "error" in res:
        raise HTTPException(res['error']['code'], res)
    return res