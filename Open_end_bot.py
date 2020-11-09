import os
import sys
import psutil
import logging
import sqlite3
from dotenv import load_dotenv
import discord
from discord.ext import commands
import time
from threading import Thread
import asyncio
import numpy as np

SEED = str(np.random.randint(0,int(2.e9)))

#Set env's:
PATH = os.path.dirname(os.path.abspath(__file__))
if not os.path.isfile(f'{PATH}/TOKEN_END.env'):
	print("TOKEN_END.env not found! Creating new:")
	print("Enter Bot-Token:")
	TOKEN = str(input())
	print(f"TOKEN={TOKEN}\nTwitter Data:\nEnter consumer key:")
	TWITTER_CONSUMER_KEY = str(input())
	print(f'TWITTER_CONSUMER_KEY={TWITTER_CONSUMER_KEY}\nEnter consumer secret:')
	TWITTER_CONSUMER_SECRET = str(input())
	print(f'TWITTER_CONSUMER_SECRET={TWITTER_CONSUMER_SECRET}\nEnter access token key:')
	TWITTER_ACCESS_TOKEN_KEY = str(input())
	print(f'TWITTER_ACCESS_TOKEN_KEY={TWITTER_ACCESS_TOKEN_KEY}\nEnter access token secret:')
	TWITTER_ACCESS_TOKEN_SECRET = str(input())
	print(f"TWITTER_ACCESS_TOKEN_SECRET={TWITTER_ACCESS_TOKEN_SECRET}\ncreating Key for Database:")
	print(f"KEY={SEED}")
	with open(f'{PATH}/TOKEN_END.env', 'w') as w:
		w.write(f"# .env\nTOKEN={TOKEN}\nTWITTER_CONSUMER_KEY={TWITTER_CONSUMER_KEY}\nTWITTER_CONSUMER_SECRET={TWITTER_CONSUMER_SECRET}\nTWITTER_ACCESS_TOKEN_KEY={TWITTER_ACCESS_TOKEN_KEY}\nTWITTER_ACCESS_TOKEN_SECRET={TWITTER_ACCESS_TOKEN_SECRET}\nKEY={SEED}")
else:
	load_dotenv(f'{PATH}/TOKEN_END.env')
	TOKEN = os.getenv('TOKEN')
	TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
	TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
	TWITTER_ACCESS_TOKEN_KEY = os.getenv('TWITTER_ACCESS_TOKEN_KEY')
	TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
	SEED = os.getenv('KEY')

#security for Database:
np.random.seed(int(SEED))
KEY = str(np.random.rand())


class CustomError(Exception):
	pass

#create Database:
if os.path.isfile(f"{PATH}/End_Bot.db"):
	conn = sqlite3.connect(database=f"{PATH}/End_Bot.db")
	cursor = conn.cursor()
	try:
		cursor.execute(f'SELECT key FROM bot WHERE key={KEY}')
		cursor.fetchone()[0]
	except:
		raise CustomError("End_Bot.db corrupted! To fix this problem simply delete file.")
else:
	conn = sqlite3.connect(database=f"{PATH}/End_Bot.db")
	cursor = conn.cursor()
	cursor.execute('CREATE TABLE guilds (id int, name text, prefix text)')
	cursor.execute('CREATE TABLE members (id int, name text, nick text, guild int, regist int)')
	cursor.execute('CREATE TABLE bot (key text)')
	cursor.execute(f'INSERT INTO bot VALUES ({KEY})')
	conn.commit()



"""functions"""
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

def sanitizer(dirtyString):
	cleanString = dirtyString.translate({ord(i): None for i in ["'", '"', ";", ",", "(", ")", "{", "}", "[", "]"]})
	return cleanString

def getter(item, table, column, value):
	"cursor.execute(f'SELECT {item} FROM {table} WHERE {column}={value}')"
	cursor.execute(f'SELECT {item} FROM {table} WHERE {column}={value}')
	return cursor.fetchone()[0]
	
def Prefix(Bot, Message):
	try :
		pfx = getter("prefix", "guilds", "id", Message.guild.id)
	except:
		pfx = "!"
	return pfx

async def send_private(user, message):
	DM = await user.create_dm()
	return await DM.send(message)
	
	
#set Bot:
bot = commands.Bot(command_prefix=Prefix, intents=discord.Intents.all())
botloop = asyncio.get_event_loop()
Games = ["v. 1.0","!help for infos","try !bip","!shutdown don't...", "!restart: While True: Bot()",\
		"!set_prefix nobody is Safe", "!register_guild with the boys", "!register without the boys"]

#set Globals:
with open(f'{PATH}/register_message.txt', 'r') as w:
	REGISTER_MESSAGE = w.read()

REGISTER_EMOJI_ACCEPT = "👍"
REGISTER_EMOJI_DENY = "👎"
GUEST_ROLE = "Gast"



""" Events """

@bot.event
async def on_ready():
	print("")
	print("Update DataBase...")
	#check for new members and missing guilds:
	for ID in cursor.execute('SELECT id FROM guilds'):
		guild = discord.utils.get(bot.guilds, id=ID[0])
		if guild:
			for member in guild.members:
				cursor.execute(f'SELECT id FROM members WHERE id={member.id} AND guild={guild.id}')
				if cursor.fetchone():
					await on_member_update(member, member)
				else:
					await on_member_join(member)
			for member_id in cursor.execute(f'SELECT id FROM members WHERE guild={guild.id}'):
				Member = discord.utils.get(guild.members, id=member_id)
				if not Member:
					await on_member_remove(member)
		else:
			await on_guild_remove(guild)
	#check if Guild is registered:
	for Guild in bot.guilds:
		cursor.execute(f'SELECT id FROM guilds WHERE id={Guild.id}')
		if not cursor.fetchone():
			await on_guild_join(Guild)

	conn.commit()

	print(f'{bot.user.name} has connected to Discord!')
	thread.start()


