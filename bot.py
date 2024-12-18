import discord
from discord.ext import commands
import requests
import json

with open ("secrets.env", "r") as file:
    token = file.read()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='-', intents=intents)

# Helper
def chunk_sentences(text, max_tokens=2000):
    sentences = text.split(". ")
    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(chunk) + len(sentence) < max_tokens:
            chunk += sentence + ". "
        else:
            chunks.append(chunk)
            chunk = sentence + ". "
    if chunk:
        chunks.append(chunk)
    return chunks

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
    
    url = 'http://192.168.0.181:11434/api/generate'
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

bot.run(token)
