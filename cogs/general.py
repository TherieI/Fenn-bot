from discord import app_commands, Interaction, Message
from discord.ext.commands import Cog
from main import FennsBot, FennsIcon
from random import random, choice
from asyncio import sleep


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

    @Cog.listener(name="on_message")
    async def fish_react(self, message: Message):
        if message.author.id == self.bot.owner_id:
            # The real commands
            # Fish react
            if "fish" in message.content.lower() or "https://tenor.com/view/discord-gif-27442765" in message.content:
                if message.reference != None:
                    react_to = await message.channel.fetch_message(message.reference.message_id)
                else:
                    react_to = [msg async for msg in message.channel.history(limit=2)][1]
                await react_to.add_reaction("🐟")


async def setup(bot: FennsBot):
    await bot.add_cog(GeneralCommands(bot))
