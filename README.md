# Discord bot
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

###### Slash Commands
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
```
