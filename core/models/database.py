"""
The MIT License (MIT)

Copyright (c) 2023-present MrSniFo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from aiosqlite import connect, Connection, Cursor
from ..utils import encrypt, decrypt


class Database(object):
    __slots__ = ('connection', 'cursor', 'secret_key')

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.connection: Connection | None = None
        self.cursor: Cursor | None = None

    async def __aenter__(self):
        self.connection = await connect(database="members.db", detect_types=3)
        self.cursor = await self.connection.cursor()

        # members(*id, storage_1,  storage_2, permissions, updated_at ,created_at)
        await self.cursor.execute("""CREATE TABLE IF NOT EXISTS members(
                                                            id INTEGER PRIMARY KEY,
                                                            storage_1 TEXT DEFAULT '',
                                                            storage_2 TEXT DEFAULT '',
                                                            permissions TEXT DEFAULT '',
                                                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL);
                                                            """)
        return self

    @staticmethod
    def permissions_format(perms: str) -> list:
        if len(perms) != 0:
            return [int(_id) for _id in perms.split(",")]
        else:
            return []

    async def has_vault(self, member_id: int) -> bool:
        # Checks if  member exists.
        get_guild = await self.cursor.execute("""SELECT * FROM members WHERE id = ?;""", (member_id,))
        fetch_member = await get_guild.fetchone()
        if fetch_member is None:
            return False
        else:
            return True

    async def get_member(self, member_id: int) -> dict:
        # -------------------------
        # Checks if the member exists.
        get_guild = await self.cursor.execute("""SELECT * FROM members WHERE id = ?;""", (member_id,))
        fetch_member = await get_guild.fetchone()
        if fetch_member is None:
            await self.cursor.execute("""INSERT INTO members(id) VALUES(?);""", (member_id,))
            await self.connection.commit()
            return {"member_id": member_id, "storage_1": "", "storage_2": "", "permissions": []}
        else:
            storage_1 = decrypt(key=self.secret_key, source=fetch_member[1])
            storage_2 = decrypt(key=self.secret_key, source=fetch_member[2])
            return {"member_id": member_id,
                    "storage_1": storage_1,
                    "storage_2": storage_2,
                    "permissions": self.permissions_format(perms=fetch_member[3])}

    async def update_storage(self, member_id: int, storage_1: str, storage_2: str) -> None:
        storage_1 = encrypt(key=self.secret_key, source=storage_1)
        storage_2 = encrypt(key=self.secret_key, source=storage_2)
        sql: str = """UPDATE members SET storage_1 = ?, storage_2 = ?, updated_at = datetime('now', 'localtime') 
        WHERE id = ? """
        await self.cursor.execute(sql, (storage_1, storage_2, member_id))
        await self.connection.commit()

    async def perms_add(self, member_id: int, target_id: int) -> bool:
        member = await self.get_member(member_id=member_id)
        if target_id not in member["permissions"]:
            permissions = ", ".join(map(str, member["permissions"] + [target_id]))
            sql: str = """UPDATE members SET permissions = ?, updated_at = datetime('now', 'localtime') WHERE id = ?"""
            await self.cursor.execute(sql, (permissions, member_id))
            await self.connection.commit()
            return True
        else:
            return False

    async def perms_remove(self, member_id: int, target_id: int) -> bool:
        member = await self.get_member(member_id=member_id)
        if target_id in member["permissions"]:
            member["permissions"].remove(target_id)
            permissions = ", ".join(map(str, member["permissions"]))
            sql: str = """UPDATE members SET permissions = ?, updated_at = datetime('now', 'localtime') WHERE id = ?"""
            await self.cursor.execute(sql, (permissions, member_id))
            await self.connection.commit()
            return True
        else:
            return False

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connection.close()
