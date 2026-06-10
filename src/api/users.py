from fastapi import APIRouter, HTTPException, Header

from pydantic import BaseModel, Field
from typing import Dict, Optional, Any

from ..config import NAMES_MAX_LEN, USERNAME_MAX_LEN, LANGUAGE_CODE_MAX_LEN, API_KEY_LEN
from ..methods import (
    get_api_key,
    record_user, unrecord_user,
    get_user,
    change_language_code, change_zoneinfo,
)

router = APIRouter(prefix="/users")


class ChangeLanguageCode(BaseModel):
    id_or_username: int | str
    new_language_code: str

class ChangeZoneinfo(BaseModel):
    id_or_username: int | str
    new_zoneinfo: str


class Record(BaseModel):
    id: int
    first_name: str = Field(..., max_length=NAMES_MAX_LEN)
    last_name: Optional[str] = Field(None, max_length=NAMES_MAX_LEN)
    username: Optional[str] = Field(None, max_length=USERNAME_MAX_LEN)
    language_code: Optional[str] = Field(None, max_length=LANGUAGE_CODE_MAX_LEN)
    is_premium: Optional[bool] = None
    added_to_attachment_menu: Optional[bool] = None
    can_join_groups: Optional[bool] = None
    can_read_all_group_messages: Optional[bool] = None
    supports_guest_queries: Optional[bool] = None
    supports_inline_queries: Optional[bool] = None
    can_connect_to_business: Optional[bool] = None
    has_main_web_app: Optional[bool] = None
    has_topics_enabled: Optional[bool] = None
    allows_users_to_create_topics: Optional[bool] = None
    can_manage_bots: Optional[bool] = None
    zoneinfo: Optional[str] = None


@router.post("/record")
async def users_record(
    request: Record,
    api_key: str = Header(..., alias="your_api_key", max_length=API_KEY_LEN, min_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    Records user's data
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    if not "c" in your_api_key['permissions']:
        return HTTPException(403, "Not enough rights (c)")

    new_user = await record_user(**dict(vars(request)))
    if "error" in new_user:
        raise HTTPException(new_user['error']['code'], new_user)
    return new_user

@router.delete("/unrecord")
async def users_unrecord(
    id_or_username: int | str = Header(..., alias="user_id_or_username"),
    api_key: str = Header(..., alias="your_api_key", max_length=API_KEY_LEN, min_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    Unrecord user's data
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    if not "d" in your_api_key['permissions']:
        return HTTPException(403, "Not enough rights (d)")

    res = await unrecord_user(id_or_username)
    if "error" in res:
        raise HTTPException(res['error']['code'], res)
    return res

@router.post("/get")
async def users_get(
    id_or_username: int | str = Header(..., alias="user_id_or_username"),
    api_key: str = Header(..., alias="your_api_key", max_length=API_KEY_LEN, min_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    Reads for the given users.
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    if not "r" in your_api_key['permissions']:
        return HTTPException(403, "Not enough rights (r)")

    user = await get_user(id_or_username)
    if "error" in user:
        raise HTTPException(user['error']['code'], user)
    return user

@router.post("/change/language-code")
async def users_change_language_code(
    request: ChangeLanguageCode,
    api_key: str = Header(..., alias="your_api_key", max_length=API_KEY_LEN, min_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    Changes language code for given user.
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    if not "u" in your_api_key['permissions']:
        return HTTPException(403, "Not enough rights (u)")

    res = await change_language_code(**dict(vars(request)))
    if "error" in res:
        raise HTTPException(res['error']['code'], res)
    return res

@router.post("/change/zoneinfo")
async def users_change_zoneinfo(
    request: ChangeZoneinfo,
    api_key: str = Header(..., alias="your_api_key", max_length=API_KEY_LEN, min_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    Changes zoneinfo for given user.
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    if not "u" in your_api_key['permissions']:
        return HTTPException(403, "Not enough rights (u)")

    res = await change_zoneinfo(**dict(vars(request)))
    if "error" in res:
        raise HTTPException(res['error']['code'], res)
    return res