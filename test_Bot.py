import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import aiohttp

PATH = os.path.dirname(os.path.abspath(__file__))
load_dotenv(f'{PATH}/TOKEN_BOT.env')
TOKEN = os.getenv('TOKEN')
TWITCH_CLIENTID = os.getenv("TWITCH_ID")
TWITCH_SECRET = os.getenv("TWITCH_SECRET")
TWITCH_CALLBACK = os.getenv("CALLBACK")
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
botloop = asyncio.get_event_loop()
Games = ["v. 1.0","!help for infos", "!echo for debugging", '!roll_dice for dice', "!random for rand(s)", "!rand_user no bots :(", 'try !bip',\
		"!shutdown don't...", "!restart: While True: Bot()", "!avatar for more details"]
COMMANDS = ['!help', '!echo', '!shell', '!stopshell']

DATA = {'game_name': 'Apex', 'thumbnail_url': 'https://static-cdn.jtvnw.net/previews-ttv/live_user_c4ndygg-1280x720.jpg?cb=1611433033', 'title': 'Streaming Apex and not Destiny 2...', 'user_id': '246901251', 'user_login': 'c4ndygg', 'user_name': 'c4ndygg', 'viewer_count': 0}


async def Embed(channel, login_name = "whitekeks"):
	Embed = discord.Embed(description=f"**Subscription successfully for [{login_name}](https://twitch.tv/{login_name}) in <#{channel.id}>**")
	Embed.add_field(name="test", value="[`123`](http://www.whitekeks.tk) test", inline=False)
	Embed.add_field(name="test", value="[`123`](http://www.whitekeks.tk) test", inline=False)
	return Embed


@bot.event
async def on_ready():
	guild = discord.utils.get(bot.guilds, name="Keks")
	member = discord.utils.get(guild.members, name="e^(iπ) + 1 = 0")
	async with aiohttp.ClientSession() as session:
		Webhook = discord.Webhook.from_url("https://discord.com/api/webhooks/813803313107304540/-88iPEMgX8ZxiK2ggLNYS16tT6fIKsch07jRve9uJk3LRaU0kqOrXYJuI4-kgG-SuWfK", adapter=discord.AsyncWebhookAdapter(session))
		await Webhook.send(content="NO I DONT", username=member.name, avatar_url=member.avatar_url)

@bot.command(name="test")
async def test(ctx, member):
	try:
		print(member[3:len(member)-1])
	except:
		print(member)


botloop.run_until_complete(bot.start(TOKEN))