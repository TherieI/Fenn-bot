from discord.ext import commands
from discord import FFmpegPCMAudio, Message, Member, VoiceState, TextChannel, File
from asyncio import sleep
from random import randint, random, choice
from main import FennsBot
from math import exp
from typing import List
import os

# Reddit fetch stuff
from asyncpraw import Reddit
from asyncpraw.models.reddit.submission import Submission
from RedDownloader import RedDownloader


audio = "resources/vine_boom.mp3"
BOOM_DELAY = 3.0  # vine boom has a chance of occuring every 3 seconds
BOOM_FACTOR = 20  # 1/X Chance of playing the vine boom

# Fenn stores the last X amount of posts to avoid reposts
POST_CACHE = 50

class FennsHangouts(commands.Cog):
    def __init__(self, bot: FennsBot) -> None:
        super().__init__()
        self.bot = bot
        self.current_voice_channel = None
        self.fenns_hangouts_guild_id = 987495278892433480
        self.reddit = Reddit(
            client_id="HYvVKpM1Gx3OxKmjNTJ4hQ",
            client_secret="mgnAvEHUQKiZRXxqcpmnL5MIan2MUw",
            user_agent="Fenn's Scrapinator by u/Thendriz",
        )
        self.posts = []
        self.send_memes = True

    def fenns_message_react_chance(self, message_len: int) -> float:
        return 1 / (8 + exp(-0.1 * message_len + 8.4)) + 0.03

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        guild = self.bot.get_guild(self.fenns_hangouts_guild_id)
        while True:
            if self.send_memes:
                await self.send_meme_from_subreddit("animemes")
                await self.send_meme_from_subreddit("greentext", to_channel=guild.get_channel(1136533072855171093))
                # Sleep for 3-9 hours
                await sleep(5)

    async def send_meme_from_subreddit(self, subreddit: str, to_channel=None):
        # Define output channel
        channel = self.random_text_channel() if to_channel == None else to_channel
        # Find reddit post
        reddit_thread = await self.reddit.subreddit(subreddit)
        post_choices = [post async for post in reddit_thread.new(limit=3)]
        submission: Submission = choice(post_choices)
        # Repost check
        scope_inc = 0
        while submission.id in self.posts:
            post_choices = [post async for post in reddit_thread.new(limit=3 + scope_inc)]
            submission = choice(post_choices)
            scope_inc += 1
        # Update posts for repost check
        if len(self.posts) > POST_CACHE:
            # Remove last post
            self.posts.pop(0)
        self.posts.append(submission.id)

        # Download files
        link = "https://www.reddit.com" + submission.permalink
        RedDownloader.Download(url=link, destination="temp/", verbose=False)
        # Parse download output
        file_name = os.listdir("temp")[0]
        output = os.path.join(os.getcwd(), "temp", file_name)
        if os.path.isfile(output):
            # Singular file
            await channel.send(file=File(output, file_name))
            # Delete file
            os.remove(output)
        else:
            # Directory
            temp = os.path.join(os.getcwd(), "temp")
            # Delete directory
            for root, dirs, files in os.walk(temp, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    # Post file
                    await channel.send(file=File(fp=file_path, filename=name))
                    os.remove(file_path)
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

    def random_text_channel(self) -> TextChannel:
        guild = self.bot.get_guild(self.fenns_hangouts_guild_id)
        # Choose one channel from a list only text channels
        return choice(
            list(filter(lambda channel: type(channel) == TextChannel, guild.channels))
        )

    @commands.Cog.listener(name="on_message")
    async def fenn_react(self, message: Message):
        if message.guild.id == self.fenns_hangouts_guild_id and not message.author.bot:
            react_chance = self.fenns_message_react_chance(
                len(message.content.split(" "))
            )
            print(f"{react_chance=}")
            if message.author.id == self.bot.owner_id or random() <= react_chance / 5:
                # Give gab chad emote (or chat a small chance of these emotes)
                emotes = [
                    "<:nave:613525321420898339>",
                    "<:noovin:1094798214294683718>",
                    "<:Pog:842595542496182312>",
                    "<:yan_left_1:843635990785949707>",
                    "<:yan_left_2:843636001838596097>",
                    "<:yan_right_1:843636015012773909>",
                    "<:yan_right_2:843636023451713547>",
                ]
            else:
                emotes = list(message.guild.emojis) + [":thumbsup:"] + ["💀"] * 2
            if len(message.attachments) >= 1 and random() <= 0.15:
                # React to (hard) image
                emote = choice(emotes)
                await sleep(randint(3, 15))
                await message.add_reaction(emote)
                return
            elif random() <= react_chance:
                # Fenn react to message
                emote = choice(emotes)
                await sleep(randint(3, 15))
                await message.add_reaction(emote)

    @commands.Cog.listener(name="on_voice_state_update")
    async def vine_boom(self, member: Member, before: VoiceState, after: VoiceState):
        if member != None and member.guild.id != self.fenns_hangouts_guild_id:
            return
        # print(f"{member=}\n{before=}\n{after=}")
        if member.bot:
            if after.channel == None and self.current_voice_channel != None:
                # Fenn was disconnected by user
                await self.current_voice_channel.disconnect(force=True)
                self.current_voice_channel = None
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
