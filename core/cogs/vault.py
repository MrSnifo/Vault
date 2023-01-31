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
from discord import Interaction, app_commands, ui, Member, Embed, TextStyle
from discord.ext.commands import Cog


class Vault(Cog):
    __slots__ = "bot"

    def __init__(self, bot: Bot) -> None:
        """
        Vault slash command
        """
        self.bot = bot

    @app_commands.command(name="vault", description="Securely store and manage your data from any server.")
    @app_commands.describe(member="Open and manage a member's vault")
    async def slash(self, interaction: Interaction, member: Member = None) -> None:
        async with Database(secret_key=self.bot.secret_key) as db:
            has_vault: bool = False
            if member is not None:
                has_vault = await db.has_vault(member_id=member.id)
                # Checks if target has a vault.
                if not has_vault:
                    embed = embed_wrong(msg=f"{member.name} does not have a vault.")
                    await interaction.response.send_message(embed=embed, ephemeral=True)

            if (member is None) or (member is not None and has_vault):
                get_member: dict = await db.get_member(
                    member_id=member.id if member is not None else interaction.user.id)
                if (member is None) or (interaction.user.id in get_member["permissions"] + [member.id]):
                    modal = MyModal(member=member if member is not None else interaction.user,
                                    vault_storage_1=get_member["storage_1"],
                                    vault_storage_2=get_member["storage_2"],
                                    secret_key=self.bot.secret_key)
                    await interaction.response.send_modal(modal)
                else:
                    embed = embed_wrong(msg=f"You don't have permissions to access {member.name}'s vault.")
                    await interaction.response.send_message(embed=embed, ephemeral=True)


class MyModal(ui.Modal):
    __slots__ = ("member", "vault", "secret_key")

    def __init__(self, member: Member, vault_storage_1: str, vault_storage_2: str, secret_key: str):
        self.member = member
        self.vault_storage_1 = vault_storage_1
        self.vault_storage_2 = vault_storage_2
        self.secret_key = secret_key

        super().__init__(title=f"{self.member.name}'s vault")
        self.storage_1 = ui.TextInput(label="Storage 1",
                                      style=TextStyle.long,
                                      default=self.vault_storage_1,
                                      required=False)

        self.storage_2 = ui.TextInput(label="Storage 2",
                                      style=TextStyle.long,
                                      default=self.vault_storage_2,
                                      required=False)
        for item in [self.storage_1, self.storage_2]:
            self.add_item(item)

    async def on_submit(self, interaction: Interaction) -> None:
        if (str(self.storage_1.value) != self.vault_storage_1) or (str(self.storage_2.value) != self.vault_storage_2):
            async with Database(secret_key=self.secret_key) as db:
                await db.update_storage(member_id=self.member.id,
                                        storage_1=str(self.storage_1.value),
                                        storage_2=str(self.storage_2.value))
            embed = Embed(title="Vault", description="`Successfully updated!`", colour=0x738adb)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = Embed(title="Vault", description="`There is nothing to update`")
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot) -> None: await bot.add_cog(Vault(bot))
