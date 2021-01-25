import os
import sys
import psutil
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands
import time
from threading import Thread
import asyncio
import numpy as np


load_dotenv("TOKEN.env")
TOKEN = os.getenv('PRINTER_TOKEN')
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
botloop = asyncio.get_event_loop()
Games = ["v. 1.0","!help for infos", "!echo for debugging", '!roll_dice for dice', "!random for rand(s)", "!rand_user no bots :(", 'try !bip',\
		"!shutdown don't...", "!restart: While True: Bot()", "!avatar for more details"]
COMMANDS = ['!help', '!echo', '!shell', '!stopshell']


def sleep(Interval):
	time_1 = time.time()
	while time.time()-time_1<Interval and alive:
		None

def Preference():
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	
	loop.run_until_complete(bot.change_presence(activity=discord.Game("Hello, just started!")))
	sleep(5)

	Interval = 60
	i = 0
	while alive:
		game = discord.Game(Games[i])
		loop.run_until_complete(bot.change_presence(activity=game))
		# time.sleep(Interval)
		sleep(Interval)
		if i == len(Games)-1: i = 0
		else: i += 1

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')
	thread.start()
	member = discord.utils.get(bot.get_all_members(), name="Steffen")
	print(len(member.roles))

@bot.event
async def on_command_error(ctx, error):
	with open("err.log", "a") as f:
		f.write(f"command error: {error}")
	await ctx.send(error)

@bot.command(name='echo', help='Sends back the given Message')
async def echo(ctx, Message):
	await ctx.send(Message)

@bot.command(name='bip', help='bop')
async def bip(ctx):
	await ctx.send('bop')

@bot.command(name='shutdown', help="shut's down the System", hidden=True)
@commands.is_owner()
async def shutdown(ctx):
	await ctx.send('Shutting down... Bye!')
	SHUTDOWN()

@bot.command(name='random', help='```random start stop N```, gives N random ints in [start,stop)')	
async def random(ctx, start: int, stop: int, N: int):
	Random = np.random.randint(start, stop, N).tolist()
	for i, rand in enumerate(Random):
		Random[i] = str(rand)
	await ctx.send(", ".join(Random))

@bot.command(name='roll_dice', help='just a standart dice')
async def roll_dice(ctx):
	Random = np.random.randint(1,7)
	await ctx.send(Random)

@bot.command(name='avatar', help='get avatar_url of member as format ‘webp’, ‘jpeg’, ‘jpg’, ‘png’ or ‘gif’, or ‘gif’ (default is ‘webp’)')
async def avatar(ctx, Member, Format="webp"):
	MEMBER = discord.utils.get(ctx.guild.members, name=str(Member))
	await ctx.send(str(MEMBER.avatar_url_as(format=Format)))

@bot.command(name='rand_user', help='get random User on Server')
async def raffle(ctx):
	guild = ctx.guild
	rand_user = np.random.choice(guild.members)
	while rand_user.bot:
		rand_user = np.random.choice(guild.members)
	await ctx.send(rand_user.name)


def SHUTDOWN():
	global alive
	print("starting shutdown")
	botloop.create_task(bot.logout())
	while True:
		try: 
			loop = asyncio.get_running_loop()
			loop.close()
		except:
			break
	try:
		alive = False 
		thread.join()
	except: None

def START():
	botloop.run_until_complete(bot.start(TOKEN))

def RESTART():
	print("Bot is restarting...")
	SHUTDOWN()
	print("Bot has logged out")
	
	try:
		p = psutil.Process(os.getpid()) #gives current Process
		for handler in p.open_files() + p.connections():
			os.close(handler.fd)
	except Exception as e:
		logging.error(e)
	
	python = sys.executable
	os.execl(python, python, *sys.argv)

alive = True
thread = Thread(target=Preference)

START()

print("Bot has logged out")
