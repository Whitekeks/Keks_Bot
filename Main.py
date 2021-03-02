import os, sys, psutil, logging, discord, time, asyncio, pytz
import twitter as tw
from bin import SocketServer, importantFunctions, twitter, twitch, selfrole, stdrole, events, Commands
from bin.importantFunctions import s, sleep, send_private, CustomError, STDPREFIX
from dotenv import load_dotenv
from discord.ext import commands
from threading import Thread
import numpy as np
from datetime import datetime
import mysql.connector

# get creationtime:
now = datetime.now()
timezone = pytz.timezone("Europe/Berlin")
now = timezone.localize(now)

# To make the Setup individuel:
SEED = str(np.random.randint(0, int(2.e9)))

print("starting...")

"""--------------environment variables------------------"""

PATH = os.path.dirname(os.path.abspath(__file__))
if not os.path.isfile(f'{PATH}/TOKEN_BOT.env'):
	GEHEIMNIS=[]
	print("TOKEN_BOT.env not found! Creating new (make sure TOKEN_BOT.env is in .gitignore, so your data is secured when pushing):")
	print("Enter Bot-Token:")
	TOKEN = str(input())
	GEHEIMNIS.append(f"TOKEN={TOKEN}")
	print(f"TOKEN={TOKEN}\n\nTwitter Data:\nEnter Twitter consumer key:")
	TWITTER_CONSUMER_KEY = str(input())
	GEHEIMNIS.append(f"TWITTER_CONSUMER_KEY={TWITTER_CONSUMER_KEY}")
	print(f'TWITTER_CONSUMER_KEY={TWITTER_CONSUMER_KEY}\nEnter Twitter consumer secret:')
	TWITTER_CONSUMER_SECRET = str(input())
	GEHEIMNIS.append(f"TWITTER_CONSUMER_SECRET={TWITTER_CONSUMER_SECRET}")
	print(f'TWITTER_CONSUMER_SECRET={TWITTER_CONSUMER_SECRET}\nEnter Twitter access token key:')
	TWITTER_ACCESS_TOKEN_KEY = str(input())
	GEHEIMNIS.append(f"TWITTER_ACCESS_TOKEN_KEY={TWITTER_ACCESS_TOKEN_KEY}")
	print(f'TWITTER_ACCESS_TOKEN_KEY={TWITTER_ACCESS_TOKEN_KEY}\nEnter Twitter access token secret:')
	TWITTER_ACCESS_TOKEN_SECRET = str(input())
	GEHEIMNIS.append(f"TWITTER_ACCESS_TOKEN_SECRET={TWITTER_ACCESS_TOKEN_SECRET}")
	print(f"TWITTER_ACCESS_TOKEN_SECRET={TWITTER_ACCESS_TOKEN_SECRET}\n\nTwitch Data:\nEnter Twitch ClientID:")
	TWITCH_CLIENTID = str(input())
	GEHEIMNIS.append(f"TWITCH_ID={TWITCH_CLIENTID}")
	print(f"TWITCH_CLIENTID={TWITCH_CLIENTID}\nEnter Twitch Secret")
	TWITCH_SECRET = str(input())
	GEHEIMNIS.append(f"TWITCH_SECRET={TWITCH_SECRET}")
	print(f"TWITCH_SECRET={TWITCH_SECRET}\nEnter Twitch Callback URL where notifications will be send, \
		verification URL must be set in https://dev.twitch.tv/console/apps/:")
	TWITCH_CALLBACK = str(input())
	GEHEIMNIS.append(f"CALLBACK={TWITCH_CALLBACK}")
	print(f"TWITCH_CALLBACK={TWITCH_CALLBACK}\n\nMYSQL_Data:\nEnter MYSQL Host (default=localhost):")
	MYSQL_HOST = str(input())
	GEHEIMNIS.append(f"MYSQL_HOST={MYSQL_HOST}")
	print(f"MYSQL_HOST={MYSQL_HOST}\nEnter MYSQL User:")
	MYSQL_USER = str(input())
	GEHEIMNIS.append(f"MYSQL_USER={MYSQL_USER}")
	print(f"MYSQL_USER={MYSQL_USER}\nEnter MYSQL User-password")
	MYSQL_PASSWORD = str(input())
	GEHEIMNIS.append(f"MYSQL_PASSWORD={MYSQL_PASSWORD}")
	print(f"MYSQL_PASSWORD={MYSQL_PASSWORD}\nEnter MYSQL Database-Name")
	MYSQL_DATABASE = str(input())
	GEHEIMNIS.append(f"MYSQL_DATABASE={MYSQL_DATABASE}")
	print(f"MYSQL_DATABASE={MYSQL_DATABASE}\n\nKey for indentification of Database will be created, do not loose, or Database is not usable!!!:")
	GEHEIMNIS.append(f"KEY={SEED}")
	print(f"KEY={SEED}")
	with open(f'{PATH}/TOKEN_BOT.env', 'w') as w:
		envstr="# .env\n"
		for i in GEHEIMNIS:
			envstr += f"{i}\n"
		w.write(envstr)
	GEHEIMNIS=[]
