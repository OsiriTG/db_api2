from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row
from psycopg.errors import UndefinedColumn

from aiogram.types import User, Chat

from typing import Any
from secrets import choice

from ..config import DB_HOST, DB_DBNAME, DB_PORT, DB_USER, DB_PASSWORD, API_KEY_LEN, base64
from ..custom_types import ApiKey
from ..utils import http_error

class DbQuery:
    def __init__(
            self,
            name: str | None = None
        ) -> None:
        self.conn = None
        self.name = name or DB_DBNAME

    #@property
    #def tsr(
    #    self
    #) -> str:
    #    from datetime import datetime
    #    return datetime.strftime(datetime.now().timestamp(), "%R")

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
    ) -> tuple[ApiKey | None, dict[str, str | int] | None]:
        """
        Creates API key in the database.

        :param api_key: The API key. Case-sensitive. If :code:`None` is given, then it will be randomly generated based on :data:`..config.base64`.
        :param permissions: Permissions of the API key in format (example): 'cud', 'rd', 'cd', etc. Full rights would be 'crud'.
        :param is_superkey: Superkey can CRUD (based on superkey's *permissions*) other API keys.
        :param owner_id: Telegram ID of the API key's owner. Optional in DB.
        :return: On success will return :class:`..types.api_key.ApiKey` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
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
                        await self.conn.rollback()
                        return None, http_error(404, "Specified user doesn't exist", "owner_id", "user_not_found")

                await cur.execute(
                    """
                    INSERT INTO api_keys (api_key, permissions, is_superkey, owner_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING *
                    """,
                    (api_key, permissions.lower(), is_superkey, owner_id)
                )
                new_api_key: dict[str, Any] = await cur.fetchone()
                if new_api_key is None:
                    await self.conn.rollback()
                    return None, http_error(400, "Failed to create API key", None, "failed_create_api_key")
                await self.conn.commit()
                return ApiKey(**new_api_key), None
        except Exception as e:
            await self.conn.rollback()
            return None, http_error(400, str(e), None, "unexpected_error")

    #
    # For security reasons there's no function with fetchall() return.
    # Also (for the same reasons) there are no read and update functions with **kwargs;
    # for updating there are only separate funcs for each column (except for `api_key` and `date_db`).
    #

    async def api_key_read(
        self,
        api_key: str
    ) -> tuple[ApiKey | None, dict[str, str | int] | None]:
        """
        Reads the given API key in the database.

        :param api_key: The API key whose data needs to be obtained.
        :return: On success will return :class:`..types.api_key.ApiKey` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
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
                    await self.conn.rollback()
                    return None, http_error(404, f"API key '{api_key}' not found", None, "api_key_not_found")
                return ApiKey(**api_key), None
        except Exception as e:
            return None, http_error(400, str(e), None, "unexpected_error")

    async def api_key_update_permissions(
        self,
        api_key: str,
        new_permissions: str = 'r'
    ) -> tuple[bool | None, dict[str, str | int] | None]:
        """
        Updates the :code:`permissions` column for the given API key in the database.

        :param api_key: The API key whose data needs to be updated.
        :param new_permissions: New permissions for the API key in format (example): 'cud', 'rd', 'cd', etc. Full rights would be 'crud'.
        :return: On success will return :code:`True` or if rowcount is stil 0 - :code:`False` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
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
            await self.conn.rollback()
            return None, http_error(400, str(e), None, "unexpected_error")

    async def api_key_update_is_superkey(
        self,
        api_key: str,
        new_is_superkey: bool = False
    ) -> tuple[bool | None, dict[str, str | int] | None]:
        """
        Updates the :code:`is_superkey` column for the given API key in the database.

        :param api_key: The API key whose data needs to be updated.
        :param new_is_superkey: Note: Superkey can CRUD (based on superkey's *permissions*) other API keys.
        :return: On success will return :code:`True` or if rowcount is stil 0 - :code:`False` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
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
            await self.conn.rollback()
            return None, http_error(400, str(e), None, "unexpected_error")

    async def api_key_update_owner_id(
        self,
        api_key: str,
        new_owner_id: int | None = None
    ) -> tuple[bool | None, dict[str, str | int] | None]:
        """
        Updates the :code:`owner_id` column for the given API key in the database.

        :param api_key: The API key whose data needs to be updated.
        :param new_owner_id: Note: Telegram ID of the API key's owner. Optional in DB.
        :return: On success will return :code:`True` or if rowcount is stil 0 - :code:`False` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
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
                        await self.conn.rollback()
                        return None, http_error(404, "Specified user doesn't exist", "new_owner_id", "user_not_found")

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
            await self.conn.rollback()
            return None, http_error(400, str(e), None, "unexpected_error")

    async def api_key_delete(
        self,
        api_key: str
    ) -> tuple[bool | None, dict[str, str | int] | None]:
        """
        Deletes the given API key from the database.

        :param api_key: The API key that needs to be deleted.
        :return: On success will return :code:`True` or if rowcount is stil 0 - :code:`False` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
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
            await self.conn.rollback()
            return None, http_error(400, str(e), None, "unexpected_error")

    #####################
    #                   #
    #   Table "users"   #
    #                   #
    #####################

    async def user_create_update(
        self,
        id: int,
        first_name: str,
        last_name: str | None = None,
        username: str | None = None,
        language_code: str | None = None,
        is_premium: bool | None = None,
        added_to_attachment_menu: bool | None = None,
        can_join_groups: bool | None = None,
        can_read_all_group_messages: bool | None = None,
        supports_guest_queries: bool | None = None,
        supports_inline_queries: bool | None = None,
        can_connect_to_business: bool | None = None,
        has_main_web_app: bool | None = None,
        has_topics_enabled: bool | None = None,
        allows_users_to_create_topics: bool | None = None,
        can_manage_bots: bool | None = None,
        zoneinfo: str | None = None,
    ) -> tuple[User | None, dict[str, str | int] | None]:
        """
        Creates user in the database.

        Source: https://docs.aiogram.dev/en/v3.28.2/api/types/user.html

        :param zoneinfo: *Optional*. The string that will be used to fill ZoneInfo (Source: https://docs.python.org/3/library/zoneinfo.html#the-zoneinfo-class).
        :return: On success will return :class:`aiogram.types.user.User` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
        """
        data = locals().copy(); data.pop("self")

        try:
            async with self.conn.cursor() as cur:
                if username:
                    await cur.execute(
                        """
                        UPDATE users
                        SET username = NULL
                        WHERE username = %s and id != %s
                        """,
                        (username.casefold(), id)
                    )

                columns: list[sql.SQL[str]] = []
                params: list[sql.SQL[Any]] = []
                for column, param in data.items():
                    params.append(param)
                    if column == "id": continue
                    elif column == "zoneinfo": columns.append(sql.SQL(f"{column} = COALESCE(EXCLUDED.{column}, users.{column})"))
                    else:
                        columns.append(sql.SQL("{excldd} = EXCLUDED.{excldd}").format(
                            excldd=sql.Identifier(column)
                        ))

                await cur.execute(
                    sql.SQL(
                        """
                        INSERT INTO users ({})
                        VALUES ({})
                        ON CONFLICT (id) DO UPDATE SET
                            {}
                        RETURNING *
                        """,
                    ).format(
                        sql.SQL(", ").join(map(sql.Identifier, data.keys())),
                        sql.SQL(", ").join([sql.Placeholder() for _ in params]),
                        sql.SQL(", ").join(columns)
                    ),
                    params
                )
                new_user: dict[str, Any] = await cur.fetchone()
                if new_user is None:
                    await self.conn.rollback()
                    return None, http_error(400, f"Failed to create or update user '{id}'", None, "failed_create_update_user")
                await self.conn.commit()
                return User(**new_user), None
        except Exception as e:
            await self.conn.rollback()
            return None, http_error(400, str(e), None, "unexpected_error")

    async def user_read(
        self,
        id_or_username: int | str
    ) -> tuple[User | None, dict[str, str | int] | None]:
        """
        Reads the given user in the database by his id or username.

        :param id_or_username: The user's ID or username whose data needs to be obtained.
        :return: On success will return :class:`aiogram.types.user.User` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
        """
        id_or_username = str(id_or_username)

        try:
            async with self.conn.cursor() as cur:
                if id_or_username.isdigit():
                    await cur.execute(
                        """
                        SELECT *
                        FROM users
                        WHERE id = %s
                        """,
                        (int(id_or_username),)
                    )
                else:
                    await cur.execute(
                        """
                        SELECT *
                        FROM users
                        WHERE username = %s
                        """,
                        (id_or_username.casefold(),)
                    )

                user: dict[str, Any] = await cur.fetchone()
                if user is None:
                    await self.conn.rollback()
                    return None, http_error(404, f"User '{id_or_username}' not found", None, "user_not_found")
                return User(**user), None
        except Exception as e:
            return None, http_error(400, str(e), None, "unexpected_error")

    async def user_readall(
        self,
        allow_None_values: bool = False,
        **columns_for_search
    ) -> tuple[list[User] | None, dict[str, str | int] | None]:
        """
        Searches for users by given params.

        :param allow_None_values: If :code:`True`, then the search will be performed even on None values (for examle, if you need users without a username). Otherwise, None params will be skipped.
        :param **columns_for_search: Search parameters.
        :return: On success will return list of :class:`aiogram.types.user.User` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
        """
        columns: list[sql.SQL[str]] = []
        params: list[sql.SQL[Any]] = []
        for column, param in columns_for_search.items():
            if not allow_None_values and param is None:
                continue
            params.append(param)
            columns.append(sql.SQL("{} = %s").format(
                sql.Identifier(column)
            ))

        try:
            async with self.conn.cursor() as cur:
                await cur.execute(
                    sql.SQL(
                        """
                        SELECT *
                        FROM users
                        WHERE {}
                        """
                    ).format(
                        sql.SQL(" AND ").join(columns)
                    ),
                    params
                )
                users: list[dict[str, Any]] = await cur.fetchall()
                if users is None:
                    await self.conn.rollback()
                    return None, http_error(404, "No users found", None, "users_not_found")
                users_classes: list[User] = []
                for user in users:
                    users_classes.append(User(**user))
                return users_classes, None
        except UndefinedColumn as e:
            return None, http_error(404, "One of the given columns was not found", None, "undefined_column")
        except Exception as e:
            return None, http_error(400, str(e), None, "unexpected_error")

    async def user_delete(
        self,
        user_id: int
    ) -> tuple[bool | None, dict[str, str | int] | None]:
        """
        Deletes the given user from the database.

        :param user_id: The user that needs to be deleted.
        :return: On success will return :code:`True` or if rowcount is stil 0 - :code:`False` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
        """
        try:
            async with self.conn.cursor() as cur:
                await cur.execute(
                    """
                    DELETE FROM users
                    WHERE id = %s
                    """,
                    (user_id,)
                )

                if cur.rowcount == 0:
                    return False, None    

                await self.conn.commit()
                return True, None
        except Exception as e:
            await self.conn.rollback()
            return None, http_error(400, str(e), None, "unexpected_error")

    #####################
    #                   #
    #   Table "chats"   #
    #                   #
    #####################

    async def chat_create_update(
        self,
        id: int,
        type: str,
        title: str | None = None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        is_forum: bool | None = None,
        is_direct_messages: bool | None = None,
        language_code: str | None = None,
        owner_id: int | None = None,
        zoneinfo: str | None = None,
    ) -> tuple[Chat | None, dict[str, str | int] | None]:
        """
        Creates chat in the database.

        Source: https://docs.aiogram.dev/en/v3.28.2/api/types/chat.html

        :param language_code: Telegram language code for whole chat. Optional in DB.
        :param owner_id: User Telegram ID of chat's owner. Optional in DB.
        :param zoneinfo: The string that will be used to fill ZoneInfo (Source: https://docs.python.org/3/library/zoneinfo.html#the-zoneinfo-class). Optional in DB.
        :return: On success will return :class:`aiogram.types.chat.Chat` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
        """
        data = locals().copy(); data.pop("self")

        try:
            async with self.conn.cursor() as cur:
                if username:
                    await cur.execute(
                        """
                        UPDATE chat
                        SET username = NULL
                        WHERE username = %s and id != %s
                        """,
                        (username.casefold(), id)
                    )

                columns: list[sql.SQL[str]] = []
                params: list[sql.SQL[Any]] = []
                for column, param in data.items():
                    params.append(param)
                    if column == "id": continue
                    elif column == "zoneinfo": columns.append(sql.SQL(f"{column} = COALESCE(EXCLUDED.{column}, chats.{column})"))
                    elif column == "language_code": columns.append(sql.SQL(f"{column} = COALESCE(EXCLUDED.{column}, chats.{column})"))
                    elif column == "owner_id": columns.append(sql.SQL(f"{column} = COALESCE(EXCLUDED.{column}, chats.{column})"))
                    else:
                        columns.append(sql.SQL("{excldd} = EXCLUDED.{excldd}").format(
                            excldd=sql.Identifier(column)
                        ))

                await cur.execute(
                    sql.SQL(
                        """
                        INSERT INTO chats ({})
                        VALUES ({})
                        ON CONFLICT (id) DO UPDATE SET
                            {}
                        RETURNING *
                        """,
                    ).format(
                        sql.SQL(", ").join(map(sql.Identifier, data.keys())),
                        sql.SQL(", ").join([sql.Placeholder() for _ in params]),
                        sql.SQL(", ").join(columns)
                    ),
                    params
                )
                new_chat: dict[str, Any] = await cur.fetchone()
                if new_chat is None:
                    await self.conn.rollback()
                    return None, http_error(400, f"Failed to create or update chat '{id}'", None, "failed_create_update_chat")
                await self.conn.commit()
                return Chat(**new_chat), None
        except Exception as e:
            await self.conn.rollback()
            return None, http_error(400, str(e), None, "unexpected_error")

    async def chat_read(
        self,
        id_or_username: int | str
    ) -> tuple[Chat | None, dict[str, str | int] | None]:
        """
        Reads the given chat in the database by his id or username.

        :param id_or_username: The chat's ID or username whose data needs to be obtained.
        :return: On success will return :class:`aiogram.types.chat.Chat` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
        """
        id_or_username = str(id_or_username)

        try:
            async with self.conn.cursor() as cur:
                if id_or_username.isdigit():
                    await cur.execute(
                        """
                        SELECT *
                        FROM chats
                        WHERE id = %s
                        """,
                        (int(id_or_username),)
                    )
                else:
                    await cur.execute(
                        """
                        SELECT *
                        FROM chats
                        WHERE username = %s
                        """,
                        (id_or_username.casefold(),)
                    )

                chat: dict[str, Any] = await cur.fetchone()
                if chat is None:
                    await self.conn.rollback()
                    return None, http_error(404, f"Chat '{id_or_username}' not found", None, "chat_not_found")
                return Chat(**chat), None
        except Exception as e:
            return None, http_error(400, str(e), None, "unexpected_error")

    async def chat_readall(
        self,
        allow_None_values: bool = False,
        **columns_for_search
    ) -> tuple[list[User] | None, dict[str, str | int] | None]:
        """
        Searches for chats by given params.

        :param allow_None_values: If :code:`True`, then the search will be performed even on None values (for examle, if you need chats without a username). Otherwise, None params will be skipped.
        :param **columns_for_search: Search parameters.
        :return: On success will return list of :class:`aiogram.types.chat.Chat` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
        """
        columns: list[sql.SQL[str]] = []
        params: list[sql.SQL[Any]] = []
        for column, param in columns_for_search.items():
            if not allow_None_values and param is None:
                continue
            params.append(param)
            columns.append(sql.SQL("{} = %s").format(
                sql.Identifier(column)
            ))

        try:
            async with self.conn.cursor() as cur:
                await cur.execute(
                    sql.SQL(
                        """
                        SELECT *
                        FROM chats
                        WHERE {}
                        """
                    ).format(
                        sql.SQL(" AND ").join(columns)
                    ),
                    params
                )
                chats: list[dict[str, Any]] = await cur.fetchall()
                if chats is None:
                    await self.conn.rollback()
                    return None, http_error(404, "No chats found", None, "chats_not_found")
                chats_classes: list[Chat] = []
                for chat in chats:
                    chats_classes.append(Chat(**chat))
                return chats_classes, None
        except UndefinedColumn as e:
            return None, http_error(404, "One of the given columns was not found", None, "undefined_column")
        except Exception as e:
            return None, http_error(400, str(e), None, "unexpected_error")

    async def chat_delete(
        self,
        chat_id: int
    ) -> tuple[bool | None, dict[str, str | int] | None]:
        """
        Deletes the given chat from the database.

        :param chat_id: The chat that needs to be deleted.
        :return: On success will return :code:`True` or if rowcount is stil 0 - :code:`False` & :code:`None` as error. Otherwise, :code:`None` & error in format of :func:`..utils.http_error`.
        """
        try:
            async with self.conn.cursor() as cur:
                await cur.execute(
                    """
                    DELETE FROM chat
                    WHERE id = %s
                    """,
                    (chat_id,)
                )

                if cur.rowcount == 0:
                    return False, None

                await self.conn.commit()
                return True, None
        except Exception as e:
            await self.conn.rollback()
            return None, http_error(400, str(e), None, "unexpected_error")