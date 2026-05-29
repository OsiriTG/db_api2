from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row
from psycopg.errors import UndefinedColumn

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
    #   Table "api_keys"    #
    #########################

    async def api_key_create(
        self,
        api_key: str | None = None,
        permissions: str = 'r',
        is_superkey: bool = False,
        owner_id: int | None = None
    ) -> tuple[ApiKey | None, str | None]:
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
                        if not await cur.fetchone():
                            break

                await cur.execute(
                    """
                    INSERT INTO api_keys (api_key, permissions, is_superkey, owner_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING *
                    """,
                    (api_key, permissions, is_superkey, owner_id)
                )
                new_api_key: dict = await cur.fetchone()
                if new_api_key is None:
                    e = f"Database `{self.name}` unexpected error. API key wasn't created. Report this message"
                    print(f"[{self.tsr}] database {self.name}: api_key_create(): Unexpected error: {e}")
                    await self.conn.rollback()
                    return None, e
                await self.conn.commit()
                return ApiKey(**new_api_key), None
        except Exception as e:
            print(f"[{self.tsr}] database {self.name}: api_key_create(): Unexpected error: {e}")
            await self.conn.rollback()
            return None, str(e)

    async def api_key_read(
        self,
        api_key: str
    ) -> tuple[ApiKey | None, str | None]:
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
                    e = f"Database '{self.name}' error. Given API key isn't exist"
                    print(f"[{self.tsr}] database {self.name}: api_key_read(): Error: {e}")
                    return None, e
                return ApiKey(**api_key), None
        except Exception as e:
            print(f"[{self.tsr}] database {self.name}: api_key_read(): Unexpected error: {e}")
            return None, str(e)

    #
    # For security reasons there's no function with fetchall() return.
    # Also (for the same reasons) there's no update function with **kwargs; only separate funcs.
    #

    async def api_key_update(
        self,
        api_key: str,
        allow_None_values: bool = False,
        **columns_to_update
    ) -> tuple[ApiKey | None, str | None]:
        try:
            columns = []
            params = []

            for column, value in columns_to_update.items():
                if not allow_None_values and value is None:
                    continue
                columns.append(sql.SQL("{} = %s").format(sql.Identifier(column)))
                params.append(value)
            
            query = sql.SQL(
                """
                UPDATE api_keys
                SET {}
                WHERE api_key = %s
                RETURNING *
                """
            ).format(sql.SQL(", ").join(columns))
            params.append(api_key)

            async with self.conn.cursor() as cur:
                await cur.execute(query, params)
                updated_api_key = await cur.fetchone()
                if updated_api_key is None:
                    e = f"Database '{self.name}' unexpected error. API key wasn't updated. Report this message"
                    print(f"[{self.tsr}] database {self.name}: api_key_update(): Unexpected error: {e}")
                    await self.conn.rollback()
                    return None, e
                await self.conn.commit()
                return ApiKey(**updated_api_key), None
        except UndefinedColumn as e:
            print(f"[{self.tsr}] database {self.name}: api_key_update(): UndefinedColumn error: {e}")
            await self.conn.rollback()
            return None, str(e)
        except Exception as e:
            print(f"[{self.tsr}] database {self.name}: api_key_update(): Unexpected error: {e}")
            await self.conn.rollback()
            return None, str(e)

    async def api_key_delete(
        self,
        api_key: str
    ) -> tuple[bool | None, str | None]:
        try:
            async with self.conn.cursor() as cur:
                await cur.execute(
                    """
                    DELETE FROM api_keys WHERE api_key = %s
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