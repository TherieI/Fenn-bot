import discord
from discord.ext import commands
from asyncio import run as async_run
from os import listdir, environ as os_env
from typing import Tuple

import logging
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
intents.voice_states = True

fenns_bulking_guild = discord.Object(id=1172288447592022146)

from enum import Enum
class FennsIcon(Enum):
    ERROR    = 0
    STANDARD = 1
    BULKING  = 2

class FennsBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(intents=intents, command_prefix="f!")
        # generate a dict of filename: extension for fenn's icon files
        self.icon_files = {fname[0].lower(): fname[1] for fname in list(map(lambda f: f.split("."), listdir("resources/thumbnails")))}

    async def on_ready(self):
        print(f"{self.user} is up and running!")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

    async def setup_hook(self):
        for cog in listdir("cogs"):
            if cog.endswith(".py"):
                print("Loading COG: " + cog)
                await self.load_extension(f"cogs.{cog[:-3]}")

        self.tree.copy_global_to(guild=fenns_bulking_guild)
        cmds = await self.tree.sync()
        for cmd in cmds:
            print(f"AVAILABLE SLASH CMD: {cmd.name}")

    def fenns_embed(self, icon: FennsIcon = FennsIcon.STANDARD) -> Tuple[discord.Embed, discord.File]:
        file_type = self.icon_files[icon.name.lower()]
        discord_file = discord.File(f"resources/thumbnails/{icon.name.lower()}.{file_type}", filename=f"{icon.name.lower()}.{file_type}")
        embed = discord.Embed()
        embed.color = discord.Color.purple()
        embed.set_thumbnail(url=f"attachment://{icon.name.lower()}.{file_type}")
        return embed, discord_file
    
    async def send_failure(self, interaction: discord.Interaction, failed_command: str, failed_parameter: str):
        embed, gif = self.fenns_embed(FennsIcon.ERROR)
        embed.title = "Failed!"
        embed.add_field(name="Command   |", value=f"Ran='/{failed_command}'")
        embed.add_field(name="Error", value=f"Param: **>>**{failed_parameter}**<<**")
        embed.set_footer(text="*Try to read the damn options, wouldya?!*")
        embed.color = discord.Colour.red()
        # Sending a gif can take time, so we need to defer then send it
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=embed, file=gif, ephemeral=True)
        # await interaction.response.send_message(embed=embed, file=gif, ephemeral=True)


async def main():
    bot = FennsBot(intents=intents)
    await bot.start(os_env["DISCORD_TOKEN"])


if __name__ == "__main__":
    async_run(main())
