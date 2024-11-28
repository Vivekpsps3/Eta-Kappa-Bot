import discord
from discord.ext import commands
import requests

with open ("secrets.env", "r") as file:
    token = file.read()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='-', intents=intents)

# Helper
def ping_llama(question):
    prompt=f"Q: {question}\nA:"
    with open ("system.txt", "r") as file:
        system = file.read()
    url = 'http://desktop.server:11434/api/generate'
    payload = {
        'model': 'llama3.2',
        'system': system,
        'prompt': prompt,
        'stream': False,
    }

    response = requests.post(url, json=payload)
    return response.json()["response"]


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Sync commands with Discord
    await bot.tree.sync()

#ping check command
@bot.tree.command(name="ping", description="Replies with Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!") 
    
@bot.tree.command(name="sharky", description="Ask Sharky a question")
async def sharky(interaction: discord.Interaction, question: str):
    response = "Sharky says: hello"
    await interaction.response.send_message(response)

# Replace 'YOUR_TOKEN_HERE' with your bot's token
bot.run(token)