else:
	load_dotenv(f'{PATH}/TOKEN_BOT.env')
	TOKEN = os.getenv('TOKEN')
	TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
	TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
	TWITTER_ACCESS_TOKEN_KEY = os.getenv('TWITTER_ACCESS_TOKEN_KEY')
	TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
	TWITCH_CLIENTID = os.getenv('TWITCH_ID')
	TWITCH_SECRET = os.getenv('TWITCH_SECRET')
	TWITCH_CALLBACK = os.getenv('CALLBACK')
	MYSQL_HOST = os.getenv('MYSQL_HOST')
	MYSQL_USER = os.getenv('MYSQL_USER')
	MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
	MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
	SEED = os.getenv('KEY')

print("env's set")

"""-------------------------Database---------------------------"""

# security for Database:
np.random.seed(int(SEED))
KEY = np.random.rand()

# log into Database:
conn = mysql.connector.connect(
	host=MYSQL_HOST,
	user=MYSQL_USER,
	password=MYSQL_PASSWORD,
	database=MYSQL_DATABASE
)
cursor = conn.cursor(buffered=True)

# create tables if they do not exist:
cursor.execute('CREATE TABLE IF NOT EXISTS guilds (_id BIGINT, _name TEXT, _prefix TEXT, _stdrole BIGINT, _autodelete BOOL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
cursor.execute('CREATE TABLE IF NOT EXISTS members (_id BIGINT, _name TEXT, _nick TEXT, _guild BIGINT, _regist BIGINT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
cursor.execute('CREATE TABLE IF NOT EXISTS twitter (_usertag TEXT, _channel_id BIGINT, _creation_time TEXT, _guild_id BIGINT, _feed_id BIGINT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
cursor.execute('CREATE TABLE IF NOT EXISTS twitch_feeds (_guild_id BIGINT, _channel_id BIGINT, _topic_id BIGINT, _message_id BIGINT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
cursor.execute('CREATE TABLE IF NOT EXISTS twitch_topics (_topic_id BIGINT, _login TEXT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
cursor.execute('CREATE TABLE IF NOT EXISTS bonds (_role_id BIGINT, _emoji TEXT, _guild_id BIGINT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
cursor.execute('CREATE TABLE IF NOT EXISTS sr_messages (_message_id BIGINT, _guild_id BIGINT, _jump_url TEXT, _user_id BIGINT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
cursor.execute('CREATE TABLE IF NOT EXISTS bot (_key DOUBLE, _creation_time TEXT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')

# check if key is right, and Bot exists:
cursor.execute(f'SELECT _key FROM bot')

# if Bot does not Exist:
if not cursor.fetchall():
	g = (KEY, now.strftime('%a %b %d %X %z %Y'),)
	cursor.execute(f'INSERT INTO bot VALUES ({g[0]},"{g[1]}")')
else:
	cursor.execute(f'SELECT _key FROM bot WHERE _key={KEY}')
	key = cursor.fetchone()[0]
	if key!=KEY:
		raise CustomError(f"Key is wrong, please delete existing database ({MYSQL_DATABASE})")
conn.commit()

print("database set")

"""---------------------Bot-----------------------------"""

def Prefix(Bot, Message):
	try:
		cursor.execute(f"SELECT _prefix FROM guilds WHERE _id={Message.guild.id}")
		pfx = cursor.fetchone()[0]
	except:
		pfx = STDPREFIX
	return pfx

bot = commands.Bot(command_prefix=Prefix, intents=discord.Intents.all())
botloop = asyncio.get_event_loop()
# Games = ["v. 1.2.2","/help for infos","try /bip","!shutdown don't...", "/restart: While True: Bot()",\
# 		"/set_prefix nobody is Safe", "/register_guild with the boys", "/register without the boys"]
Games = ["v. 1.4.1", "/help for infos"]

print("bot set")

"""----------------------Globals------------------------"""

REGISTER_EMOJI_ACCEPT = "👍"
REGISTER_EMOJI_DENY = "👎"
THREADS = []
alive = True
cursor.execute(f"SELECT _creation_time FROM bot WHERE _key={KEY}")
BOT_CREATION_TIME = datetime.strptime(cursor.fetchone()[0], '%a %b %d %X %z %Y')  # type = datetime
# Set RESET_TIME:
RESET_TIME = timezone.localize( datetime.now() )
if RESET_TIME.time() < datetime(2021, 1, 1, 6, 55, 0, 0).time():
	RESET_TIME = RESET_TIME.replace(hour=6, minute=55, second=0, microsecond=0)
else:
	try:
		RESET_TIME = RESET_TIME.replace(day=RESET_TIME.day+1, hour=6, minute=55, second=0, microsecond=0)
	except:
		try:
			RESET_TIME = RESET_TIME.replace(month=RESET_TIME.month+1 ,day=1, hour=6, minute=55, second=0, microsecond=0)
		except:
			RESET_TIME = RESET_TIME.replace(year=RESET_TIME.year+1 ,month=1 ,day=1, hour=6, minute=55, second=0, microsecond=0)

print("globals set")

"""---------------------functions----------------------"""

async def on_guild_remove(guild):
	await Events.on_guild_remove(guild)
	await Stdrole.on_guild_remove(guild)
	await Selfrole.on_guild_remove(guild)
	await Twitch.on_guild_remove(guild)
	await Twitter.on_guild_remove(guild)

async def on_guild_join(guild):
	await Events.on_guild_join(guild)

async def on_guild_update(before, after):
	await Events.on_guild_update(before, after)

async def on_member_remove(member):
	await Events.on_member_remove(member)
	await Stdrole.on_member_remove(member)

async def on_member_join(member):
	await Stdrole.on_member_join(member)

async def on_member_update(before, after):
	await Events.on_member_update(before, after)
	await Stdrole.on_member_update(before, after)

# changes the bots activity, just for misscalanios purpose
def Preference():
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)

	loop.run_until_complete(bot.change_presence(activity=discord.Game("Hello, just started!")))
	sleep(5, alive)

	Interval = 60
	i = 0
	while alive:
		game = discord.Game(Games[i])
		loop.run_until_complete(bot.change_presence(activity=game))
		# time.sleep(Interval)
		sleep(Interval, alive)
		if i == len(Games)-1:
			i = 0
		else:
			i += 1


def daily_reset():
	while (time.localtime()!=RESET_TIME.timetuple()) and alive:
		None
	if alive:
		# # renew subsciptions
		# for login in TwitchFeeds:
		# 	asyncio.run_coroutine_threadsafe(SERVER.HookStream(loginName=login, mode="subscribe"), botloop)
		try: RESTART(mode="restart")
		except: None


"""----------------------- Events ----------------------------"""


@bot.event
async def on_ready():
	print("\nUpdate DataBase...")

	# check for new members and missing guilds:
	cursor.execute('SELECT _id FROM guilds')
	guilds = cursor.fetchall()
	for ID in guilds:
		guild = discord.utils.get(bot.guilds, id=ID[0])
		# Update Members if Guild not exists
		if guild:
			for member in guild.members:
				cursor.execute(f'SELECT _id FROM members WHERE _id={member.id} AND _guild={guild.id}')
				if cursor.fetchone():
					await on_member_update(member, member)
				else:
					await on_member_join(member)

			cursor.execute(f'SELECT _id FROM members WHERE _guild={guild.id}')
			Members = cursor.fetchall()
			for member_id in Members:
				Member = discord.utils.get(guild.members, id=member_id[0])
				if not Member:
					await on_member_remove(member)
		else:
			await on_guild_remove(guild)

	# check if Guild is registered:
	for Guild in bot.guilds:
		cursor.execute(f'SELECT _id FROM guilds WHERE _id={Guild.id}')
		if not cursor.fetchone():
			await on_guild_join(Guild)
		else:
			await on_guild_update(Guild, Guild)

	print(f'{bot.user.name} has connected to Discord!')

	# start Twitch:
	Twitch.start()

	# start Twitter:
	Twitter.start()

	Reset_Thread.start()
	print("Reset_Thread has started")

	Preference_Thread.start()
	print('Preference has started\n')


"""----------------------- Decorators ----------------------------"""


def is_guild_owner():
	def predicate(ctx):
		if not ctx.guild:
			raise commands.NoPrivateMessage

		if ctx.guild.owner_id == ctx.author.id:
			return True

		raise commands.UserInputError("You are not the Owner of this Guild")
	return commands.check(predicate)


def is_in_guild():
	def predicate(ctx):
		if ctx.guild:
			return True
		raise commands.NoPrivateMessage
	return commands.check(predicate)


"""------------------------------ Commands --------------------------"""


@commands.command(name='register_guild', help='registers Guild. WARNING: deletes Meta-Data if Guild allready exists')
@is_guild_owner()
async def register_guild(ctx):
	guild = ctx.guild
	await on_guild_remove(guild)
	await on_guild_join(guild)
	await guild.owner.send(embed=discord.Embed(description='Guild successfully registered!'))


@commands.command(name='register', help='register yourself. WARNING: deletes your Meta-Data')
@is_in_guild()
async def register(ctx):
	member = ctx.author
	await on_member_remove(member)
	await on_member_join(member)


@bot.command(name='shutdown', help="shuts down the System")
@commands.is_owner()
async def shutdown(ctx):
	await ctx.send('Shutting down... Bye!')
	SHUTDOWN()


@bot.command(name='restart', help="restarts the System")
@commands.is_owner()
async def restart(ctx):
	await ctx.send('Restarting...')
	RESTART(mode="restart")


def SHUTDOWN(mode="shutdown"):
	# to shut down preference and reset thread
	global alive
	alive = False

	print("starting shutdown")
	if mode=="shutdown":
		# stop Twitch
		Twitch.stop()
	botloop.create_task(bot.logout())

	# stop Twitter
	Twitter.stop()

	# close running loops
	while True:
		try:
			loop = asyncio.get_running_loop()
			loop.close()
		except:
			break

	try:
		Preference_Thread.join()
		Reset_Thread.join()
	except:
		None

	conn.close()


def RESTART(mode="shutdown"):
	print("Bot is restarting...")
	SHUTDOWN(mode=mode)
	print("Bot has logged out")

	try:
		p = psutil.Process(os.getpid())  # gives current Process
		for handler in p.open_files() + p.connections():
			os.close(handler.fd)
	except Exception as e:
		logging.error(e)

	python = sys.executable
	os.execl(python, python, *sys.argv)



"""------------------------------ Startup --------------------------"""


Preference_Thread = Thread(target=Preference)

Reset_Thread = Thread(target=daily_reset)

# set twitch
Twitch = twitch.Twitch(
	bot=bot,
	prefix=STDPREFIX, 
	mysql_connector=conn, 
	botloop=botloop, 
	CLIENTID=TWITCH_CLIENTID,
	SECRET=TWITCH_SECRET,
	CALLBACK=TWITCH_CALLBACK
)

# set twitter
Twitter = twitter.Twitter(
	bot=bot,
	prefix=STDPREFIX,
	mysql_connector=conn,
	botloop=botloop,
	CONSUMER_KEY=TWITTER_CONSUMER_KEY,
	CONSUMER_SECRET=TWITTER_CONSUMER_SECRET,
	ACCESS_TOKEN_KEY=TWITTER_ACCESS_TOKEN_KEY,
	ACCESS_TOKEN_SECRET=TWITTER_ACCESS_TOKEN_SECRET
)

# set selfrole:
Selfrole = selfrole.selfrole(
	bot=bot,
	prefix=STDPREFIX,
	mysql_connector=conn,
	botloop=botloop
)

# set stdrole:
Stdrole = stdrole.stdrole(
	bot=bot,
	prefix=STDPREFIX,
	mysql_connector=conn,
	botloop=botloop,
	PATH=PATH,
	REGISTER_EMOJI_ACCEPT=REGISTER_EMOJI_ACCEPT,
	REGISTER_EMOJI_DENY=REGISTER_EMOJI_DENY
)

# set commands:
Commands = Commands.Commands(
	bot=bot,
	prefix=STDPREFIX,
	mysql_connector=conn,
	botloop=botloop
)

# set events:
Events = events.events(
	bot=bot,
	prefix=STDPREFIX,
	mysql_connector=conn,
	botloop=botloop,
	func_member_join=on_member_join  # Possible because referencing at actual calling not sending
)

# add Cogs:
bot.add_cog(Twitch)
bot.add_cog(Twitter)
bot.add_cog(Selfrole)
bot.add_cog(Stdrole)
bot.add_cog(Commands)
bot.add_cog(Events)

botloop.run_until_complete(bot.start(TOKEN))

print("Bot has logged out")
