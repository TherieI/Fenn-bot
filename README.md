# Fenn bot
Something to manage niche things on discord. This bot leverages slash commands built using `discord.py`'s cog system, which is something I haven't really seen from other projects at first inspection.

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
# ... Imports ...

class FennsBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(intents=intents, command_prefix="f!")
        # ...

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

async def main():
    bot = FennsBot(intents=intents)
    await bot.start(os_env["DISCORD_TOKEN"])

if __name__ == "__main__":
    asyncio.run(main())
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
