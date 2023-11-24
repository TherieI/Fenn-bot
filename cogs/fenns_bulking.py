from discord.ext import commands
from discord import app_commands, Interaction, Guild
from discord import Member, User, Colour, RawReactionActionEvent, PermissionOverwrite
from discord.app_commands import Choice
from discord.ui import View
from json import loads, dumps
from typing import List, Union, Dict, Any
from main import FennsIcon, FennsBot
from datetime import datetime
from cogs.general import EmbedBook

"""Fenn's Bulking Server Commands"""

WEIGHT_EMOJI = "<:weight:1177345354342072412>"
REP_EMOJI = "<:reps:1177346322240647198>"
CLOCK_EMOJI = "<a:mc_clock:1177336089749508147>"
REPS = "ᴿᴱᴾ"

class Bulker:
    def __init__(self) -> None:
        self._workouts = []
        self._exercises = {}
        self.load_exercises()

    def workouts(self):
        return self._workouts

    def exercises(self):
        return self._exercises

    def load_exercises(self):
        with open("resources/exercises.json") as workouts:
            # Read workouts from json file
            workout_data = loads(workouts.read())["workouts"]
            self._workouts = list(
                map(
                    lambda workout: Choice(name=workout, value=workout),
                    workout_data.keys(),
                )
            )
            self._exercises = workout_data

    def update_user_set(
        self,
        member: Union[Member, User],
        exercise: str,
        reps: int,
        weights: int,
        note: str = "",
    ) -> bool:
        """Exercise must be a valid name. Returns true if the set is a personal record."""
        # Users should all exist, but just in case...
        self.check_db_for(member.id, member.global_name)
        # userstats.json ::
        # users: [ "id": {"name": ..., "top_stats":[...], "progression":[...]}}, ... ]
        with open("resources/userstats.json", "r+") as user_stats:
            stats_json = loads(user_stats.read())

            user_data = stats_json[str(member.id)]
            date_today = datetime.now().strftime(r"%Y/%m/%d")
            # generate entry for today
            if not date_today in user_data["progression"]:
                user_data["progression"][date_today] = {}
            # add exercise to today
            user_data["progression"][date_today][exercise] = {
                "reps": reps,
                "weight": weights,
                "note": note,
            }
            # check if personal best
            # best is determined by reps * weights atm
            record = (
                True
                if exercise not in user_data["personal_best"]
                or user_data["personal_best"][exercise]["weight"] * user_data["personal_best"][exercise]["reps"] < weights * reps
                else False
            )
            if record:
                # Update personal best
                user_data["personal_best"][exercise] = {
                    "date": date_today,
                    "reps": reps,
                    "weight": weights,
                    "note": note,
                }
            # update stats
            user_stats.seek(0)
            stats_json[str(member.id)] = user_data
            user_stats.write(dumps(stats_json))
            # If the new file is shorter than the old one
            user_stats.truncate()
            return record

    def check_db_for(self, user_id: int, name: str) -> bool:
        """Checks database for user."""
        with open("resources/userstats.json", "r+") as userstats:
            stats_json = loads(userstats.read())
            if str(user_id) in stats_json:
                return True
            # Create new user
            stats_json[str(user_id)] = {
                "name": name,
                "personal_best": {},
                "progression": {},
            }
            # update stats
            userstats.seek(0)
            userstats.write(dumps(stats_json))
            # If the new file is shorter than the old one
            userstats.truncate()
        return False

    def get_pb(
        self, member: Union[Member, User], exercise: str
    ) -> Union[Dict[str, Any], None]:
        """Returns dictionary if user is else None"""
        # Add user to db if not in db
        if not self.check_db_for(member.id, member.global_name):
            # User not in db, fat prick
            return None

        data = None
        with open("resources/userstats.json", "r") as user_stats:
            stats_json = loads(user_stats.read())
            user_data = stats_json[str(member.id)]
            if exercise in user_data["personal_best"]:
                data = user_data["personal_best"][exercise]
        return data

    def has_channel(self, member: Member) -> bool:
        ret = False
        with open("resources/userbulkchannels.json", "r") as channels:
            users = loads(channels.read())
            ret = str(member.id) in users
        return ret

    def add_channel(self, member: Member, channel_id: int):
        """Assumes user has no channel"""
        with open("resources/userbulkchannels.json", "r+") as channels:
            users = loads(channels.read())
            users[str(member.id)] = channel_id
            # update file
            channels.seek(0)
            channels.write(dumps(users))
            # If the new file is shorter than the old one
            channels.truncate()

    def leaderboard(self, server: Guild, exercise: str, entries: int = 3) -> Dict[Member, Any]:
        # print(server.members)
        server_members = server.members
        top_records = {}
        with open("resources/userstats.json", "r") as channels:
            users = loads(channels.read())
            for user_id in users.keys():
                user = list(filter(lambda member: member.id == int(user_id), server_members))
                if len(user) == 0:
                    # No user found (Example user will not be found)
                    continue
                user = user[0]
                if exercise in users[user_id]["personal_best"]:
                    top_records[user] = users[user_id]["personal_best"][exercise] 
        # Sort dict in greatest to least based on reps * weight
        top_records = dict(list(sorted(top_records.items(), key=lambda item: item[1]["reps"] * item[1]["weight"], reverse=True))[:entries])
        return top_records
    
    def history_of(self, member: Member, days_limit: int = 20) -> Dict[str, Dict[str, Dict[str, Union[str, int]]]]:
        self.check_db_for(member.id, member.name)
        history = {}
        with open("resources/userstats.json", "r") as channels:
            users = loads(channels.read())
            # History of last days_limit days
            dates = list(users[str(member.id)]["progression"].items())[:days_limit]
            dates.reverse()
            history = dict(dates)
        return history


        
