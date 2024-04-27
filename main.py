import discord
from discord.ext import commands
from asyncio import run as async_run
import os
from typing import Tuple
import sys, traceback
from datetime import datetime, timedelta

LOG_FILE = "fennl.log"
MAIN_PATH = os.getcwd()

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

intents = discord.Intents.all()
intents.voice_states = True

from enum import Enum
class FennsIcon(Enum):
    ERROR = 0
    STANDARD = 1
    BULKING = 2

class FennsBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(intents=intents, command_prefix="f!")
        # generate a dict of filename: extension for fenn's icon files
        self.icon_files = {
            fname[0].lower(): fname[1]
            for fname in list(
                map(lambda f: f.split("."), os.listdir("resources/thumbnails"))
            )
        }
        self.owner_id = 283677434476363776
        self.reaction_listeners = [ # Message id's the bot should listen to
            1173735486578245744
        ]
        # Logging to console and discord
        self.logger = logging.getLogger()
        # Create a file handler and set the logging level
        file_handler = logging.FileHandler(LOG_FILE)
        # Create a console handler and set the logging level
        console_handler = logging.StreamHandler()
        # Add the handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    async def on_ready(self):
        self.log(f"{self.user} is up and running!")

    async def on_message(self, message: discord.Message):
        if not message.author.bot:
            await self.process_commands(message)

    async def setup_hook(self):
        for cog in os.listdir("cogs"):
            if cog.endswith(".py"):
                print("Loading COG: " + cog)
                await self.load_extension(f"cogs.{cog[:-3]}")

        fenns_bulking_guild = discord.Object(id=1172288447592022146)
        self.tree.copy_global_to(guild=fenns_bulking_guild)
        cmds = await self.tree.sync()
        for cmd in cmds:
            print(f"AVAILABLE SLASH CMD: {cmd.name}")

    def fenns_embed(
        self, icon: FennsIcon = FennsIcon.STANDARD
    ) -> Tuple[discord.Embed, discord.File]:
        file_type = self.icon_files[icon.name.lower()]
        discord_file = discord.File(
            f"resources/thumbnails/{icon.name.lower()}.{file_type}",
            filename=f"{icon.name.lower()}.{file_type}",
        )
        embed = discord.Embed()
        embed.color = discord.Color.purple()
        embed.set_thumbnail(url=f"attachment://{icon.name.lower()}.{file_type}")
        return embed, discord_file

    async def send_failure(
        self,
        interaction: discord.Interaction,
        message: str = None,
        failed_command: str = None,
        failed_parameter: str = None,
    ):
        embed, gif = self.fenns_embed(FennsIcon.ERROR)
        embed.title = "Failed!"
        if message != None:
            embed.add_field(name="What went wrong?", value=f"{message}")
        if failed_command != None:
            embed.add_field(name="Command   |", value=f"Ran='/{failed_command}'")
        if failed_parameter != None:
            embed.add_field(
                name="Error", value=f"Param: **>>**{failed_parameter}**<<**"
            )
        embed.set_footer(text="*Try to read the damn options, wouldya?!*")
        embed.color = discord.Colour.red()
        # Sending a gif can take time, so we need to defer then send it
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=embed, file=gif, ephemeral=True)
        # await interaction.response.send_message(embed=embed, file=gif, ephemeral=True)

    # Custom error handler (sends errors to Theriel)
    async def on_error(self, /, *args, **kwargs):
        # Print default information to console
        await super().on_error(self, args, kwargs)
        self.log("Sending error to mods...", log_level=logging.ERROR)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        time = datetime.now()
        msg = f"```py\n[{time.strftime('%d/%m/%y | %H:%M AM : %S.%f')}]\nTraceback (most recent call last):\n"
        for tb in traceback.format_tb(exc_traceback):
            msg += tb + "\n"
        msg += f"{exc_type.__name__}: {exc_value}\n```"
        mod = self.get_user(self.owner_id) 
        await mod.send(content=msg)
        self.logger.error(msg)

    # Function for debugging by sending logs to the owner
    def log(self, message, /, log_level=logging.INFO, *args, **kwargs):
        if self.logger.level >= log_level:
            print(message)
        try:
            self.logger.log(log_level, message, *args, **kwargs)
        except:
            self.logger.warn(f"Logging library error with message: {message}")

    # Get the contents of the log file from a certain date
    # If date is unspecified return the last 24 hours of info
    def log_file(self, date="") -> str:
        DATE_FORMAT = f"%Y-%m-%d"
        try:
            target_date = datetime.strptime(date, DATE_FORMAT)
        except ValueError:
            target_date = datetime.now() - timedelta(days=1)
        contents = []
        with open(os.path.join(MAIN_PATH, LOG_FILE), "r") as fenns_log:
            contents = fenns_log.readlines()
        starting_index = 0
        for line in contents:
            # First 10 characters of a line is the date
            date = datetime.strptime(line[0:10], DATE_FORMAT)
            if target_date <= date:
                break;
            starting_index += 1
        return "".join(contents[starting_index:])


async def main():
    bot = FennsBot(intents=intents)
    await bot.start(os.environ["DISCORD_TOKEN"])


if __name__ == "__main__":
    # Create temp file for media downloads if not already existing
    temp = os.path.join(MAIN_PATH, "temp")
    if not os.path.exists(temp):
        print("Folder temp not found! Creating folder...")
        os.makedirs(temp)
    # Remove all content (if any) in temp
    for root, dirs, files in os.walk(temp, topdown=False):
        for name in files:
            print(f"Removing file: {name} in temp")
            os.remove(os.path.join(root, name))
        for name in dirs:
            print(f"Removing directory: {name} in temp")
            os.rmdir(os.path.join(root, name))
    async_run(main())
