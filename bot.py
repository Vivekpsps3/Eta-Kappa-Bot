import discord
from discord.ext import commands
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

bot.run(token)