from discord.ext import commands
from discord import FFmpegPCMAudio
from asyncio import sleep
from random import randint

audio = "resources/vine_boom.mp3"
BOOM_DELAY = 3.0  # vine boom has a chance of occuring every 3 seconds
BOOM_FACTOR = 30  # 1/X Chance of playing the vine boom


class FennsHangouts(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.current_voice_channel = None

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


async def setup(bot: commands.Bot):
    await bot.add_cog(FennsHangouts(bot))
