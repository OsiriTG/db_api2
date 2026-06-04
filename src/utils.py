def http_error(
    code: int,
    message: str,
    field: str | None,
    reason: str
) -> dict[str, str | int]:
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