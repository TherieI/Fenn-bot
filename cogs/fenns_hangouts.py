from discord.ext import commands
from discord import FFmpegPCMAudio, Message
from asyncio import sleep
from random import randint, random, choice
from main import FennsBot

audio = "resources/vine_boom.mp3"
BOOM_DELAY = 3.0  # vine boom has a chance of occuring every 3 seconds
BOOM_FACTOR = 30  # 1/X Chance of playing the vine boom


class FennsHangouts(commands.Cog):
    def __init__(self, bot: FennsBot) -> None:
        super().__init__()
        self.bot = bot
        self.current_voice_channel = None
        self.fenns_hangouts_guild_id = 987495278892433480
        self.react_chance = 1

    @commands.Cog.listener(name="on_message")
    async def fenn_react(self, message: Message):
        if message.guild.id == self.fenns_hangouts_guild_id and random() <= self.react_chance:
            # Fenn react
            if message.author.id == self.bot.owner_id or random() <= self.react_chance / 5:
                # Give gab chad emote (or chat a small chance of these emotes)
                emotes = ["<:nave:613525321420898339>", "<:noovin:1094798214294683718>", "<:Pog:842595542496182312>", "<:yan_left_1:843635990785949707>", "<:yan_left_2:843636001838596097>", "<:yan_right_1:843636015012773909>", "<:yan_right_2:843636023451713547>"]
            else:
                emotes = list(message.guild.emojis) + ["💀", "💀", "💀", "💀", "<:dayruin:845485839127019520>"]
            emote = choice(emotes)
            await sleep(randint(3, 15))
            await message.add_reaction(emote)

    @commands.Cog.listener(name="on_voice_state_update")
    async def vine_boom(self, member, before, after):
        if member == self.bot.user:
            return
        if after.channel:
            # Joined a channel
            if self.current_voice_channel != None:
                # The bot is currently in a VC, so disconnect (if theres no one else)
                await self.current_voice_channel.disconnect()
                self.current_voice_channel = None
            # Connect to VC
            self.current_voice_channel = await after.channel.connect(self_deaf=True)

            # Potentially play sfx sounds every delay seconds
            while (
                self.current_voice_channel and self.current_voice_channel.is_connected()
            ):
                # Attempt to play a vine boom
                if (
                    randint(0, BOOM_FACTOR) == 0
                    and not self.current_voice_channel.is_playing()
                ):
                    # Play boom
                    sfx = FFmpegPCMAudio(audio)
                    self.current_voice_channel.play(sfx)
                await sleep(BOOM_DELAY)

        else:
            # Left a channel
            if len(before.channel.members) <= 1 and self.current_voice_channel != None:
                # Only leave if the channel has no members (1 includes bot)
                await self.current_voice_channel.disconnect()
                self.current_voice_channel = None

        # print(f"{member.name} in {after.channel}")


async def setup(bot: FennsBot):
    await bot.add_cog(FennsHangouts(bot))
