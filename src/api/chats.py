from fastapi import APIRouter, HTTPException, Header

from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, Literal

from ..config import (
    TITLE_MAX_LEN,
    USERNAME_MAX_LEN, NAMES_MAX_LEN, LANGUAGE_CODE_MAX_LEN,
    API_KEY_LEN
)
from ..methods import (
    get_api_key,
    record_chat, unrecord_chat,
    get_chat,
    change_chat_language_code, change_chat_zoneinfo
)

router = APIRouter(prefix="/chats")


class Record(BaseModel):
    id: int
    type: Literal["private", "group", "supergroup", "channel"]
    title: Optional[str] = Field(None, max_length=TITLE_MAX_LEN)
    username: Optional[str] = Field(None, max_length=USERNAME_MAX_LEN)
    first_name: Optional[str] = Field(None, max_length=NAMES_MAX_LEN)
    last_name: Optional[str] = Field(None, max_length=NAMES_MAX_LEN)
    is_forum: Optional[bool] = None
    is_direct_messages: Optional[bool] = None
    language_code: Optional[str] = Field(None, max_length=LANGUAGE_CODE_MAX_LEN)
    owner_id: Optional[int] = None
    zoneinfo: Optional[str] = None

class ChangeLanguageCode(BaseModel):
    id_or_username: int | str
    new_language_code: str

class ChangeZoneinfo(BaseModel):
    id_or_username: int | str
    new_zoneinfo: str


@router.post("/record")
async def chats_record(
    request: Record,
    api_key: str = Header(..., alias="your_api_key", max_length=API_KEY_LEN, min_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    Records chat's data
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    if not "c" in your_api_key['permissions']:
        return HTTPException(403, "Not enough rights (c)")

    new_chat = await record_chat(**dict(vars(request)))
    if "error" in new_chat:
        raise HTTPException(new_chat['error']['code'], new_chat)
    return new_chat

@router.delete("/unrecord")
async def chats_unrecord(
    id_or_username: int | str = Header(..., alias="chat_id_or_username"),
    api_key: str = Header(..., alias="your_api_key", max_length=API_KEY_LEN, min_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    Unrecord chat's data
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    if not "d" in your_api_key['permissions']:
        return HTTPException(403, "Not enough rights (d)")

    res = await unrecord_chat(id_or_username)
    if "error" in res:
        raise HTTPException(res['error']['code'], res)
    return res

@router.post("/get")
async def chats_get(
    id_or_username: int | str = Header(..., alias="chat_id_or_username"),
    api_key: str = Header(..., alias="your_api_key", max_length=API_KEY_LEN, min_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    Reads for the given chat.
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    if not "r" in your_api_key['permissions']:
        return HTTPException(403, "Not enough rights (r)")

    chat = await get_chat(id_or_username)
    if "error" in chat:
        raise HTTPException(chat['error']['code'], chat)
    return chat

@router.post("/change/language-code")
async def chats_change_language_code(
    request: ChangeLanguageCode,
    api_key: str = Header(..., alias="your_api_key", max_length=API_KEY_LEN, min_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    Changes language code for given chat.
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    if not "u" in your_api_key['permissions']:
        return HTTPException(403, "Not enough rights (u)")

    res = await change_chat_language_code(**dict(vars(request)))
    if "error" in res:
        raise HTTPException(res['error']['code'], res)
    return res

@router.post("/change/zoneinfo")
async def chats_change_zoneinfo(
    request: ChangeZoneinfo,
    api_key: str = Header(..., alias="your_api_key", max_length=API_KEY_LEN, min_length=API_KEY_LEN)
) -> Dict[str, Any]:
    """
    Changes zoneinfo for given chat.
    """
    your_api_key = await get_api_key(api_key)
    if "error" in your_api_key:
        raise HTTPException(your_api_key['error']['code'], your_api_key)
    if not "u" in your_api_key['permissions']:
        return HTTPException(403, "Not enough rights (u)")

    res = await change_chat_zoneinfo(**dict(vars(request)))
    if "error" in res:
        raise HTTPException(res['error']['code'], res)
    return res