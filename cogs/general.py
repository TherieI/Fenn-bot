from discord import app_commands, Interaction, Message, Embed, ui, ButtonStyle, File
from discord.ext.commands import Cog
from typing import List, Union
from main import FennsBot, FennsIcon
from discord.app_commands import Choice
import io


class EmbedBook(ui.View):
    def __init__(self, embeds: List[Embed]):
        """len(embeds) must be greater than or equal to 1"""
        super().__init__()
        self.current_page = 0
        self.embeds = embeds
        if len(embeds) == 1:
            self.reset_pages(prev_disabled=True, next_disabled=True)
        else:
            self.reset_pages(prev_disabled=True)

    def reset_pages(self, prev_disabled: bool = False, next_disabled: bool = False):
        self.clear_items()
        prev_page = ui.Button(
            style=ButtonStyle.blurple,
            emoji="<:prev_page:780564661275852890>",
            disabled=prev_disabled,
        )
        prev_page.callback = self.prev_page
        next_page = ui.Button(
            style=ButtonStyle.blurple,
            emoji="<:next_page:780564809296904233>",
            disabled=next_disabled,
        )
        next_page.callback = self.next_page
        self.add_item(prev_page)
        self.add_item(next_page)

    async def prev_page(self, interaction: Interaction):
        self.current_page -= 1
        if self.current_page <= 0:
            # Disable prev page
            self.reset_pages(prev_disabled=True)
        elif self.current_page == len(self.embeds) - 2:
            # Enable both buttons
            self.reset_pages()
        await interaction.response.edit_message(
            embed=self.embed_with_page_num(), view=self
        )

    async def next_page(self, interaction: Interaction):
        self.current_page += 1
        if self.current_page >= len(self.embeds) - 1:
            # Disable next page
            self.reset_pages(next_disabled=True)
        elif self.current_page == 1:
            # Enable both buttons
            self.reset_pages()
        await interaction.response.edit_message(
            embed=self.embed_with_page_num(), view=self
        )

    def embed_with_page_num(self) -> Embed:
        embed = self.embeds[self.current_page]
        return embed.set_footer(text=f"Page {self.current_page + 1}/{len(self.embeds)}")


class GeneralCommands(Cog):
    def __init__(self, bot: FennsBot) -> None:
        super().__init__()
        self.bot = bot
        
    @Cog.listener(name="on_ready")
    async def on_ready(self):
        print(self.get_listeners())

    @app_commands.command(
        name="logging",
        description="Change the logging debug level of Fenn. Only usable by the real.",
    )
    @app_commands.describe(level="Log level")
    @app_commands.choices(
        level=[
            Choice(name="CRITICAL", value="50"),
            Choice(name="ERROR", value="40"),
            Choice(name="WARNING", value="30"),
            Choice(name="INFO", value="20"),
            Choice(name="DEBUG", value="10"),
            Choice(name="NOTSET", value="0"),
        ]
    )
    async def log_cmd(
        self, interaction: Interaction, level: Choice[str],
    ):
        if interaction.user.id == self.bot.owner_id:
            self.bot.logger.setLevel(level.name)
            embed, png = self.bot.fenns_embed()
            embed.add_field(name="__Logging__", value=f"{level.name}={level.value}")
            await interaction.response.send_message(embed=embed, file=png, ephemeral=True)

    @app_commands.command(
        name="logfile",
        description="Retrieve the log file of fenn. Only usable by the real.",
    )
    @app_commands.describe(date="Collect all logs from specified date (format=YYYY-MM-DD)")
    async def log_file_cmd(self, interaction: Interaction, date: Union[None, str] = ""):
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id == self.bot.owner_id:
            log_bytes = self.bot.log_file(date=date).encode('utf-8')
            file_bytes = io.BytesIO(log_bytes)
            log_file = File(file_bytes, "fenns_log.txt")
            await interaction.followup.send(file=log_file, ephemeral=True)

    @app_commands.command(
        name="listener",
        description="So gab can create listener messages. Only he may perform this act.",
    )
    async def create_listener(self, interaction: Interaction, message: str):
        if not await self.bot.is_owner(interaction.user):
            self.bot.send_failure(interaction, message="You are not the owner. Grr.")
            return
        embed, png = self.bot.fenns_embed(FennsIcon.BULKING)
        embed.title = "__Bulking Channels__"
        embed.description = "__Create__ a personal channel to track your own progress.\n__React__ '🏋️' for a channel."
        await interaction.response.send_message(embed=embed, file=png)

    @Cog.listener(name="on_message")
    async def fish_react(self, message: Message):
        if not message.author.bot and message.author.id == self.bot.owner_id:
            # The real commands
            # Fish react
            if (
                "fish" in message.content.lower()
                or "https://tenor.com/view/discord-gif-27442765" in message.content
            ):
                if message.reference != None:
                    react_to = await message.channel.fetch_message(
                        message.reference.message_id
                    )
                else:
                    react_to = [msg async for msg in message.channel.history(limit=2)][
                        1
                    ]
                await react_to.add_reaction("🐟")
    
    @Cog.listener(name="on_command_error")
    async def on_command_error(self, /, *args, **kwargs):
        print("GENERAL Error")
        self.bot.on_error(*args, **kwargs)


async def setup(bot: FennsBot):
    await bot.add_cog(GeneralCommands(bot))
