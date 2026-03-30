import discord
from discord.ui import Button, View
from discord.ext  import commands
import logging
from dotenv import load_dotenv
import os
from datetime import datetime
import tkinter 
import random
import webserver
 

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="*", intents=intents, help_command=None)
banned_words = [""]
server_role = "Gamer"


@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")


@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    for banned_word in banned_words:
        if banned_word in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention} - that word isn't allowed")
            await message.channel.timeout()

    

    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
async def help(ctx):
    commands_list = [
        ("hello", "Greets the user."),
        ("list_commands", "Shows this list of commands."),
        ("assign [role] [user]", "Assigns a role to you (requires permission)."),
        ("remove [role] [user]", "Removes a role from you (requires permission)."),
        ("list_roles", "Lists all server roles."),
        ("secret", f"Access restricted to users with the '{server_role}' role."),
        ("dm [message]", "DMs you the message."),
        ("poll [question]", "Creates a simple thumbs-up/down poll."),
        ("avatar", "Displays your avatar."),
        ("date", "Displays today's date."),
        ("servercount", "Displays the number of members in the server."),
        ("serverinfo", "Displays server information."),
        ("flip", "Flips a coin (Heads or Tails)."),
        ("random_number", "Pick a number from 1 - 100."),
        ("tictactoe @user1 @user2", "Starts a game of Tic-Tac-Toe.")
    ]

    embed = discord.Embed(
        title="📜 Bot Commands List",
        description="Here are all the available commands:",
        color=discord.Color.green()
    )

    for cmd_name, cmd_desc in commands_list:
        embed.add_field(name=f"`*{cmd_name}`", value=cmd_desc, inline=False)

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_roles=True)  
async def assign(ctx, *, role_name: str):
    roles = ctx.guild.roles  
    target_role = discord.utils.get(roles, name=role_name)

    if not target_role:
        await ctx.send(f"❌ Role '{role_name}' does not exist.")
        return

    # Check if the bot can assign this role
    if target_role >= ctx.guild.me.top_role:
        await ctx.send("⚠️ I don't have permission to assign that role.")
        return
    
    await ctx.author.add_roles(target_role)
    await ctx.send(f"✅ {ctx.author.mention} has been assigned the role '{target_role.name}'.")


@bot.command()
@commands.has_permissions(manage_roles=True)  
async def remove(ctx, user: discord.Member = None, *, role_name: str = None, ):

    if user is None:
        await ctx.send("You need to specify a user")
    
    if role_name is None:
        await ctx.send("You need to specify the role name")

    roles = ctx.guild.roles  
    target_role = discord.utils.get(roles, name=role_name)

    if not target_role:
        await ctx.send(f"Role doesn't exist")
        return
    
    if target_role not in user.roles:
        await ctx.send(f"⚠️ {user.mention} doesn't have the '{role_name}' role.")
        return 
    
    try:
        await user.remove_roles(target_role)
        await ctx.send(f"✅ Removed role '{role_name}' from {user.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ I do not have permission to remove that role.")
    except Exception as e:
        await ctx.send(f"⚠️ An error occurred: {e}")



@bot.command()
@commands.has_permissions(manage_roles=True)  
async def list_roles(ctx):
    roles = ctx.guild.roles  
    role_names = [role.name for role in roles if role.name != "@everyone"]

    if role_names:
        role_list = "\n".join(role_names)
        embed = discord.Embed(
            title="📜 Server Roles",
            description=role_list,
            color=discord.Color.yellow()
        )
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    else:
        await ctx.send("No roles found in this server.")

@bot.command()
@commands.has_role(server_role)
async def secret(ctx):
    await ctx.send(f"Welcome there {ctx.author.mention} you have the {server_role} role")



@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said {msg}")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = None):
    if amount is None:
        await ctx.send("❌ You need to specify how many messages to delete.")
        return

    if amount <= 0:
        await ctx.send("❌ Amount must be greater than 0.")
        return

    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared {amount} messages!", delete_after=5)  # Optional: auto-delete this message


    

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(
        title=f"New Poll by {ctx.author.display_name}",
        description=question,
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

@bot.command()
async def avatar(ctx, user: discord.Member = None):
    target = user or ctx.author  # Use mentioned user if provided, else default to command author
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    embed = discord.Embed(
        title=f"{target.display_name}'s Avatar",
        description=f"Requested on {now}",
        color=discord.Color.blue()
    )
    embed.set_image(url=target.display_avatar.url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

    message = await ctx.send(embed=embed)
    await message.add_reaction("👍")
    await message.add_reaction("👎")

@bot.command()
async def date(ctx):
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")  # Example: June 18, 2025 at 01:12 AM

    embed = discord.Embed(
        title="📅 Today's Date & Time",
        description=f"The current date and time is:\n**{now}**",
        color=discord.Color.orange()
    )

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)



@bot.command()
@commands.has_permissions(manage_roles=True)
async def servercount(ctx):
    members = ctx.guild.member_count
    await ctx.send(f"Total number of people in this server is {members}")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def ban(ctx, *, banned : discord.Member):

    guild = ctx.guild

    owner = guild.owner
    if ctx.author != owner:
        await ctx.send(f"Only the owner has ban permissions")
        return
    
    try:
        await banned.ban(reason=f"Banned by the owner {ctx.author}")
        await ctx.send(f"✅ {banned.mention} has been banned by the server owner.")
    except discord.Forbidden:
        await ctx.send("❌ I do not have permission to ban this user.")
    except Exception as e:
        await ctx.send(f"⚠️ An error occurred: {str(e)}")


@bot.command()
@commands.has_permissions(ban_members=True)
async def banned(ctx):
    if ctx.author != ctx.guild.owner:
        await ctx.send("❌ Only the **server owner** can view the ban list.")
        return

    bans = await ctx.guild.bans()
    
    if not bans:
        await ctx.send("✅ No users are currently banned.")
        return

    pretty_list = ["• {0.id} ({0.name}#{0.discriminator})".format(entry.user) for entry in bans]
    await ctx.send("**Ban list:**\n{}".format("\n".join(pretty_list)))




@bot.command()
@commands.has_permissions(manage_roles=True)
async def serverinfo(ctx):
    guild = ctx.guild
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    members = guild.member_count
    roles = [role.name for role in guild.roles if role.name != "@everyone"]
    role_list = ", ".join(roles) if roles else "No custom roles."

    embed = discord.Embed(
        title=f"📊 Server Info - {guild.name}",
        description=f"Information as of {now}",
        color=discord.Color.dark_blue()
    )

    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="👑 Server Owner", value=str(guild.owner), inline=False)
    embed.add_field(name="👥 Member Count", value=str(members), inline=False)
    embed.add_field(name=f"📜 Roles ({len(roles)})", value=role_list, inline=False)
    embed.add_field(name="Created at", value=guild.created_at.strftime("%B %d, %Y"))

    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def flip(ctx):
    sides = ["Heads", "Tails"]
    

    selection = random.choice(sides)
    await ctx.send(f"You landed on {selection}")
    
