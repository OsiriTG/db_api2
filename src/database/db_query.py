from psycopg import AsyncConnection#, sql
from psycopg.rows import dict_row
#from psycopg.errors import UndefinedColumn

from aiogram.types import User, Chat

from string import ascii_letters, digits
from secrets import choice

from ..config import DB_HOST, DB_DBNAME, DB_PORT, DB_USER, DB_PASSWORD, API_KEY_LEN
from ..types import ApiKey

base64 = ascii_letters + digits + "_" + "-"

class DbQuery:
    def __init__(
            self,
            name: str | None = None
        ) -> None:
        self.conn = None
        self.name = name or "db_query"

    @property
    def tsr(
        self
    ) -> str:
        from datetime import datetime
        return datetime.strftime(datetime.now().timestamp(), "%R")

    async def connect(
        self
    ) -> None:
        self.conn = await AsyncConnection.connect(
            host        = DB_HOST,
            dbname      = DB_DBNAME,
            port        = DB_PORT,
            user        = DB_USER,
            password    = DB_PASSWORD,
            row_factory = dict_row
        )

    #########################
    #                       #
    #   Table "api_keys"    #
    #                       #
    #########################

    async def api_key_create(
        self,
        api_key: str | None = None,
        permissions: str = 'r',
        is_superkey: bool = False,
        owner_id: int | None = None
    ) -> tuple[ApiKey | None, str | None]:
        """
        Creates API key in the database.

        :param api_key: The API key. Case-sensitive. If :code:`None` is given, then it will be randomly generated based on :data:`base64`.
        :param permissions: Permissions of the API key in format (example): 'cud', 'rd', 'cd', etc. Full rights would be 'crud'.
        :param is_superkey: Superkey can CRUD (based on superkey's *permissions*) other API keys.
        :param owner_id: Telegram ID of the API key's owner. Optional in DB.
        :return: On success will return :class:`src.types.api_key.ApiKey` & :code:`None` as error. Otherwise, :code:`None` & text of error: :code:`str`.
        """
        try:
            async with self.conn.cursor() as cur:
                if api_key is None:
                    while True:
                        api_key: str = ''.join(choice(base64) for _ in range(API_KEY_LEN))
                        await cur.execute(
                            """
                            SELECT 1 FROM api_keys WHERE api_key = %s
                            """,
                            (api_key,)
                        )
                        if await cur.fetchone() is None:
                            break

                if owner_id is not None:
                    await cur.execute(
                        """
                        SELECT 1 FROM users WHERE id = %s
                        """,
                        (owner_id,)
                    )
                    if await cur.fetchone() is None:
                        e: str = f"Database '{self.name}' error. User with the specified owner_id doesn't exist"
                        print(f"[{self.tsr}] database {self.name}: api_key_create(): Error: {e}")
                        await self.conn.rollback()
                        return None, e

                await cur.execute(
                    """
                    INSERT INTO api_keys (api_key, permissions, is_superkey, owner_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING *
                    """,
                    (api_key, permissions.lower(), is_superkey, owner_id)
                )
                new_api_key: dict = await cur.fetchone()
                if new_api_key is None:
                    e: str = f"Database `{self.name}` unexpected error. API key wasn't created. Report this message"
                    print(f"[{self.tsr}] database {self.name}: api_key_create(): Unexpected error: {e}")
                    await self.conn.rollback()
                    return None, e
                await self.conn.commit()
                return ApiKey(**new_api_key), None
        except Exception as e:
            print(f"[{self.tsr}] database {self.name}: api_key_create(): Unexpected error: {e}")
            await self.conn.rollback()
            return None, str(e)

    #
    # For security reasons there's no function with fetchall() return.
    # Also (for the same reasons) there are no read and update functions with **kwargs;
    # for updating there are only separate funcs for each column (except for `api_key` and `date_db`).
    #

    async def api_key_read(
        self,
        api_key: str
    ) -> tuple[ApiKey | None, str | None]:
        """
        Reads the given API key in the database.

        :param api_key: The API key whose data needs to be obtained.
        :return: On success will return :class:`src.types.api_key.ApiKey` & :code:`None` as error. Otherwise, :code:`None` & text of error: :code:`str`.
        """
        try:
            async with self.conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT * FROM api_keys WHERE api_key = %s
                    """,
                    (api_key,)
                )
                api_key: dict = await cur.fetchone()
                if api_key is None:
                    e: str = f"Database '{self.name}' error. Specified API key doesn't exist"
                    print(f"[{self.tsr}] database {self.name}: api_key_read(): Error: {e}")
                    return None, e
                return ApiKey(**api_key), None
        except Exception as e:
            print(f"[{self.tsr}] database {self.name}: api_key_read(): Unexpected error: {e}")
            return None, str(e)

    async def api_key_update_permissions(
        self,
        api_key: str,
        new_permissions: str = 'r'
    ) -> tuple[bool | None, str | None]:
        """
        Updates the :code:`permissions` column for the given API key in the database.

        :param api_key: The API key whose data needs to be updated.
        :param new_permissions: New permissions for the API key in format (example): 'cud', 'rd', 'cd', etc. Full rights would be 'crud'.
        :return: On success will return :code:`True` if column have been changed, otherwise :code:`False` & :code:`None` as error. Otherwise, :code:`None` & text of error: :code:`str`.
        """
        try:
            async with self.conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE api_keys
                    SET permissions = %s
                    WHERE api_key = %s AND permissions != %s
                    """,
                    (new_permissions.lower(), api_key, new_permissions.lower())
                )

                if cur.rowcount == 0:
                    return False, None

                await self.conn.commit()
                return True, None
        except Exception as e:
            print(f"[{self.tsr}] database {self.name}: api_key_update_permissions(): Unexpected error: {e}")
            await self.conn.rollback()
            return None, str(e)

    async def api_key_update_is_superkey(
        self,
        api_key: str,
        new_is_superkey: bool = False
    ) -> tuple[bool | None, str | None]:
        """
        Updates the :code:`is_superkey` column for the given API key in the database.

        :param api_key: The API key whose data needs to be updated.
        :param new_is_superkey: Note: Superkey can CRUD (based on superkey's *permissions*) other API keys.
        :return: On success will return :code:`True` if column have been changed, otherwise :code:`False` & :code:`None` as error. Otherwise, :code:`None` & text of error: :code:`str`.
        """
        try:
            async with self.conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE api_keys
                    SET is_superkey = %s
                    WHERE api_key = %s AND is_superkey != %s
                    """,
                    (new_is_superkey, api_key, new_is_superkey)
                )

                if cur.rowcount == 0:
                    return False, None

                await self.conn.commit()
                return True, None
        except Exception as e:
            print(f"[{self.tsr}] database {self.name}: api_key_update_is_superkey(): Unexpected error: {e}")
            await self.conn.rollback()
            return None, str(e)

    async def api_key_update_owner_id(
        self,
        api_key: str,
        new_owner_id: int | None = None
    ) -> tuple[bool | None, str | None]:
        """
        Updates the :code:`owner_id` column for the given API key in the database.

        :param api_key: The API key whose data needs to be updated.
        :param new_owner_id: Note: Telegram ID of the API key's owner. Optional in DB.
        :return: On success will return :code:`True` if column have been changed, otherwise :code:`False` & :code:`None` as error. Otherwise, :code:`None` & text of error: :code:`str`.
        """
        try:
            async with self.conn.cursor() as cur:
                if new_owner_id is not None:
                    await cur.execute(
                        """
                        SELECT 1 FROM users WHERE id = %s
                        """,
                        (new_owner_id,)
                    )
                    if await cur.fetchone() is None:
                        e: str = f"Database '{self.name}' error. User with the specified new_owner_id doesn't exist"
                        print(f"[{self.tsr}] database {self.name}: api_key_update_owner_id(): Error: {e}")
                        await self.conn.rollback()
                        return None, e

                await cur.execute(
                    """
                    UPDATE api_keys
                    SET owner_id = %s
                    WHERE api_key = %s AND owner_id IS DISTINCT FROM %s
                    """,
                    (new_owner_id, api_key, new_owner_id)
                )

                if cur.rowcount == 0:
                    return False, None

                await self.conn.commit()
                return True, None
        except Exception as e:
            print(f"[{self.tsr}] database {self.name}: api_key_update_owner_id(): Unexpected error: {e}")
            await self.conn.rollback()
            return None, str(e)

    async def api_key_delete(
        self,
        api_key: str
    ) -> tuple[bool | None, str | None]:
        """
        Deletes the given API key from the database.

        :param api_key: The API key that needs to be deleted.
        :return: On success will return :code:`True` if column have been changed, otherwise :code:`False` & :code:`None` as error. Otherwise, :code:`None` & text of error: :code:`str`.
        """
        try:
            async with self.conn.cursor() as cur:
                await cur.execute(
                    """
                    DELETE FROM api_keys
                    WHERE api_key = %s
                    """,
                    (api_key,)
                )

                if cur.rowcount == 0:
                    return False, None    

                await self.conn.commit()
                return True, None
        except Exception as e:
            print(f"[{self.tsr}] database {self.name}: api_key_delete(): Unexpected error: {e}")
            await self.conn.rollback()
            return None, str(e)

    #####################
    #   Table "users"   #
    #####################

    async def user_create(
        self,
        id: int,
        first_name: str,
        last_name: str | None = None,
        username: str | None = None,
        language_code: str | None = None,
        is_premium: bool | None = None
    ) -> tuple[User | None, str | None]:
        try:
            async with self.conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT 1 FROM users WHERE username = %s
                    """,
                    (username,)
                )
                if cur.fetchone():
                    await cur.execute(
                        """
                        UPDATE users SET username = NULL WHERE username = %s AND id != %s
                        """,
                        (username, id)
                    )

                await cur.execute(
                    """
                    INSERT INTO users (id, first_name, last_name, username, language_code, is_premium)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        username = EXCLUDED.username,
                        language_code = EXCLUDED.language_code,
                        is_premium = EXCLUDED.is_premium,
                        zoneinfo = COALESCE(EXCLUDED.zoneinfo, users.zoneinfo)
                    RETURNING *
                    """,
                    (id, first_name, last_name, username, language_code, is_premium)
                )
                new_user: dict = await cur.fetchone()
                if new_user is None:
                    e: str = "Unexpecter error. User wasn't created. Report this message"
                    print(f"[{self.tsr}] database {self.name}: user_create(): Error: {e}")
                    await self.conn.rollback()
                    return None, e
                await self.conn.commit()
                return User(**new_user), None
        except Exception as e:
            print(f"[{self.tsr}] database {self.name}: user_create(): Error: {e}")
            await self.conn.rollback()
            return None, str(e)