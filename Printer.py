import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from threading import Thread
import asyncio
import numpy as np

TOKEN_PATH = "./TOKEN.env"
load_dotenv(TOKEN_PATH)
TOKEN = os.getenv('PINTER_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('DISCORD_CHANNEL')
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def send(Message, username=None, avatar=None):
	webhook = discord.Webhook.from_url(WEBHOOK_URL, adapter=discord.RequestsWebhookAdapter())
	webhook.send(content=Message, wait=False, username=username, avatar_url=avatar)

def gekapert(member, guild):
	Member = discord.utils.get(guild.members, name=member)
	if not Member.bot:
		send("Account erfolgreich gekapert.", username=Member.name, avatar=Member.avatar_url)

def shutdown():
	BOTLOOP.create_task(bot.logout())
	print("Bot has logged out")
	try: BOTTHREAD.join()
	except: None

@bot.event
async def on_ready():
	global bot_is_ready
	game = discord.Game("/bip to check activity")
	await bot.change_presence(activity=game)
	print(f'{bot.user.name} has connected to Discord!')

	guild = discord.utils.get(bot.guilds, name=GUILD)
	# Whitekeks = discord.utils.get(guild.members, name="Whitekeks")
	for Member in guild.members:
		print(Member.name)
		print(Member.avatar_url)
		print(Member.avatar_url_as(format="png"))
		print(get_avatar_url(Member.id, Member.avatar))

	bot_is_ready = True
	shutdown()

@bot.command(name='bip', help='bop')
async def bip(ctx):
	await ctx.send('bop')

bot_is_ready = False

def run_bot():
	BOTLOOP.run_until_complete(bot.start(TOKEN))

BOTLOOP = asyncio.get_event_loop()
run_bot()
# BOTTHREAD = Thread(target=run_bot)
# BOTTHREAD.start()

# while not bot_is_ready:
# 	None

# shutdown()