BULKER = Bulker()

class FennsBulking(commands.Cog):
    def __init__(self, bot: FennsBot) -> None:
        super().__init__()
        self.bot = bot
        self.bulkers_guild_id = 1172288447592022146
        self.user_channels_category_id = 1172359070917853196

    async def bulk_set_autocomplete(
        self, interaction: Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        workout = interaction.namespace.workout
        # Filters out options that don't start with 'current'
        autocomplete = list(
            map(
                lambda exercise: Choice(name=exercise["name"], value=exercise["name"]),
                filter(
                    lambda exercise: True
                    if current == exercise["name"][: len(current)]
                    else False,
                    BULKER.exercises()[workout],
                ),
            )
        )[:25]
        return autocomplete

    @app_commands.command(name="set", description="Records an exercise")
    @app_commands.describe(
        workout="Class of exercise",
        exercise="Exersize to update",
        reps="Number of reps per set",
        weight="Weight amount",
        note="Optional information for entry",
    )
    @app_commands.choices(workout=BULKER.workouts())
    @app_commands.autocomplete(exercise=bulk_set_autocomplete)
    async def add_bulk_set(
        self,
        interaction: Interaction,
        workout: Choice[str],
        exercise: str,
        reps: int,
        weight: int,
        note: Union[str, None],
    ):
        """Records an exercise the user has completed in the database"""
        # BULKER.exercises()[workout.name] is a list of choices
        if exercise not in [exer["name"] for exer in BULKER.exercises()[workout.name]]:
            # Invalid exercise
            await self.bot.send_failure(interaction, "set", exercise)
            return

        record = BULKER.update_user_set(
            interaction.user,
            exercise,
            reps,
            weight,
            note=note if type(note) == str else "",
        )
        # Embed generation
        embed, png = self.bot.fenns_embed(FennsIcon.BULKING)
        embed.set_author(name="Recorded Set!", icon_url=interaction.user.display_avatar)
        embed.add_field(
            name=exercise.capitalize(), value=f"{REP_EMOJI} **{reps}**{REPS}\n{WEIGHT_EMOJI} **{weight}**lbs"
        )
        if note != None:
            embed.description = f'"*{note}*"'
        if record:
            embed.set_footer(
                text=f"🎉 {interaction.user.display_name} set a new personal best! 🎉"
            )
        await interaction.response.send_message(embed=embed, file=png)

    @app_commands.command(
        name="list", description="Lists exercises part of a given workout"
    )
    @app_commands.describe(workout="Class of exercise")
    @app_commands.choices(workout=BULKER.workouts())
    async def list_bulks(self, interaction: Interaction, workout: Choice[str]):
        """Lists exercises part of a given workout."""
        # Embed generation
        embed, png = self.bot.fenns_embed(FennsIcon.BULKING)
        embed.title = f"Workouts: {workout.name.capitalize()}"
        for exercise in BULKER.exercises()[workout.name]:
            info = f"**Sets**: {exercise['sets']}.\n**Reps**: {exercise['reps']}."
            if "meta" in exercise:
                # Add additional metadata
                info += f"\n**Extra info**: __{exercise['meta']}__"
            embed.add_field(name=f"__{exercise['name'].capitalize()}__", value=info)
        embed.color = Colour.purple()
        # response might take longer to send
        await interaction.response.defer()
        await interaction.followup.send(embed=embed, file=png)

    async def pb_autocompete(self, interaction: Interaction, current: str):
        # Compile all exercises
        all_exercises = []
        for exercises in BULKER.exercises().values():
            all_exercises += exercises
        # Filters out options that don't start with 'current'
        autocomplete = list(
            map(
                lambda exercise: Choice(name=exercise["name"], value=exercise["name"]),
                filter(
                    lambda exercise: True
                    if current == exercise["name"][: len(current)]
                    else False,
                    all_exercises,
                ),
            )
        )[:25]
        return autocomplete

    @app_commands.command(name="best", description="List personal best")
    @app_commands.describe(exercise="Name of exercise", member="Check a specific member's stats")
    @app_commands.autocomplete(exercise=pb_autocompete)
    async def send_pb(self, interaction: Interaction, exercise: str, member: Union[Member, None]):
        target_member = interaction.user if member == None else member
        # Compile all exercises
        all_exercises = []
        for exercises in BULKER.exercises().values():
            all_exercises += [exercise["name"] for exercise in exercises]
        # Check if exercise is valid
        if exercise not in all_exercises:
            # Invalid exercise
            await self.bot.send_failure(interaction, "best", exercise)
            return
        # Get pb
        best = BULKER.get_pb(target_member, exercise)
        embed, png = self.bot.fenns_embed(FennsIcon.BULKING)
        embed.set_author(name="Personal Best!", icon_url=target_member.display_avatar)
        embed.title = exercise.capitalize()
        if best == None:
            # No record! User is chungus!
            embed.add_field(name="No records found!", value="Lmao!")
        else:
            # User has record
            info = (
                f"Date: {best['date']}\nReps: {best['reps']}\nWeight: {best['weight']}"
            )
            if best["note"] != "":
                info += f"\nAuthor's Note: *{best['note']}*"
            embed.add_field(name="__Info__", value=info)

        await interaction.response.send_message(embed=embed, file=png)

    @commands.Cog.listener(name="on_raw_reaction_add")
    async def create_user_bulk_channel(self, payload: RawReactionActionEvent):
        # 'user' will be type Member if in guild, User in DMs
        guild: Guild = self.bot.get_guild(self.bulkers_guild_id)
        if (
            payload.message_id == self.bot.reaction_listeners[0]
            and payload.event_type == "REACTION_ADD"
        ):
            if not BULKER.has_channel(payload.member):
                permissions = {
                    payload.member: PermissionOverwrite(send_messages=True),
                    guild.default_role: PermissionOverwrite(send_messages=False),
                }
                new_channel = await guild.create_text_channel(
                    f"Mog Log {payload.member.display_name}",
                    reason="User requested their channel",
                    category=guild.get_channel(self.user_channels_category_id),
                    overwrites=permissions,
                    # Tightrosspants teehee
                    nsfw=True if payload.member.id == 498175715993190421 else False,
                )
                BULKER.add_channel(
                    payload.member,
                    new_channel.id
                )
                # Give user bulker role
                bulker = [r for r in guild.roles if r.name == "Bulker"][0]
                await payload.member.add_roles(bulker)
    
    @app_commands.command(name="leaderboard", description="List bulking leaderboard")
    @app_commands.describe(workout="Name of workout")
    @app_commands.choices(workout=BULKER.workouts())
    async def leaderboard(self, interaction: Interaction, workout: Choice[str], verbose: Union[bool, None]):
        # Embed generation
        embed, png = self.bot.fenns_embed(FennsIcon.BULKING)
        workouts = {
            "push":":muscle:",
            "pull":":raised_hands:",
            "legs":":leg:"
        }
        embed.title = f"Leaderboard「 {workouts[workout.name]} 」{workout.name.capitalize()}"
        for exercise in BULKER.exercises()[workout.name]:
            exercise = exercise["name"]
            info = ""   
            # Build top members for exercise
            emojis = {
                1: ":first_place:",
                2: ":second_place:",
                3: ":third_place:"
            }
            for i, (member, stats) in enumerate(BULKER.leaderboard(self.bot.get_guild(self.bulkers_guild_id), exercise).items()):
                info += f"{emojis[i + 1]} †{member.display_name}†\n"
                if verbose:
                    # Display all info
                    info += f"- {CLOCK_EMOJI} *{stats['date']}*\n- {REP_EMOJI} *× **{stats['reps']}**{REPS}*\n- {WEIGHT_EMOJI} ***{stats['weight']}** lbs*\n"
                    if stats["note"] != "":
                        info += f"> *{stats['note']}*\n"
                    info += "\n"
                else:
                    # Display most info
                    info += f"- {WEIGHT_EMOJI} ***{stats['reps']}**{REPS} × **{stats['weight']}** lbs*\n"
            embed.add_field(name=f"**{exercise.capitalize()}**", value=info)
        # response might take longer to send
        await interaction.response.defer()
        await interaction.followup.send(embed=embed, file=png)

    @app_commands.command(name="history", description="View user history")
    async def history(self, interaction: Interaction):
        embeds = []
        for date, exercises in BULKER.history_of(interaction.user).items():
            embed, png = self.bot.fenns_embed(FennsIcon.BULKING)
            embed.set_author(name=date, icon_url=interaction.user.display_avatar)
            for exercise, stats in exercises.items():
                info = f"- {WEIGHT_EMOJI}***{stats['reps']}**{REPS} × **{stats['weight']}** lbs*\n"
                if stats["note"] != "":
                    info += f"> *{stats['note']}*\n"
                info += "\n"
                embed.add_field(name=exercise.capitalize(), value=info)
            embeds.append(embed)
        await interaction.response.send_message(embed=embeds[0], file=png, view=EmbedBook(embeds))

async def setup(bot: commands.Bot):
    await bot.add_cog(FennsBulking(bot))
