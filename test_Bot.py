import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio

PATH = os.path.dirname(os.path.abspath(__file__))
load_dotenv(f'{PATH}/TOKEN_BOT.env')
TOKEN = os.getenv('TOKENz')
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
	print(f'{bot.user.name} has connected to Discord!')
	guild = discord.utils.get(bot.guilds, name="Keks")
	channel = discord.utils.get(guild.channels, name="system")
	await channel.send(":sob:")