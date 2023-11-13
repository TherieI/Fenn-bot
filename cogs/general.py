from discord import app_commands, Interaction
from discord.ext.commands import Cog
from main import FennsBot, FennsIcon


class GeneralCommands(Cog):
    def __init__(self, bot: FennsBot) -> None:
        super().__init__()
        self.bot = bot

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


async def setup(bot: FennsBot):
    await bot.add_cog(GeneralCommands(bot))
