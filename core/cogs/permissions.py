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

# ------ Core ------
from ..bot import Bot
from ..models import Database
from ..utils import embed_wrong

# ------ Discord ------
from discord import Interaction, app_commands, Embed, Member
from discord.ext.commands import Cog
from typing import Literal


class Permissions(Cog):
    __slots__ = "bot"

    def __init__(self, bot: Bot) -> None:
        """
        Permissions code slash command
        """
        self.bot = bot

    @app_commands.command(name="permissions",
                          description="Allows you to specify who can view and modify your vault")
    @app_commands.describe(option="Granting or Revoking access")
    async def slash(self, interaction: Interaction, option: Literal["add", "remove"], member: Member):
        if interaction.user.id != member.id:
            async with Database(secret_key=self.bot.secret_key) as db:
                # ---------------\
                # Add permissions
                embed = Embed(title="Vault permissions")
                if option == "add":
                    added: bool = await db.perms_add(member_id=interaction.user.id, target_id=member.id)
                    if added:
                        embed.description = f"`{member.name} Has been granted access to your vault`"
                        embed.colour = 0x738adb
                    else:
                        embed.description = f"`{member.name} Already has permission to access your vault`"
                # ------------------\
                # remove permissions
                elif option == "remove":
                    removed: bool = await db.perms_remove(member_id=interaction.user.id, target_id=member.id)
                    if removed:
                        embed.description = f"`{member.name} Has been removed from the vault's access list`"
                        embed.colour = 0xe74c3c
                    else:
                        embed.description = f"`{member.name} Does not already have permission to access your vault`"


            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = embed_wrong(msg=f"You cannot give yourself permission to access to your vault")
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot) -> None: await bot.add_cog(Permissions(bot))
