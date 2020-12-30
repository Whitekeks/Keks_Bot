# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv("TOKEN.env")
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if "!" in message.content:
        await message.channel.send("None")
    elif message.content == 'raise-exeption':
        raise discord.DiscordException

@client.event
async def on_error(event, *args, **kwargs):
    with open("err.log", "a") as f:
        if event == "on_message":
            f.write(f"Unhandled message: {args[0]}\n")
        else:
            raise

client.run(TOKEN)