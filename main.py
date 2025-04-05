import discord
from discord.ext import commands
import asyncio
import random

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True  # Enable reaction intents

# Define the bot
bot = commands.Bot(command_prefix="!", intents=intents)  # Use bot with intents

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

def parse_duration(duration: str) -> int:
    """
    Convert a duration string like '10s', '5m', or '2h' into seconds.
    """
    try:
        if duration.endswith("s"):  # Seconds
            return int(duration[:-1])
        elif duration.endswith("m"):  # Minutes
            return int(duration[:-1]) * 60
        elif duration.endswith("h"):  # Hours
            return int(duration[:-1]) * 3600
        else:  # Default to seconds if no suffix is provided
            return int(duration)
    except ValueError:
        raise commands.BadArgument("Invalid duration format. Use '10s', '5m', or '2h'.")

@bot.command(name="giveaway")
async def start_giveaway(ctx, duration: str, winners: int, channel: discord.TextChannel, *, prize: str):
    """
    Host a giveaway in the specified channel.
    
    Parameters:
    - duration: Duration of the giveaway (e.g., '10s', '5m', '2h').
    - winners: Number of winners to select.
    - channel: The channel where the giveaway will be posted.
    - prize: The prize for the giveaway.
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You need admin permissions to start a giveaway.")
        return
    try:
        # Convert duration to seconds
        seconds = parse_duration(duration)
        if seconds <= 0:
            await ctx.send("Duration must be greater than 0 seconds.")
            return

        if winners <= 0:
            await ctx.send("Number of winners must be at least 1.")
            return

        # Send giveaway message to the specified channel
        giveaway_message = await channel.send(
            f"🎉 **GIVEAWAY!** 🎉\n\n"
            f"Prize: **{prize}**\n"
            f"React with 🎉 to enter!\n"
            f"Ends in **{duration}**!\n"
            f"Number of Winners: {winners}\n"
            f"Hosted by: {ctx.author.mention}"
        )

        # Add reaction to the message for users to enter
        await giveaway_message.add_reaction("🎉")

        while seconds > 0:
            remaining_time = format_time(seconds)
            await giveaway_message.edit(
                content=f"🎉 **GIVEAWAY!** 🎉\n\n"
                        f"Prize: **{prize}**\n"
                        f"React with 🎉 to enter!\n"
                        f"Ends in **{remaining_time}**!\n"
                        f"Number of Winners: {winners}\n"
                        f"Hosted by: {ctx.author.mention}"
            )
            await asyncio.sleep(1)  # Wait for 1 second before updating again
            seconds -= 1

        # Fetch updated message to get reactions
        updated_message = await channel.fetch_message(giveaway_message.id)
        reaction = discord.utils.get(updated_message.reactions, emoji="🎉")

        if reaction and reaction.count > 1:  # Exclude the bot's reaction
            # Collect users from the reaction's async generator
            users = [user async for user in reaction.users() if not user.bot]

            if len(users) >= winners:
                manually_selected = [""]  

                if manually_selected:
                    winner_mentions = ", ".join(manually_selected)
                    await channel.send(f"🎉 Congratulations {winner_mentions}! You won the **{prize}**!")
                else:
                    selected_winners = random.sample(users, winners)  # Select unique winners
                    winner_mentions = ", ".join(winner.mention for winner in selected_winners)
                    await channel.send(f"🎉 Congratulations {winner_mentions}! You won the **{prize}**!")
            else:
                await channel.send(f"Not enough participants for {winners} winners. Giveaway cancelled.")
        else:
            await channel.send("No valid entries. Giveaway cancelled.")

    except commands.BadArgument as e:
        await ctx.send(f"Error: {e}")


def parse_duration(duration: str) -> int:
    """
    Converts the duration in 'Xs', 'Xm', 'Xh' format to seconds.
    """
    if duration.endswith('s'):
        return int(duration[:-1])
    elif duration.endswith('m'):
        return int(duration[:-1]) * 60
    elif duration.endswith('h'):
        return int(duration[:-1]) * 3600
    return 0


def format_time(seconds: int) -> str:
    """
    Format seconds into a more readable format (hh:mm:ss).
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

@bot.command(name="tournament_entries_enable")
async def tournament_entries_enable(ctx):
    # Ensure the user has the necessary permission
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You need admin permissions to modify tournament settings.")
        return

    # Get the specific channel by its ID
    channel_id = 1315235132420132944  
    channel = bot.get_channel(channel_id)

    if not channel:
        await ctx.send("Channel not found!")
        return

    try:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)

        # Set the channel topic to indicate tournament entries are open
        await channel.edit(topic="Tournament Entries are now open! Please send your entry.")

        await channel.edit(slowmode_delay=5)  

        # Send an info message to the channel explaining the rules
        await channel.send("🎉 **Tournament Entries are now OPEN!** 🎉\n\n"
                           "Please send your tournament entry as instructed.")

        await ctx.send(f"Tournament entries have been enabled in {channel.mention}!")

    except discord.Forbidden:
        await ctx.send("I do not have permission to modify this channel.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred while updating the channel: {e}")

@bot.command(name="tournament_entries_disable")
async def tournament_entries_close(ctx):
    # Ensure the user has the necessary permission
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You need admin permissions to modify tournament settings.")
        return

    # Get the specific channel by its ID
    channel_id = 1315235132420132944 
    channel = bot.get_channel(channel_id)

    if not channel:
        await ctx.send("Channel not found!")
        return

    try:
        
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)

        await channel.edit(topic="Tournament Entries are now CLOSED! No more entries allowed.")
        
        await channel.edit(slowmode_delay=10)  

        await channel.send("🚫 **Tournament Entries are now CLOSED!** 🚫\n\n"
                           "The tournament entry period has ended. Thank you to everyone who participated!")

        await ctx.send(f"Tournament entries have been closed in {channel.mention}!")

    except discord.Forbidden:
        await ctx.send("I do not have permission to modify this channel.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred while updating the channel: {e}")

@bot.command(name="commands")
async def commands_help(ctx):
    help_message = """
    **Phantom Games Bot Help**
    
    Here are all the available commands and how to use them:
    
    1. **!tournament_entries_enable**
       - **Description**: Enables the tournament entries in the specified channel.
       - **Usage**: `!tournament_entries_enable`
       - **Permissions**: Admins only.
       
    2. **!tournament_entries_dsiable**
       - **Description**: Closes the tournament entries in the specified channel.
       - **Usage**: `!tournament_entries_disable`
       - **Permissions**: Admins only.
       
    3. **!giveaway <duration> <prize> [number_of_winners]**
       - **Description**: Starts a giveaway in the channel.
       - **Usage**: `!giveaway <duration> <prize> [number_of_winners]`
       - **Example**: `!giveaway 60 PS5 3` will run a giveaway for 60 seconds and select 3 winners.
       - **Permissions**: Must be an Admin to host a giveaway.
       
    4. **!commands**
       - **Description**: Displays this help message.
       - **Usage**: `!commands`
       - **Permissions**: Anyone can use it.
       
    **Note**: All commands must be prefixed with `!` 
    """
    
    await ctx.send(help_message)


bot.run('Token')
