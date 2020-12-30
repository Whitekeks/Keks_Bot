import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import aiohttp

load_dotenv("TOKEN.env")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MAINLOOP = asyncio.get_event_loop()

#async Webhook creation
async def send(Message):
	async with aiohttp.ClientSession() as session: # __enter__ and __exit__ function directly called (closed Session)
		webhook = discord.Webhook.from_url(WEBHOOK_URL, adapter=discord.AsyncWebhookAdapter(session))
		await webhook.send(content=Message, wait=False, username="Printer_Bot", avatar_url="http://whitekeks.ga/9068935281DDF65576064A2898191FDD.jpg", tts=False, file=None, files=None, embed=None, embeds=None, allowed_mentions=None)

#MAINLOOP.run_until_complete(send())

def send(Message, username=None, avatar=None):
	webhook = discord.Webhook.from_url(WEBHOOK_URL, adapter=discord.RequestsWebhookAdapter())
	webhook.send(content=Message, wait=False, username=username, avatar_url=avatar)

send("""
```py
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

def gekapert(member, guild):
	Member = discord.utils.get(guild.members, name=member)
	if not Member.bot:
		send("Account erfolgreich gekapert.", username=Member.name, avatar=Member.avatar_url)

def send(Message, username=None, avatar=None):
	webhook = discord.Webhook.from_url(WEBHOOK_URL, adapter=discord.RequestsWebhookAdapter())
	webhook.send(content=Message, wait=False, username=username, avatar_url=avatar)
```
""")