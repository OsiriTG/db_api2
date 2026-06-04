from .api_keys import (
    activate_api_key, deactivate_api_key,
    change_api_key_permissions, change_api_key_owner,
    superkey, unsuperkey
)
from .users import (
    record_user, unrecord_user,
    get_user,
    update_language_code, update_timezone
)


def check_names(
    first_name: str,
    last_name: str | None = None,
    username: str | None = None
) -> str | None:
    """Checks the validity of the first name, last name and username fields."""
    from ..config import NAMES_MAX_LEN, USERNAME_MAX_LEN
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
    from ..config import LANGUAGE_CODE_MAX_LEN
    if not language_code:
        return f"Method error. The language code field is empty"
    if len(language_code) > LANGUAGE_CODE_MAX_LEN:
        return f"Method error. The language code field should be maximum {LANGUAGE_CODE_MAX_LEN} letters lengh"
    return None


__all__ = [
    "check_names", "check_language_code",
    "activate_api_key", "deactivate_api_key",
    "change_api_key_permissions", "change_api_key_owner",
    "superkey", "unsuperkey",
    "record_user", "unrecord_user",
    "get_user",
    "update_language_code", "update_timezone"
]