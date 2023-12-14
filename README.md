# Fenn bot
By Theriales

### Cool features

###### Autocompletion
```py
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
```

###### Slash commands with Cogs
```py
class FennsBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(intents=intents, command_prefix="f!")
        # generate a dict of filename: extension for fenn's icon files
        self.icon_files = {fname[0].lower(): fname[1] for fname in list(map(lambda f: f.split("."), listdir("resources/thumbnails")))}
        self.owner_id = 283677434476363776
        self.reaction_listeners = [1173735486578245744] # Message id's the bot should listen to
        # self.openai_client = AsyncOpenAI()

    async def on_ready(self):
        print(f"{self.user} is up and running!")

    async def on_message(self, message: discord.Message):
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
```

###### Slash Command Example
```py
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
...
```
