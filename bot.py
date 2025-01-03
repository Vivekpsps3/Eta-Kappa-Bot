import discord
from discord.ext import commands
from discord.ui import Button, View

import requests
import json
import chess

from src import chatbot as Chatbot

# Gemini chatbot
gbot = Chatbot.gemini()

with open ("secrets.env", "r") as file:
    token = file.read()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='-', intents=intents)
board = chess.Board()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Sync commands with Discord
    await bot.tree.sync()

#ping check command
@bot.tree.command(name="ping", description="Replies with Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.defer()

    await interaction.followup.send_message("Pong!") 

@bot.tree.command(name="sharky", description="Ask Sharky a question")
async def sharky(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    
    url = 'http://10.0.0.136:11434/api/generate'
    with open("system.txt", "r") as file:
        system = file.read()
    
    payload = {
        'model': 'llama3.2:latest',
        'system': system,
        'prompt': f"Q: {question}\nA:",
        'stream': True,
    }
    
    response = requests.post(url, json=payload, stream=True)
    
    # Initialize variables for streaming
    current_message = ""
    temp_buffer = ""
    message = None
    
    for line in response.iter_lines():
        if line:
            json_response = json.loads(line)
            if 'response' in json_response:
                temp_buffer += json_response['response']
                
                # Update message every 20 characters
                if len(temp_buffer) >= 20:
                    current_message += temp_buffer
                    temp_buffer = ""
                    
                    # Ensure message length doesn't exceed Discord's limit
                    if len(current_message) > 1999:
                        current_message = current_message[:1999]
                        break
                    
                    # Edit existing message or send first message
                    if message:
                        await message.edit(content=current_message)
                    else:
                        message = await interaction.followup.send(current_message)
    
    # Send any remaining characters and final message
    if temp_buffer:
        current_message += temp_buffer
        if len(current_message) > 1999:
            current_message = current_message[:1999]
        if message:
            await message.edit(content=current_message)
        else:
            await interaction.followup.send(current_message)

@bot.tree.command(name="smarty", description="Ask Smart Sharky a question")
async def smarty(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    
    url = 'http://10.0.0.136:11434/api/generate'
    with open("system.txt", "r") as file:
        system = file.read()
    
    payload = {
        'model': 'solar:latest',
        'system': system,
        'prompt': f"Q: {question}\nA:",
        'stream': True,
    }
    
    response = requests.post(url, json=payload, stream=True)
    
    # Initialize variables for streaming
    current_message = ""
    temp_buffer = ""
    messages = []
    
    for line in response.iter_lines():
        if line:
            json_response = json.loads(line)
            if 'response' in json_response:
                temp_buffer += json_response['response']
                
                # Update message every 20 characters
                if len(temp_buffer) >= 20:
                    current_message += temp_buffer
                    temp_buffer = ""
                    
                    # If current message exceeds Discord's limit, start a new message
                    if len(current_message) > 1999:
                        # Send or update the current message
                        if messages:
                            await messages[-1].edit(content=current_message[:1999])
                        else:
                            messages.append(await interaction.followup.send(current_message[:1999]))
                        
                        # Start a new message with the overflow
                        current_message = current_message[1999:]
                        messages.append(await interaction.followup.send(current_message))
                    else:
                        # Update or send the current message
                        if messages:
                            await messages[-1].edit(content=current_message)
                        else:
                            messages.append(await interaction.followup.send(current_message))
    
    # Handle any remaining content
    if temp_buffer:
        current_message += temp_buffer
        if len(current_message) > 1999:
            if messages:
                await messages[-1].edit(content=current_message[:1999])
                messages.append(await interaction.followup.send(current_message[1999:]))
            else:
                messages.append(await interaction.followup.send(current_message[:1999]))
                messages.append(await interaction.followup.send(current_message[1999:]))
        else:
            if messages:
                await messages[-1].edit(content=current_message)
            else:
                messages.append(await interaction.followup.send(current_message))
import chess

@bot.tree.command(name='gemini', description="Uses Gemini to come up with a response")
async def gemini(ctx, *, text: str):
    """Uses Gemini to come up with a response."""
    await ctx.response.defer()
    global gbot
    output = gbot.request(text)
    if len(output) > 2000:
        for i in range(0, len(output), 2000):
            await ctx.followup.send(output[i:i+2000])
    else:
        await ctx.followup.send(output)

@bot.tree.command(name='gchat', description="Uses Gemini to chat with the bot")
async def gchat(ctx, *, text: str):
    """Uses Gemini to chat with the bot."""
    await ctx.response.defer()
    global gbot
    output = gbot.chat(text)
    if len(output) > 2000:
        for i in range(0, len(output), 2000):
            await ctx.followup.send(output[i:i+2000])
    else:
        await ctx.followup.send(output)

@bot.tree.command(name='gclear', description="Clears the Gemini chat history")
async def gclear(ctx):
    """Clears the Gemini chat history."""
    global gbot
    gbot.clear()
    await ctx.response.send_message("Chat history cleared.")

@bot.tree.command(name='new_chess', description="Restart or start a new game of chess")
async def new_chess(ctx):
    """Starts a new game of chess with the user via print statements."""
    global board
    board = chess.Board()
    await ctx.response.send_message(
        "Welcome to text-based chess! In order to make a move, use standard algebraic notation (e.g., e2e4, Nf3, O-O).\n"
        "To make a move, type the move in the chat. For example, to move a pawn from e2 to e4, type 'e2e4'.\n"
        f"```{board}```"
    )

@bot.tree.command(name='show', description="Show the current board state")
async def show(ctx):
    """Shows the current board state."""
    await ctx.response.defer()
    global board
    if board.turn == chess.WHITE:
        await ctx.followup.send("White to move:")
    else:
        await ctx.followup.send("Black to move:")
    await ctx.followup.send(f"```{board}```")

@bot.tree.command(name='move', description="Make a move in the current game of chess")
async def move(ctx, move_str: str):
    """Makes a move in the current game of chess with the user via print statements."""
    global board
    move = chess.Move.from_uci(move_str)
    response_message = ""
    
    if move not in board.legal_moves:
        response_message = "Invalid move. Please use standard algebraic notation (e.g., e2e4, Nf3, O-O)."
    else:
        board.push(move)
        response_message = f"```{board}```\n"
        
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                response_message += "Checkmate! Black wins."
            else:
                response_message += "Checkmate! White wins."
        elif board.is_stalemate():
            response_message += "Stalemate! It's a draw."
        elif board.is_insufficient_material():
            response_message += "Insufficient material! It's a draw."
        elif board.is_seventyfive_moves():
            response_message += "75-moves rule! It's a draw."
        elif board.is_fivefold_repetition():
            response_message += "Fivefold repetition! It's a draw."
        else:
            response_message += "Move successful."
    
    await ctx.response.send_message(response_message)

@bot.tree.command(name='stockfish', description="Play Stockfish's move as the next move")
async def stockfish(ctx):
    """Get the best move from Stockfish."""
    global board
    await ctx.response.defer()
    import chess.engine
    engine = chess.engine.SimpleEngine.popen_uci("stockfish")
    result = engine.play(board, chess.engine.Limit(time=1))
    engine.quit()
    board.push(result.move)
    await ctx.followup.send(f"```{board}```")

@bot.tree.command(name="list_members", description="List members based on role conditions with confirmation.")
async def list_members(interaction: discord.Interaction, role_condition: str = "@everyone"):
    """
    Lists members based on role conditions with confirmation.
    Args:
        interaction (discord.Interaction): The interaction object representing the command invocation.
        role_condition (str, optional): The role condition to filter members by. Defaults to "@everyone".
    Returns:
        None: This function sends messages to the interaction response and does not return any value.
    Raises:
        None: This function does not raise any exceptions.
    Notes:
        - Only members with the "HKN Exec Comm" role are allowed to use this command.
        - If no members match the role condition, a message is sent indicating no members were found.
        - A confirmation message is sent before listing the members, with a view containing Yes/No buttons for confirmation.
    """
    """Lists members based on role conditions with confirmation."""
    AllowedRoles = ["HKN Exec Comm"]
    if not any(role.name in AllowedRoles for role in interaction.user.roles):
        await interaction.response.send_message(f"You do not have permission to use this command. Only members with the {AllowedRoles} role can use it.")
        return
    
    guild = interaction.guild
    members_to_list = []

    # Parse the condition and loop through all members
    for member in guild.members:
        member_roles = [role.name for role in member.roles]
        
        # Check if the member's roles meet the role condition
        if process_roles_condition(role_condition, member_roles):
            members_to_list.append(member)

    # If no members match the condition
    if not members_to_list:
        await interaction.response.send_message(f"No members found matching '{role_condition}'.")
        return

    # List members and ask for confirmation
    member_names = [f"{member.name}\t Roles: {', '.join([role.name for role in member.roles if role.name != '@everyone'])}" for member in members_to_list]
    if role_condition == "@everyone":
        confirmation_msg = "List all members in the server?"
    else:
        confirmation_msg = f"list {len(members_to_list)} members based on the role condition '{role_condition}'?"

    # Create a confirmation view (with buttons for Yes/No)
    view = ConfirmationView(interaction, members_to_list, role_condition, action='list')
    await interaction.response.send_message(confirmation_msg, view=view)

@bot.tree.command(name="remove_members", description="Remove members based on role conditions with confirmation.")
async def remove_members(interaction: discord.Interaction, role_condition: str):
    """
    Remove members (kick) based on role conditions, with confirmation.
    Args:
        interaction (discord.Interaction): The interaction object representing the command invocation.
        role_condition (str): The condition to check against members' roles.
    Returns:
        None
    Behavior:
        - Checks if the user invoking the command has the required role.
        - Parses the role condition and identifies members matching the condition.
        - If no members match the condition, sends a message indicating so.
        - Lists members matching the condition and asks for confirmation before removal.
    """
    """Remove members (kick) based on role conditions, with confirmation."""
    AllowedRoles = ["HKN Exec Comm"]
    if not any(role.name in AllowedRoles for role in interaction.user.roles):
        await interaction.response.send_message(f"You do not have permission to use this command. Only members with the {AllowedRoles} role can use it.")
        return
    
    guild = interaction.guild
    members_to_remove = []

    # Parse the condition and loop through all members
    for member in guild.members:
        member_roles = [role.name for role in member.roles]
        
        # Check if the member's roles meet the role condition
        if process_roles_condition(role_condition, member_roles):
            members_to_remove.append(member)

    # If no members match the condition
    if not members_to_remove:
        await interaction.response.send_message(f"No members found matching '{role_condition}'.")
        return

    # List members and ask for confirmation
    member_names = [f"{member.mention} ({member.name})\t Roles: {', '.join([role.name for role in member.roles if role.name != '@everyone'])}" for member in members_to_remove]
    confirmation_msg = f"The following members will be removed based on the role condition '{role_condition}':\n"
    confirmation_msg += "\n".join(member_names)

    # Create a confirmation view (with buttons for Yes/No)
    view = ConfirmationView(interaction, members_to_remove, role_condition, action='remove')
    await interaction.response.send_message(confirmation_msg, view=view)

# Helper Stuff
def process_roles_condition(roles_string, member_roles):
    """
    Process the role condition string and check if the member's roles match.
    The roles_string can contain roles separated by OR (|) and AND (&) operators.
    Parentheses can be used to group conditions. The NOT operator (!) can be used
    to negate a role condition.
    Args:
        roles_string (str): The string representing the role conditions.
        member_roles (list): The list of roles that the member has.
    Returns:
        bool: True if the member's roles match the conditions, False otherwise.
    """
    """Process the role condition string and check if the member's roles match."""
    def evaluate_condition(condition, member_roles):
        """Evaluate a single condition or a parenthesized group."""
        # Remove any outer parentheses
        if condition.startswith("(") and condition.endswith(")"):
            return process_roles_condition(condition[1:-1], member_roles)
        
        # Handle NOT condition
        if condition.startswith("!"):
            return condition[1:].strip() not in member_roles
        
        # Check if the role is present in member roles
        return condition.strip() in member_roles

    # Split by OR (|)
    or_conditions = roles_string.split("|")

    for condition in or_conditions:
        # Split by AND (&)
        and_conditions = condition.split("&")

        # Check if all AND conditions are met for this part of the OR condition
        if all(evaluate_condition(role.strip(), member_roles) for role in and_conditions):
            return True

    return False

class ConfirmationView(View):
    def __init__(self, interaction, members_to_remove, role_condition, action):
        super().__init__(timeout=30)  # Set timeout for response (30 seconds)
        self.interaction = interaction
        self.members_to_remove = members_to_remove
        self.role_condition = role_condition
        self.action = action  # Action to perform (either 'remove' or 'list')
        self.confirmed = False
    
    async def on_timeout(self):
        """Handle timeout if the user doesn't respond in time."""
        await self.interaction.followup.send("Confirmation timeout. No action was taken.")

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        """Handles the confirmation response."""
        self.confirmed = True
        await interaction.response.edit_message(content=interaction.message.content + f"\nProceeding with the action: {self.action} for {len(self.members_to_remove)} member(s).")

        # Perform the action (remove members or list them)
        if self.action == 'remove':
            # Check if the bot has the permissions and role hierarchy is correct
            if not interaction.guild.me.guild_permissions.kick_members:
                await interaction.followup.send("I do not have the 'Kick Members' permission.")
                return
            
            members_removed = []
            for member in self.members_to_remove:
                try:
                    await member.kick(reason=f"Matched role condition: {self.role_condition}")
                    members_removed.append(member.name)
                except discord.Forbidden:
                    print(f"Could not remove {member.name} (insufficient permissions).")
                except discord.HTTPException as e:
                    print(f"Failed to remove {member.name}: {e}")

            if members_removed:
                await self.interaction.followup.send(f"Members removed: {', '.join(members_removed)}")
            else:
                await self.interaction.followup.send(f"No members could be removed.")
        elif self.action == 'list':
            member_names = [f"{member.display_name}\t\t ({member.name})\t Roles:  {', '.join([role.name for role in member.roles if role.name != '@everyone'])}" for member in self.members_to_remove]
            await self.interaction.followup.send(f"Members matching '{self.role_condition}':\n" + "\n".join(member_names))

        # Stop the view from accepting further responses
        self.stop()
        # Remove the button after the action is completed
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        """Handles the cancellation response."""
        self.confirmed = False
        # await interaction.response.send_message(f"Action canceled. No members were {self.action}ed.", ephemeral=True)
        self.stop()
        # Remove the original message
        await interaction.message.delete()


bot.run(token)