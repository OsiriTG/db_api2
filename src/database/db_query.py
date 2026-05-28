from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row
from psycopg.errors import UndefinedColumn

from aiogram.types import User, Chat

from ..config import DB_HOST, DB_DBNAME, DB_PORT, DB_USER, DB_PASSWORD

class DbQuery:
    def __init__(
            self,
            name: str | None = None
        ) -> None:
        self.conn = None
        self.name = name or "db_query.py"

    @property
    def tsr(
        self
    ) -> str:
        from datetime import datetime
        return datetime.strftime(datetime.now().timestamp(), "%Rs")

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