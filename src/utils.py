from .config import NAMES_MAX_LEN, USERNAME_MAX_LEN, LANGUAGE_CODE_MAX_LEN

def http_error(
    code: int,
    message: str,
    field: str | None,
    reason: str
) -> dict[str, str | int]:
    """
    :return: {"error": {"code": *code*, "message": *message*, "details": [{"field": *field*, "reason": *reason*}]}}
    """
    return {
        "error": {
            "code": code,
            "message": message,
            "details": [
                {
                    "field": field,
                    "reason": reason
                }
            ]
        }
    }

def check_names(
    first_name: str,
    last_name: str | None = None,
    username: str | None = None
) -> dict[str, str | int] | None:
    """Checks the validity of the first name, last name and username fields."""
    data: dict[str, str] = locals().copy(); data.pop("username")

    if not first_name:
        return http_error(400, "The first name field is empty", "first_name", "missing_required_field")
    if len(first_name) > NAMES_MAX_LEN:
        return http_error(400, f"The first name field can be a maximum of {NAMES_MAX_LEN} letters in length", "fist_name", "first_name_too_long")

    if last_name is not None:
        if not last_name:
            return http_error(400, "The last name field is empty", "last_name", "missing_field")
        if len(last_name) > NAMES_MAX_LEN:
            return http_error(400, f"The last name field can be a maximum of {NAMES_MAX_LEN} letters in length", "last_name", "last_name_too_long")

    if username is not None:
        if not username:
            return http_error(400, "The username field is empty", "username", "missing_field")
        if len(username) > USERNAME_MAX_LEN:
            return http_error(400, f"The username field can be a maximum of {USERNAME_MAX_LEN} letters in length", "username", "username_too_long")

    return None

def check_username(
    username: str
) -> dict[str, str | int] | None:
    """Checks the validity of the username field."""
    if not username:
        return http_error(400, "The username field is empty", "username", "missing_field")
    if len(username) > USERNAME_MAX_LEN:
        return http_error(400, f"The username field can be a maximum of {USERNAME_MAX_LEN} letters in length", "username", "username_too_long")

def check_language_code(
    language_code: str
) -> dict[str, str | int] | None:
    """Checks the validity of the language code field."""
    if not language_code:
        return http_error(400, "The language code field is empty", "language_code", "missing_required_field")
    if len(language_code) > LANGUAGE_CODE_MAX_LEN:
        return http_error(400, f"The language code field can be a maximum of {LANGUAGE_CODE_MAX_LEN} letters in length", "language_code", "language_code_too_long")
    return None