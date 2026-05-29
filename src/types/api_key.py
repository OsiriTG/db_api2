class ApiKey:
    def __init__(
        self,
        api_key: str,
        permissions: str = 'r',
        is_superkey: bool = False,
        owner_id: int | None = None
    ) -> None:
        self.api_key=api_key
        self.permissions=permissions
        self.is_superkey=is_superkey
        self.owner_id=owner_id

    def __str__(
        self
    ) -> str:
        return str(vars(self))