@bot.command()
@commands.has_permissions(manage_roles=True)
async def random_number(ctx):
    

    selection = random.randint(1, 100)
    await ctx.send(f"Random number is {selection}")




class InviteButtons(discord.ui.View):
    def __init__(self, inv: str):
        super().__init__()
        self.inv = inv
        self.add_item(discord.ui.Button(label="Invite link", url=self.inv))

    @discord.ui.button(label="Invite Button", style=discord.ButtonStyle.green)
    async def tictactoeBtn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(self.inv, ephemeral=True)

@bot.command()
async def invite(ctx: commands.Context):
    inv = await ctx.channel.create_invite()

    embed = discord.Embed(
        title="Click the button below to invite someone!",
        description="",
        color=discord.Color.green()
    )
    view = InviteButtons(str(inv))

    embed.add_field(name=f"Have a good day", value="", inline=False)


    await ctx.send(embed=embed, view=view)





class TicButton(discord.ui.Button):
    def __init__(self, index):
        super().__init__(
            style=discord.ButtonStyle.grey,
            label="⬜",
            row=index // 3
        )
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        # Only allow current turn player to click
        if interaction.user != self.view.current_turn:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        # Update the board state
        if self.view.current_turn == self.view.players[0]:
            self.label = self.view.labels[0]  # ❌
            self.view.board[self.index] = self.view.labels[0]
        else:
            self.label = self.view.labels[1]  # ⭕
            self.view.board[self.index] = self.view.labels[1]

        self.disabled = True

        # Check for win
        result = check_winner(self.view.board, self.label)

        if result == "win":
            self.view.disable_all_items()
            await interaction.response.edit_message(view=self.view)
            await interaction.followup.send(f"🎉 {interaction.user.mention} wins! Game over.", ephemeral=False)
            return

        elif result == "draw":
            self.view.disable_all_items()
            await interaction.response.edit_message(view=self.view)
            await interaction.followup.send("🤝 It's a draw! No more moves left.", ephemeral=False)
            return


        # Switch turn
        self.view.current_turn = (
            self.view.players[1]
            if self.view.current_turn == self.view.players[0]
            else self.view.players[0]
        )

        # Update message
        await interaction.response.edit_message(view=self.view)
        await interaction.followup.send(
            f"{self.view.current_turn.mention}, it's your turn!", ephemeral=False
        )

class Board(discord.ui.View):
    def __init__(self, players, labels, current_turn):
        super().__init__(timeout=None)
        self.players = players
        self.labels = labels
        self.current_turn = current_turn
        self.board = ["⬜"] * 9  # 3x3 board

        for i in range(9):
            self.add_item(TicButton(i))

    def disable_all_items(self):
        for item in self.children:
            item.disabled = True


def check_winner(board, mark):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]

    for condition in win_conditions:
        if all(board[i] == mark for i in condition):
            return "win"

    if all(cell != "⬜" for cell in board):
        return "draw"

    return None


@bot.command()
async def tictactoe(ctx, p2: discord.Member = None):
    if p2 is None:
        await ctx.send("You need to tag a friend to play")
        return

    players = (ctx.author, p2)
    labels = ("❌", "⭕")
    current_turn = random.choice(players)

    view = Board(players=players, labels=labels, current_turn=current_turn)
    await ctx.send(f"🎮 Tic-Tac-Toe started by {ctx.author.mention} with {p2.mention}!", view=view)
    await ctx.send(f"🕹️ It's {current_turn.mention}'s turn!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ You missed a required argument for this command.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You don’t have permission to use this command.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ That command doesn't exist. Use `*help` to see all available commands.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("⚠️ Invalid argument provided.")
    elif isinstance(error, commands.UserInputError):
        await ctx.send("❌ There was an error with your command input. Check your syntax.")
    else:
       
        await ctx.send("⚠️ An unexpected error occurred.")
        raise error  

webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)