@bot.event
async def on_command_error(ctx, error):
	with open("err.log", "a") as a:
		a.write(f"From {ctx.author.name}, command error: {error}\n")
	print(error)
	try:
		prefix = getter("prefix", "guilds", "id", ctx.guild.id)
		await ctx.send(str(error) + f". Try {prefix}help bzw. {prefix}help command for more infos.")
	except:
		prefix = "!"
		await ctx.send(str(error) + f". Try {prefix}help bzw. {prefix}help command for more infos.")

@bot.event
async def on_guild_join(guild):
	#add guild to DB:
	t = (guild.name, )
	cursor.execute(f'INSERT INTO guilds VALUES ({guild.id},?,"!")', t)	
	
	#add all members of guild to DB:
	for member in guild.members:
		await on_member_join(member)
	conn.commit()

@bot.event
async def on_guild_remove(guild):
	#delete guild:
	cursor.execute(f'DELETE FROM guilds WHERE id={guild.id}')
	#delete members on guild:
	cursor.execute(f'DELETE FROM members WHERE guild={guild.id}')
	conn.commit()

@bot.event
async def on_guild_update(before, after):
	t = (guild.name, )
	cursor.execute(f'UPDATE guilds SET name=? WHERE id={after.id}', t)
	cursor.commit()

@bot.event
async def on_member_join(member):
	guild = member.guild
	if not member.bot:
		if len(member.roles) == 1:
			regist = 2
		else:
			regist = 1

		t = (member.id, member.name, member.nick, guild.id, regist)
		cursor.execute('INSERT INTO members VALUES (?,?,?,?,?)',t)
		conn.commit()

		if regist >= 2:
			Message = await send_private(member, REGISTER_MESSAGE)
			await Message.add_reaction(REGISTER_EMOJI_ACCEPT)
			await Message.add_reaction(REGISTER_EMOJI_DENY)
			return False
		return True

@bot.event
async def on_member_remove(member):
	guild = member.guild
	cursor.execute(f'DELETE FROM members WHERE id={member.id} AND guild={guild.id}')
	conn.commit()

@bot.event
async def on_member_update(before, after):
	guild = before.guild
	#update member:
	t = (after.nick, after.name )
	cursor.execute(f'UPDATE members SET nick=?, name=? WHERE id={after.id} AND guild={guild.id}', t)
	conn.commit()

@bot.event
async def on_reaction_add(reaction, user):
	if reaction.message.content==REGISTER_MESSAGE and not user.bot:

		cursor.execute(f'SELECT guild FROM members WHERE id={user.id} AND regist>=2')
		ID = cursor.fetchone()[0]
		guild = discord.utils.get(bot.guilds, id=ID)
		member = discord.utils.get(guild.members, id=user.id)

		if reaction.emoji==REGISTER_EMOJI_ACCEPT:
			role = discord.utils.get(guild.roles, name=GUEST_ROLE)
			await member.add_roles(role)
			cursor.execute(f'UPDATE members SET regist=1 WHERE id={user.id} AND regist>=2 AND guild={guild.id}')
			await reaction.message.delete()
		elif reaction.emoji==REGISTER_EMOJI_DENY:
			await member.kick()
			cursor.execute(f'DELETE FROM members WHERE id={member.id} AND guild={guild.id}')
			await reaction.message.delete()
			await send_private(reaction.message.author, "Bedingungen müssen akzeptiert werden!")
		conn.commit()

""" Decorators """

def is_guild_owner():
	def predicate(ctx):
		if not ctx.guild:
			raise commands.NoPrivateMessage

		if ctx.guild.owner_id == ctx.author.id:
			return True

		raise commands.UserInputError("You are not the Owner of this Guild")
	return commands.check(predicate)

""" Commands """

@bot.command(name='set_prefix', help='choose a new prefix for this Server (Private allways "!")')
@commands.has_guild_permissions(administrator=True)
async def set_prefix(ctx, prefix : str):
	guild = ctx.guild
	t = (prefix, )
	cursor.execute(f'UPDATE guilds SET prefix=? WHERE id={guild.id}', t)
	conn.commit()
	await ctx.send(f'New Prefix set: "{getter("prefix", "guilds", "id", guild.id)}"')

@bot.command(name='register_guild', help='registers Guild. WARNING: delets Meta-Data if Guild allready exists')
@is_guild_owner()
async def register_guild(ctx):
	guild = ctx.guild
	await on_guild_remove(guild)
	await on_guild_join(guild)
	await guild.owner.send('Guild successfully registered!') 

@bot.command(name='register', help='register yourself')
async def register(ctx):
	member = ctx.author
	guild = ctx.guild

	if type(member)!=discord.member.Member:
		raise CustomError("Only callable on Guilds")

	cursor.execute(f'SELECT id FROM members WHERE id={member.id} AND guild={guild.id}')
	if cursor.fetchone():
		await on_member_update(member, member)
		await send_private(member, f"Successfully updated on {guild.name}")
	else:
		if await on_member_join(member):
			await send_private(member, f"Successfully registered on {guild.name}")

@bot.command(name='bip', help='bop')
async def bip(ctx):
	await ctx.send('bop')
	print(ctx.member.name, "bop")

@bot.command(name='shutdown', help="shut's down the System")
@commands.is_owner()
async def shutdown(ctx):
	await ctx.send('Shutting down... Bye!')
	SHUTDOWN()

@bot.command(name='restart', help="restart's the System")
@commands.is_owner()
async def restart(ctx):
	await ctx.send('Restarting...')
	RESTART()



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
	conn.close()

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