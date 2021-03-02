import os, sys, psutil, logging, discord, time, asyncio, pytz, twitter
from bin import SocketServer
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
cursor.execute(f'SELECT _key FROM bot WHERE _key={KEY}')

# if Bot does not Exist:
if not cursor.fetchone():
	g = (KEY, now.strftime('%a %b %d %X %z %Y'),)
	cursor.execute(f'INSERT INTO bot VALUES ({g[0]},"{g[1]}")')
conn.commit()

print("database set")

"""------------------important functions---------------------"""

class CustomError(Exception):
	pass


def s(dirtyString):
	cleanString = None
	if dirtyString:
		cleanString = dirtyString.translate({ord(i): None for i in [";", '"', "'", "\\"]})
	return cleanString


def getter(item, table, column, value):
	"""cursor.execute(f'SELECT {item} FROM {table} WHERE {column}={value}')
	WARNING: if type(value) == String then value must be f'\"{value}\"' """
	cursor.execute(f'SELECT {item} FROM {table} WHERE {column}={value}')
	return cursor.fetchone()[0]


def Prefix(Bot, Message):
	try:
		pfx = getter("_prefix", "guilds", "_id", Message.guild.id)
	except:
		pfx = STDPREFIX
	return pfx


"""---------------------Bot-----------------------------"""

bot = commands.Bot(command_prefix=Prefix, intents=discord.Intents.all())
botloop = asyncio.get_event_loop()
# Games = ["v. 1.2.2","/help for infos","try /bip","!shutdown don't...", "/restart: While True: Bot()",\
# 		"/set_prefix nobody is Safe", "/register_guild with the boys", "/register without the boys"]
Games = ["v. 1.3.10", "/help for infos"]

print("bot set")

"""---------------------Twitter-------------------------"""

twitter_api = twitter.Api(consumer_key=TWITTER_CONSUMER_KEY,
						  consumer_secret=TWITTER_CONSUMER_SECRET,
						  access_token_key=TWITTER_ACCESS_TOKEN_KEY,
						  access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
)

print("twitter set")


"""----------------------Globals------------------------"""

REGISTER_EMOJI_ACCEPT = "👍"
REGISTER_EMOJI_DENY = "👎"
BOT_CREATION_TIME = datetime.strptime(getter("_creation_time", "bot", "_key", KEY), '%a %b %d %X %z %Y')  # type = datetime

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


STDPREFIX = "/"
THREADS = []
alive = True

print("globals set")

"""---------------------functions----------------------"""

# custom sleep function which breaks when alive = False
def sleep(Interval, Condition=True):
	time_1 = time.time()
	while time.time()-time_1 < Interval and alive and Condition:
		None

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


class checkTwitter:

	def __init__(self, **kwargs):

		self.CREATION_TIME = kwargs['CREATION_TIME']
		self.usertag = kwargs['usertag']
		self.feed_id = kwargs['feed_id']
		self.guild_id = kwargs['guild_id']
		self.channel_id = kwargs['channel_id']

		self.CREATION_TIME = datetime.strptime(
			self.CREATION_TIME, '%a %b %d %X %z %Y')
		self.Stop = False
		self.Thread = Thread(target=self.checkTwitter)
		self.table = f'twitter_{self.feed_id}'

	def checkTwitter(self):
		Tconn = mysql.connector.connect(
			host=MYSQL_HOST,
			user=MYSQL_USER,
			password=MYSQL_PASSWORD,
			database=MYSQL_DATABASE
		)
		c = Tconn.cursor(buffered=True)

		while alive and not self.Stop:
			statuses = twitter_api.GetUserTimeline(screen_name=self.usertag, count=100)
			for rank, status in enumerate(statuses):
				# check if status.id exists:
				c.execute(f'SELECT _id FROM {self.table} WHERE _id={status.id}')
				ID = c.fetchone()
				if not ID:
					retweet = status.retweeted_status != None
					t = (rank, status.id, status.created_at, 0, retweet, )
					c.execute(f'INSERT INTO {self.table} VALUES ({t[0]},{t[1]},"{t[2]}",{t[3]},{t[4]})')
				else:
					c.execute(f'UPDATE {self.table} SET _rank={rank} WHERE _id={status.id}')

				Tconn.commit()

			c.execute(f'DELETE FROM {self.table} WHERE _rank=99')

			# send new tweets:
			c.execute(f'SELECT _id, _created_at, _retweet FROM {self.table} WHERE _send=0 ORDER BY _rank DESC')
			notsended = c.fetchall()
			for i in notsended:
				if datetime.strptime(i[1], '%a %b %d %X %z %Y') > self.CREATION_TIME:
					url = twitter_api.GetStatusOembed(status_id=i[0])['url']
					guild = discord.utils.get(bot.guilds, id=self.guild_id)
					channel = discord.utils.get(guild.channels, id=self.channel_id)
					if i[2]:
						url = f'{self.usertag} hat auf Twitter folgendes Retweetet:\n{url}'
					asyncio.run_coroutine_threadsafe(channel.send(url), botloop)
					c.execute(f'UPDATE {self.table} SET _send=1 WHERE _id={i[0]}')

				Tconn.commit()

			sleep(30, not self.Stop)
		Tconn.close()

	def start(self):
		self.Thread.start()

	def stop(self):
		self.Stop = True
		self.Thread.join()


async def send_private(member, message=None, embed=None):
	DM = await member.create_dm()
	return await DM.send(content=message, embed=embed)


def daily_reset():
	while (time.localtime()!=RESET_TIME.timetuple()) and alive:
		None
	if alive:
		# # renew subsciptions
		# for login in TwitchFeeds:
		# 	asyncio.run_coroutine_threadsafe(SERVER.HookStream(loginName=login, mode="subscribe"), botloop)
		try: RESTART(mode="restart")
		except: None


def timestring(deltatime):
	hours = int(deltatime.seconds/60/60)
	minutes = int((deltatime.seconds-hours*60*60)/60)
	seconds = int((deltatime.seconds-hours*60*60-minutes*60))
	time = [("h", hours), ("m", minutes), ("s", seconds)]
	String = ""
	for i in time:
		if i[1] > 0:
			String += f"{i[1]} {i[0]}, "
	return String[0:len(String)-2]


async def twitchOffMessage(topic, NOW):
	Server = SocketServer.Handler(TWITCH_CLIENTID, TWITCH_SECRET, TWITCH_CALLBACK)
	headers = {
			'Authorization': await Server.getToken(),
			'Client-Id': Server.CLIENTID
	}
	User = await Server.GETRequest(
		url='https://api.twitch.tv/helix/users',
		params={'id': topic},
		headers=headers
	)
	data = User['data'][0]

	UserID = User['data'][0]['id']
	UserName = User['data'][0]['login']
	Video = await Server.GETRequest(
		url='https://api.twitch.tv/helix/videos',
		params={'user_id': topic},
		headers=headers
	)
	try:
		video = Video['data'][0]
		VOD_txt = f"[{video['title']}]({video['url']})\nClick on the Link or on one of the Timestamps above"
	except:
		video = {'url' : None}
		VOD_txt = "No Video found"

	# Make Stream_ofline_txt
	Stream_offline_txt = ""
	cursor.execute(f"SELECT * FROM twitch_{topic}")
	Times = cursor.fetchall()
	T = lambda x: datetime.strptime(x, '%a %b %d %X %z %Y')
	for i,Time in enumerate(Times):
		if i>0:
			T1 = T(Times[i-1][0])-T(Times[0][0])
			T2 = T(Time[0])-T(Times[0][0])
			dT = T2-T1
			Stream_offline_txt += f"[`{str(T1).split('.', 2)[0]}-{str(T2).split('.', 2)[0]}`]({video['url']}?t={T1.seconds}s) **{Times[i-1][1]}** {timestring(dT)}\n"

	Embed = discord.Embed(timestamp=NOW, color=0x363636)
	Embed.set_author(name=f"{data['login']}", url=f"https://twitch.tv/{data['login']}", icon_url=f"{data['profile_image_url']}")
	Embed.set_image(url=f"{data['offline_image_url']}")
	Embed.set_thumbnail(url=f"{data['profile_image_url']}")
	Embed.set_footer(text="Last online")
	Embed.add_field(name="Games played", value=Stream_offline_txt, inline=False)
	Embed.add_field(name="Stream Video", value=VOD_txt, inline=False)
	return (Embed, UserName)


async def twitchOnMessage(topic, NOW, footer, Data):
	Server = SocketServer.Handler(TWITCH_CLIENTID, TWITCH_SECRET, TWITCH_CALLBACK)
	headers = {
			'Authorization': await Server.getToken(),
			'Client-Id': Server.CLIENTID
	}
	User = await Server.GETRequest(
		url='https://api.twitch.tv/helix/users',
		params={'id': topic},
		headers=headers
	)
	data = User['data'][0]
	# f"[{Data['title']}](https://twitch.tv/{data['login']})"

	Embed = discord.Embed(title=f"{Data['title']}", timestamp=NOW, color=0xad61bd, url=f"https://twitch.tv/{data['login']}")
	Embed.set_author(name=f"{data['login']}", url=f"https://twitch.tv/{data['login']}", icon_url=f"{data['profile_image_url']}")
	Embed.set_thumbnail(url=f"{data['profile_image_url']}")
	Embed.set_footer(text=f"{footer}")
	if Data['game_name']:
		Embed.add_field(name="Game", value=f"{Data['game_name']}")
	else:
		Embed.add_field(name="Game", value="No Game")
	Embed.set_image(url=f"{Data['thumbnail_url'].replace('{width}x{height}', '1280x720')}?cb={int(time.mktime(NOW.timetuple()))}")
	return Embed


def data_handler(query):
	_NOW = datetime.now()
	timezone = pytz.timezone("Europe/Berlin")
	NOW = timezone.localize(_NOW)
	print(f"Request at {NOW}:\n{query}\n")

	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	
	Data = query['data']
	UserID = int(query['topic'])

	# Creates Table for Topic if not exists and updates stream change for later usage
	cursor.execute(f"CREATE TABLE IF NOT EXISTS twitch_{UserID} (_timestamp TEXT, _game TEXT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;")

	# 'twitch_feeds (_guild_id BIGINT, _channel_id BIGINT, _topic_id BIGINT, _message_id BIGINT)')
	cursor.execute(f"SELECT * FROM twitch_feeds WHERE _topic_id={UserID}")
	Feeds = cursor.fetchall()
	
	# type(Data) = array and right now only a Stream Topic,
	# if Change in Future necessary, scan over request.path and change callback properly,
	# or make a different handler for every callback
	if Data:
		data = Data[0]
		cursor.execute(f"INSERT INTO twitch_{UserID} VALUES ('{NOW.strftime('%a %b %d %X %z %Y')}','{s(data['game_name'])}')")
		# data has content, upgrade existing message (if message_id is not 0), or create message (and update message_id):
		for feed in Feeds:
			guild = discord.utils.get(bot.guilds, id=int(feed[0]))
			channel = discord.utils.get(guild.channels, id=int(feed[1]))
			if feed[3]:
				message = asyncio.run_coroutine_threadsafe(channel.fetch_message(int(feed[3])), botloop)
				message = message.result()
				embed = loop.run_until_complete(twitchOnMessage(topic=UserID, NOW=NOW, footer="Streaming", Data=data))
				asyncio.run_coroutine_threadsafe(message.edit(content=f"**{data['user_login']}** is now online!\nhttps://twitch.tv/{data['user_login']}", embed=embed), botloop)
			else:
				embed = loop.run_until_complete(twitchOnMessage(topic=UserID, NOW=NOW, footer="Started streaming", Data=data))
				message = asyncio.run_coroutine_threadsafe(channel.send(content=f"**{data['user_login']}** is now online!\nhttps://twitch.tv/{data['user_login']}", embed=embed), botloop)
				message = message.result()
				cursor.execute(f"UPDATE twitch_feeds SET _message_id={message.id} WHERE _topic_id={UserID} AND _channel_id={channel.id}")	
	else:
		cursor.execute(f"INSERT INTO twitch_{UserID} VALUES ('{NOW.strftime('%a %b %d %X %z %Y')}','')")
		OffMessage, UserName = loop.run_until_complete(twitchOffMessage(topic=UserID, NOW=NOW))
		# data is empty, upgrade message to offline_message and set message_id to 0
		for feed in Feeds:
			guild = discord.utils.get(bot.guilds, id=int(feed[0]))
			channel = discord.utils.get(guild.channels, id=int(feed[1]))
			message = asyncio.run_coroutine_threadsafe(channel.fetch_message(int(feed[3])), botloop)
			message = message.result()
			asyncio.run_coroutine_threadsafe(message.edit(content=f"**{UserName}** was online" ,embed=OffMessage), botloop)
			# clean Database
			cursor.execute(f"UPDATE twitch_feeds SET _message_id=0 WHERE _topic_id={UserID} AND _channel_id={channel.id}")
		# delete topic database:
		cursor.execute(f"DROP TABLE twitch_{UserID}")
	
	conn.commit()

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
	conn.commit()

	# check if Guild is registered:
	for Guild in bot.guilds:
		cursor.execute(f'SELECT _id FROM guilds WHERE _id={Guild.id}')
		if not cursor.fetchone():
			await on_guild_join(Guild)
		else:
			await on_guild_update(Guild, Guild)

	print(f'{bot.user.name} has connected to Discord!')

	# subscribe to Twitch_Topics:
	cursor.execute(f"SELECT _login FROM twitch_topics")
	Topics = cursor.fetchall()
	for topic in Topics:
		await SERVER.HookStream(topic[0], "subscribe")
		TwitchFeeds.append(topic[0])
	
	print("Successfully subscribed to Twitch_Topics")

	Preference_Thread.start()
	print('Preference has started')

	# start Twitter-Threads
	for thread in THREADS:
		thread[0].start()

	print("Twitter-Threads have started\n")


@bot.event
async def on_command_error(ctx, error):
	try:
		prefix = getter("_prefix", "guilds", "_id", ctx.guild.id)
		await ctx.send(str(error) + f". Try {prefix}help bzw. {prefix}help command for more infos.")
	except:
		prefix = STDPREFIX
		await ctx.send(str(error) + f". Try {prefix}help bzw. {prefix}help command for more infos.")


@bot.event
async def on_guild_join(guild):
	# add guild to DB:
	t = (guild.id, guild.name, STDPREFIX, 0, False, )
	cursor.execute(f'INSERT INTO guilds VALUES ({t[0]},"{s(t[1])}","{s(t[2])}",{t[3]},{t[4]});')

	# add all members of guild to DB:
	for member in guild.members:
		await on_member_join(member)
	conn.commit()


@bot.event
async def on_guild_remove(guild):
	global THREADS

	# delete guild:
	cursor.execute(f'DELETE FROM guilds WHERE _id={guild.id}')
	# delete members on guild:
	cursor.execute(f'DELETE FROM members WHERE _guild={guild.id}')
	# delete sr_messages and bonds:
	cursor.execute(f'DELETE FROM sr_messages WHERE _guild_id={guild.id}')
	cursor.execute(f'DELETE FROM bonds WHERE _guild_id={guild.id}')
	# delete stdrole_message:
	os.remove(PATH + f"/stdrole_messages/{guild.id}.txt")

	# delete Twitch_Feeds and Tables:
	cursor.execute(f'SELECT * FROM twitch_feeds WHERE _guild_id={guild.id}')
	Feeds = cursor.fetchall()
	for feed in Feeds:
		cursor.execute(f'SELECT _login FROM twitch_topics WHERE _topic_id={feed[2]}')
		login = cursor.fetchone()
		await subscription(guild, None, login[0], feed[1], "unsubscribe")

	# delete twitter feeds and tables:
	cursor.execute(f'SELECT * FROM twitter WHERE _guild_id={guild.id};')
	Feeds = cursor.fetchall()
	for feed in Feeds:
		for i, thread in enumerate(THREADS):
			if thread[1] == feed[4]:
				thread[0].stop()
				del THREADS[i]
				break

		cursor.execute(f'DELETE FROM twitter WHERE _feed_id={feed[4]};')
		cursor.execute(f'DROP TABLE twitter_{feed[4]};')
	conn.commit()


@bot.event
async def on_guild_update(before, after):
	t = (after.name, )
	cursor.execute(f'UPDATE guilds SET _name="{s(t[0])}" WHERE _id={after.id}')
	conn.commit()


@bot.event
async def on_guild_channel_delete(channel):
	global THREADS

	# delete sr_messages:
	cursor.execute(f'DELETE FROM sr_messages WHERE _message_id={channel.id} AND _guild_id={guild.id}')

	# delete Twitch_Feeds and Tables:
	cursor.execute(f'SELECT * FROM twitch_feeds WHERE _channel_id={channel.id} AND _guild_id={channel.guild.id}')
	Feeds = cursor.fetchall()
	for feed in Feeds:
		cursor.execute(f'SELECT _login FROM twitch_topics WHERE _topic_id={feed[2]}')
		login = cursor.fetchone()
		await subscription(guild, None, login[0], feed[1], "unsubscribe")

	# delete twitter feeds and tables:
	cursor.execute(f'SELECT * FROM twitter WHERE _channel_id={channel.id} AND _guild_id={channel.guild.id};')
	Feeds = cursor.fetchall()
	for feed in Feeds:
		for i, thread in enumerate(THREADS):
			if thread[1] == feed[4]:
				thread[0].stop()
				del THREADS[i]
				break

		cursor.execute(f'DELETE FROM twitter WHERE _feed_id={feed[4]};')
		cursor.execute(f'DROP TABLE twitter_{feed[4]};')
	conn.commit()


# must be entered complete in stdrole.py
@bot.event
async def on_member_join(member):
	if member.bot:
		return

	# set registration status
	guild = member.guild
	stdrole = getter("_stdrole", "guilds", "_id", guild.id)
	if len(member.roles) == 1 and stdrole:
		regist = 2
	else:
		regist = 1

	# DB-registration
	t = (member.id, member.name, member.nick, guild.id, regist, )
	cursor.execute(f'INSERT INTO members VALUES ({t[0]},"{s(t[1])}","{s(t[2])}",{t[3]},{t[4]})')

	# send Registration-Message
	if regist >= 2 and stdrole:
		with open(file=PATH + f"/stdrole_messages/{guild.id}.txt", mode="r", encoding="utf8") as r:
			message = r.read()
		Message = await send_private(member, message)
		# (_message_id BIGINT, _guild_id BIGINT, _jump_url TEXT, _user_id BIGINT)
		cursor.execute(f'INSERT INTO sr_messages VALUES ({Message.id},{guild.id},"0",{member.id})')
		await Message.add_reaction(REGISTER_EMOJI_ACCEPT)
		await Message.add_reaction(REGISTER_EMOJI_DENY)
	conn.commit()


@bot.event
async def on_member_remove(member):
	if member.bot:
		return

	guild = member.guild
	# Delete members entry
	cursor.execute(f'DELETE FROM members WHERE _id={member.id} AND _guild={guild.id}')
	# Delete selfrole created for this Member within stdrole (selfrole ticket for stdrole)
	cursor.execute(f'DELETE FROM sr_messages WHERE _user_id={member.id} AND _guild_id={guild.id} AND _jump_url="0"')
	conn.commit()


@bot.event
async def on_member_update(before, after):
	if before.bot or after.bot:
		return

	guild = after.guild
	# update member:
	t = (after.nick, after.name)
	cursor.execute(f'UPDATE members SET _nick="{s(t[0])}", _name="{s(t[1])}" WHERE _id={after.id} AND _guild={guild.id}')
	conn.commit()

	# autodeletion of stdrole:
	if len(after.roles) > 1:
		Guest = discord.utils.get(after.roles, id=getter("_stdrole", "guilds", "_id", guild.id))

		if Guest:
			cursor.execute(f'SELECT _regist FROM members WHERE _id={after.id} AND _guild={guild.id}')
			regist = cursor.fetchone()[0]
			cursor.execute(f'SELECT _autodelete FROM guilds WHERE _id={guild.id}')
			autodelete = cursor.fetchone()[0]
			# if registered (because member has more than one Role):
			if regist >> 0 & 0x01 and len(after.roles) > 2 and autodelete:
				await after.remove_roles(Guest)
			elif regist >> 1 & 0x01:
				regist |= 0x01  # 3 is possible

			cursor.execute(f'UPDATE members SET _regist={regist} WHERE _id={after.id} AND _guild={guild.id}')

	conn.commit()


@bot.event
async def on_raw_reaction_add(payload):
	if payload.user_id == bot.user.id:
		return

	# stdrole:
	if not payload.guild_id:
		cursor.execute(f'SELECT _guild_id FROM sr_messages WHERE _jump_url="0" AND _user_id={payload.user_id} AND _message_id={payload.message_id}')
		guild_id = cursor.fetchone()
		if guild_id:

			cursor.execute(f'SELECT _stdrole FROM guilds WHERE _id={guild_id[0]}')
			stdrole = cursor.fetchone()[0]
			if stdrole:

				guild = discord.utils.get(bot.guilds, id=guild_id[0])
				member = discord.utils.get(guild.members, id=payload.user_id)
				# channel = discord.utils.get(bot.private_channels, id=payload.channel_id)
				channel = await member.create_dm()
				message = await channel.fetch_message(payload.message_id)
				if payload.emoji.name == REGISTER_EMOJI_ACCEPT:
					try:
						role = discord.utils.get(guild.roles, id=stdrole)
						await member.add_roles(role)
						cursor.execute(f'UPDATE members SET _regist=1 WHERE _id={payload.user_id} AND _guild={guild.id}')
						cursor.execute(f'DELETE FROM sr_messages WHERE _user_id={payload.user_id} AND _guild_id={guild.id} AND _jump_url="0"')
						await send_private(member, embed=discord.Embed(description=f"Willkommen auf dem {guild.name} Discord!"))
						await message.delete()
					except:
						raise commands.UserInputError(f"Registration failed, please contact an admin or the developer ({bot.owner.name})")
				elif payload.emoji.name == REGISTER_EMOJI_DENY:
					cursor.execute(f'DELETE FROM members WHERE _id={member.id} AND _guild={guild.id}')
					await send_private(member, embed=discord.Embed(description="Bedingungen müssen akzeptiert werden!"))
					await message.delete()
					await member.kick()
				conn.commit()
	# selfrole:
	elif payload.guild_id:
		# check if message id is in sr_messages:
		cursor.execute(f'SELECT _message_id FROM sr_messages WHERE _guild_id = {payload.guild_id} AND _message_id = {payload.message_id}')
		if cursor.fetchone():
			guild = discord.utils.get(bot.guilds, id=payload.guild_id)
			member = discord.utils.get(guild.members, id=payload.user_id)
			cursor.execute(f'SELECT _role_id, _emoji FROM bonds WHERE _guild_id={payload.guild_id}')
			for role_id in cursor.fetchall():
				if role_id[1] == payload.emoji.name:
					role = discord.utils.get(guild.roles, id=role_id[0])
					await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
	if not payload.guild_id or payload.user_id == bot.user.id:
		return

	# check if message id is in sr_messages:
	cursor.execute(f'SELECT _message_id FROM sr_messages WHERE _guild_id = {payload.guild_id} AND _message_id = {payload.message_id}')
	if cursor.fetchone():
		guild = discord.utils.get(bot.guilds, id=payload.guild_id)
		member = discord.utils.get(guild.members, id=payload.user_id)
		cursor.execute(f'SELECT _role_id, _emoji FROM bonds WHERE _guild_id = {payload.guild_id}')
		for role_id in cursor.fetchall():
			if role_id[1] == payload.emoji.name:
				role = discord.utils.get(guild.roles, id=role_id[0])
				await member.remove_roles(role)


@bot.event
async def on_raw_message_delete(payload):
	if not payload.guild_id:
		return
	cursor.execute(f'DELETE FROM sr_messages WHERE _message_id = {payload.message_id} AND _guild_id = {payload.guild_id}')
	conn.commit()

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


@bot.command(name='twitter_set', help=f'set channel for twitter_news twitter_tag without "@" usage: {STDPREFIX}twitter_set twitter_tag(without "@") channel')
@commands.has_guild_permissions(administrator=True)
async def twitter_set(ctx, twitter_tag: str, channel: str):
	global THREADS

	guild_id = ctx.guild.id
	Channel = discord.utils.get(ctx.guild.channels, name=channel)
	try:
		Channel = discord.utils.get(ctx.guild.channels, id=int(channel))
	except:
		try:
			Channel = discord.utils.get(ctx.guild.channels, id=int(channel[2:len(channel)-1]))
		except:
			Channel = discord.utils.get(ctx.guild.channels, name=channel)
	if not Channel: commands.UserInputError("Could not find channel")
	channel_id = Channel.id
	usertag = "@" + s(twitter_tag)

	cursor.execute(f'SELECT * FROM twitter WHERE _channel_id={channel_id} AND _usertag="{usertag}" AND _guild_id={guild_id};')
	if cursor.fetchone():
		raise commands.UserInputError("Twitter-Feed allready set")

	now = datetime.now()
	timezone = pytz.timezone("Europe/Berlin")
	now = timezone.localize(now)
	creation_time = now.strftime('%a %b %d %X %z %Y')

	cursor.execute('SELECT _feed_id FROM twitter ORDER BY _feed_id;')
	feed_id = 0
	for i, j in enumerate(cursor.fetchall()):
		if i != j[0]:
			feed_id = i
			break
		else:
			feed_id = i+1

	cursor.execute(f'INSERT INTO twitter VALUES ("{usertag}", {channel_id}, "{creation_time}", {guild_id}, {feed_id});')
	cursor.execute(f'CREATE TABLE IF NOT EXISTS twitter_{feed_id} (_rank BIGINT, _id BIGINT, _created_at TEXT, _send BOOL, _retweet BOOL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
	conn.commit()

	THREADS.append((checkTwitter(usertag=usertag, channel_id=channel_id, CREATION_TIME=creation_time, guild_id=guild_id, feed_id=feed_id), feed_id))
	THREADS[len(THREADS)-1][0].start()

	await Channel.send(embed=discord.Embed(description=f"Twitter-Feed for {usertag} successfully set in #{Channel.name}"))


@bot.command(name='twitter_delete', help=f'deletes news-feed, usage: {STDPREFIX}twitter_delete twitter_tag(without "@") channel')
@commands.has_guild_permissions(administrator=True)
async def twitter_delete(ctx, twitter_tag: str, channel: str):
	global THREADS

	guild_id = ctx.guild.id
	try:
		Channel = discord.utils.get(ctx.guild.channels, id=int(channel))
	except:
		try:
			Channel = discord.utils.get(ctx.guild.channels, id=int(channel[2:len(channel)-1]))
		except:
			Channel = discord.utils.get(ctx.guild.channels, name=channel)
	if not Channel: commands.UserInputError("Could not find channel")
	channel_id = Channel.id
	usertag = "@" + s(twitter_tag)

	cursor.execute(f'SELECT * FROM twitter WHERE _channel_id={channel_id} AND _usertag="{usertag}" AND _guild_id={guild_id};')
	feed = cursor.fetchone()
	if not feed:
		raise commands.UserInputError("News-Feed does not exist")

	for i, thread in enumerate(THREADS):
		if thread[1] == feed[4]:
			thread[0].stop()
			del THREADS[i]
			break

	cursor.execute(f'DELETE FROM twitter WHERE _feed_id={feed[4]};')
	cursor.execute(f'DROP TABLE twitter_{feed[4]};')
	conn.commit()
	await ctx.send(embed=discord.Embed(description=f"Twitter-Feed for {usertag} in #{Channel.name} successfully deleted"))


@bot.command(name='twitter_show', help='shows active twitter-feeds')
@commands.has_guild_permissions(administrator=True)
async def twitter_show(ctx):
	cursor.execute(f'SELECT _usertag, _channel_id, _creation_time FROM twitter WHERE _guild_id={ctx.guild.id};')
	Feeds = cursor.fetchall()
	if Feeds:
		Embed = discord.Embed(title="Twitter Feeds")
		for i, feed in enumerate(Feeds):
			channel = discord.utils.get(ctx.guild.channels, id=feed[1])
			Embed.add_field(name=f'#{channel.name}', value=f"Usertag: {feed[0]}\n Channel: {channel.name}\n Created at: {feed[2]}")
	else:
		Embed = discord.Embed(description="No Feeds found")
	await ctx.send(embed=Embed)


@bot.command(name='set_prefix', help=f'choose a new prefix for this Server (Private allways "{STDPREFIX}")')
@commands.has_guild_permissions(administrator=True)
async def set_prefix(ctx, prefix: str):
	guild = ctx.guild
	t = (s(prefix), )
	if t[0] and t[0] != "":
		cursor.execute(f'UPDATE guilds SET _prefix="{s(t[0])}" WHERE _id={guild.id}')
		conn.commit()
		await ctx.send(embed=discord.Embed(description=f'New Prefix set: "{getter("_prefix", "guilds", "_id", guild.id)}"'))
	else:
		raise commands.UserInputError("Prefix not allowed!")


@bot.command(name='stdrole', help=f'toggles autoregistration usage: {STDPREFIX}stdrole role(name or id) Message(as String, ID(same Channel) or txt-File-Attachement)')
@commands.has_guild_permissions(administrator=True)
async def stdrole(ctx, role_id, message_id=None):
	try:
		role = discord.utils.get(ctx.guild.roles, id=int(role_id))
		if not role:
			raise CustomError()
	except:
		role = discord.utils.get(ctx.guild.roles, name=role_id)

	if not message_id:
		try:
			message = await ctx.message.attachments[0].read()
			message = message.decode("utf-8")
		except:
			raise commands.UserInputError("No right attachement found")
	elif message_id:
		try:
			message = await ctx.channel.fetch_message(int(message_id[int(len(message_id)-18):]))
			message = message.content
			if not message:
				raise CustomError()
		except CustomError:
			raise commands.UserInputError("Could not find Message, make sure the Command is in the same Channel as the Message")
		except:
			message = message_id

	cursor.execute(f'UPDATE guilds SET _stdrole = {role.id} WHERE _id = {ctx.guild.id}')
	with open(file=PATH + f"/stdrole_messages/{ctx.guild.id}.txt", mode="w", encoding="utf8") as w:
		w.write(message)
	conn.commit()
	await ctx.send(embed=discord.Embed(description="standart-role set"))


@bot.command(name='stdrole_delete', help=f'turns off autoregistration and autodelete')
@commands.has_guild_permissions(administrator=True)
async def stdrole_delete(ctx):
	guild = ctx.guild
	cursor.execute(f'UPDATE guilds SET _stdrole = 0, _autodelete = {False} WHERE _id = {guild.id}')
	conn.commit()
	os.remove(PATH + f"/stdrole_messages/{guild.id}.txt")
	await ctx.send(embed=discord.Embed(description="autoregistration and autodelete successfully turned off"))


@bot.command(name='autodelete', help=f'toggles autodelete for stdrole if User has another Role, default = False, usage: {STDPREFIX}autodelete True/False')
@commands.has_guild_permissions(administrator=True)
async def autodelete(ctx, con: bool):
	cursor.execute(f'UPDATE guilds SET _autodelete = {con} WHERE _id = {ctx.guild.id}')
	conn.commit()
	await ctx.send(embed=discord.Embed(description=f"autodelete set to {con}"))


@bot.command(name='stdrole_show', help='shows stdrole and welcome-message')
@commands.has_guild_permissions(administrator=True)
async def stdrole_show(ctx):

	cursor.execute(f'SELECT _stdrole FROM guilds WHERE _id = {ctx.guild.id}')
	stdrole = cursor.fetchone()[0]
	role = discord.utils.get(ctx.guild.roles, id=stdrole)
	with open(file=PATH + f"/stdrole_messages/{ctx.guild.id}.txt", mode="r", encoding="utf8") as r:
		message = r.read()
	await ctx.send(f"**Role:** {role.name}\n\n**Message:**\n{message}")


@bot.command(name='sr_bond', help=f'binds emoji to role, usage: {STDPREFIX}sr_bond role(name or id) emoji')
@commands.has_guild_permissions(administrator=True)
async def sr_bond(ctx, role_id, emoji):
	guild = ctx.guild

	if type(role_id) == int:
		role = discord.utils.get(ctx.guild.roles, id=role_id)
	elif type(role_id) == str:
		role = discord.utils.get(ctx.guild.roles, name=role_id)

	cursor.execute(f'DELETE FROM bonds WHERE _role_id = {role.id} AND _emoji = "{emoji}" AND _guild_id = {guild.id}')
	cursor.execute(f'INSERT INTO bonds VALUES ({role.id}, "{emoji}", {guild.id})')
	conn.commit()
	await ctx.send(embed=discord.Embed(description=f"bond {role.name} -> {emoji} successfully created"))


@bot.command(name='sr_bond_delete', help=f'deletes bond of emoji to role, usage: {STDPREFIX}sr_bond_delete role(name or id) emoji')
@commands.has_guild_permissions(administrator=True)
async def sr_bond_delete(ctx, role_id, emoji):
	guild = ctx.guild

	if type(role_id) == int:
		role = discord.utils.get(ctx.guild.roles, id=role_id)
	elif type(role_id) == str:
		role = discord.utils.get(ctx.guild.roles, name=role_id)

	cursor.execute(f'DELETE FROM bonds WHERE _role_id = {role.id} AND _emoji = "{emoji}" AND _guild_id = {guild.id}')
	conn.commit()
	await ctx.send(embed=discord.Embed(description=f"bond {role.name} -> {emoji} successfully deleted"))


@bot.command(name='sr_bond_show', help=f'shows bonds of emojis to roles')
@commands.has_guild_permissions(administrator=True)
async def sr_bond_show(ctx):
	# check if role in bond still exists:
	cursor.execute(f'SELECT _role_id FROM bonds WHERE _guild_id = {ctx.guild.id}')
	for role in cursor.fetchall():
		if not ctx.guild.get_role(role[0]):
			cursor.execute(f'DELETE FROM bonds WHERE _role_id = {role[0]}')
			break
	conn.commit()
	Embed = discord.Embed(title="Active Bonds:\n\n")
	cursor.execute(f'SELECT _role_id, _emoji FROM bonds WHERE _guild_id = {ctx.guild.id}')
	for i, bond in enumerate(cursor.fetchall()):
		rolename = discord.utils.get(ctx.guild.roles, id=bond[0]).name
		Embed.add_field(name=f'Bond {i}:', value=f"{i}: {rolename} -> {bond[1]}")
	await ctx.send(embed=Embed)


@bot.command(name='sr_message', help=f'creates message for self-role or binds existing message, usage: {STDPREFIX}sr_message Message(as String or ID(same Channel)) emojis(*args, ...)')
@commands.has_guild_permissions(administrator=True)
async def sr_message(ctx, message_id=None, *args):
	try:
		message = await ctx.channel.fetch_message(int(message_id[int(len(message_id)-18):]))
		if not message:
			raise CustomError()
	except CustomError:
		raise commands.UserInputError("Could not find Message, make sure the Command is in the same Channel as the Message")
	except:
		message = await ctx.send(embed=discord.Embed(description=message_id))
	
	# test if Message allready exists in Database (then this is a update):
	cursor.execute(f'SELECT * FROM sr_messages WHERE _message_id={message.id} AND _guild_id={ctx.guild.id} AND _jump_url="{message.jump_url}" AND _user_id={message.author.id}')
	if not cursor.fetchone():
		cursor.execute(f'INSERT INTO sr_messages VALUES ({message.id}, {ctx.guild.id}, "{message.jump_url}", {message.author.id})')
	conn.commit()
	
	for emoji in args:
		try:
			await message.add_reaction(emoji)
		except:
			None


@bot.command(name='sr_message_show', help=f'shows created messages for self-role')
@commands.has_guild_permissions(administrator=True)
async def sr_message_show(ctx):
	Embed = discord.Embed(title="Active Self-Role Messages:")
	cursor.execute(f'SELECT _jump_url, _user_id FROM sr_messages WHERE _guild_id = {ctx.guild.id}')
	for i, msg in enumerate(cursor.fetchall()):
		user = discord.utils.get(ctx.guild.members, id=msg[1])
		Embed.add_field(name=f"Message {i}", value=f"Message [here]({msg[0]})\n created by <@{user.id}>")
	await ctx.send(embed=Embed)


async def subscription(guild, Channel, login_name, channel_id, mode):
	global TwitchFeeds

	if channel_id:
		try:
			channel = discord.utils.get(guild.channels, id=int(channel_id))
		except:
			try:
				channel = discord.utils.get(guild.channels, id=int(channel_id[2:len(channel_id)-1]))
			except:
				channel = discord.utils.get(guild.channels, name=channel_id)
		if not channel: channel = Channel
	else:
		channel = Channel

	User = await SERVER.GETRequest(
		url='https://api.twitch.tv/helix/users',
		params={'login': login_name},
		headers = {
			'Authorization': await SERVER.getToken(),
			'Client-Id': SERVER.CLIENTID
		}
	)
	try:
		UserID = User['data'][0]['id']
	except:
		raise CustomError("Twitch-Topic not found")

	if mode=="subscribe":
		cursor.execute(f'INSERT INTO twitch_feeds VALUES ({guild.id},{channel.id},{UserID},0)')

		Embed = discord.Embed(description=f"**Subscription successfully for [{login_name}](https://twitch.tv/{login_name}) in <#{channel.id}>**")

		cursor.execute(f'SELECT _topic_id FROM twitch_topics WHERE _topic_id={UserID}')
		if not cursor.fetchall():
			Response = await SERVER.HookStream(login_name, 'subscribe')
			if not Response:
				cursor.execute(f'INSERT INTO twitch_topics VALUES ({UserID}, "{s(login_name)}")')
				TwitchFeeds.append(login_name)
				conn.commit()
				return (None, Embed)
			else:
				conn.commit()
				return (Response, None)
		
		conn.commit()
		return (None, Embed)

	elif mode=="unsubscribe":
		cursor.execute(f'DELETE FROM twitch_feeds WHERE _guild_id={guild.id} AND _channel_id={channel.id} AND _topic_id={UserID}')

		Embed = discord.Embed(description=f"**Successfully unsubscribed for [{login_name}](https://twitch.tv/{login_name}) in <#{channel.id}>**")

		# if no feeds for topic left, delete Topic as well and unsubscribe:
		cursor.execute(f'SELECT * FROM twitch_feeds WHERE _topic_id={UserID}')
		if not cursor.fetchall():
			Response = await SERVER.HookStream(login_name, 'unsubscribe')
			if not Response:
				cursor.execute(f'DELETE FROM twitch_topics WHERE _topic_id={UserID}')
				TwitchFeeds.remove(login_name)
				try:
					cursor.execute(f"DROP TABLE twitch_{UserID}")
				except:
					None
				conn.commit()
				return (None, Embed)
			else:
				conn.commit()
				return (Response, None)

		conn.commit()
		return (None, Embed)


@bot.command(name='twitch_sub', help=f'creates Twitch-Topic subscription (leave Channel empty if calling from same channel), \
	usage: {STDPREFIX}twitch_sub login_name login_name Channel[optional]')
@commands.has_guild_permissions(administrator=True)
async def twitch_sub(ctx, login_name : str, Channel = None):
	content, embed = await subscription(ctx.guild, ctx.channel, login_name, Channel, "subscribe")
	await ctx.send(content=content, embed=embed)


@bot.command(name='twitch_unsub', help=f'unsub from existing Twitch-Topic (leave Channel empty if calling from same channel), \
	usage: {STDPREFIX}twitch_unsub login_name Channel[optional]')
@commands.has_guild_permissions(administrator=True)
async def twitch_unsub(ctx, login_name : str, Channel = None):
	content, embed = await subscription(ctx.guild, ctx.channel, login_name, Channel, "unsubscribe")
	await ctx.send(content=content, embed=embed)


@bot.command(name='twitch_show', help=f'shows active twitch_feeds for this Channel')
@commands.has_guild_permissions(administrator=True)
async def twitch_show(ctx):
	cursor.execute(f'SELECT _channel_id, _topic_id FROM twitch_feeds WHERE _guild_id={ctx.guild.id}')
	Feeds = cursor.fetchall()
	Embed = discord.Embed(title="Twitch Feeds")
	for feed in Feeds:
		Channel = discord.utils.get(ctx.guild.channels, id=feed[0])
		Name = getter('_login', 'twitch_topics', '_topic_id', feed[1])
		Embed.add_field(name=f'<#{Channel.name}>', value=f"[{Name}](https://twitch.tv/{Name})")
	await ctx.send(embed=Embed)


@bot.command(name='show_subs', hidden=True)
@commands.is_owner()
async def show_subs(ctx):
	headers={
			'Authorization': await SERVER.getToken(),
			'Client-Id': SERVER.CLIENTID
		}
	Subs = await SERVER.GETRequest(
		url="https://api.twitch.tv/helix/webhooks/subscriptions",
		params=None,
		headers=headers
	)
	
	Embed = discord.Embed(title=f"{Subs['total']} active Twitch subscriptions found")
	user_list = []
	sub_infos = []
	
	for sub in Subs['data']:
		user_list.append( ['id', str(int(sub['topic'].replace("https://api.twitch.tv/helix/streams?user_id=", "")))] )
	
	Users = await SERVER.GETRequest(
		url="https://api.twitch.tv/helix/users",
		params=user_list,
		headers=headers
	)

	for i, user in enumerate(Users['data']):
		data = Subs['data'][i]
		Embed.add_field(name=f'{user["login"]}', value=f'callback: {data["callback"]}\nexpires_at: {data["expires_at"]}')

	await ctx.send(embed=Embed)


@bot.command(name='register_guild', help='registers Guild. WARNING: deletes Meta-Data if Guild allready exists')
@is_guild_owner()
async def register_guild(ctx):
	guild = ctx.guild
	await on_guild_remove(guild)
	await on_guild_join(guild)
	await guild.owner.send(embed=discord.Embed(description='Guild successfully registered!'))


@bot.command(name='register', help='register yourself. WARNING: deletes your Meta-Data')
@is_in_guild()
async def register(ctx):
	member = ctx.author
	await on_member_remove(member)
	await on_member_join(member)


@bot.command(name='bip', help='bop')
async def bip(ctx):
	await ctx.send('bop')


# @bot.command(name='test', hidden=True)
# @commands.is_owner()
# async def test(ctx, *args):
# 	global RESET_TIME
# 	RESET_TIME = timezone.localize( datetime.now() )


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


@bot.command(name='dice', help=f'just a variable dice, usage {STDPREFIX}dice sites(=6)')
async def roll_dice(ctx, sites=6):
	if sites==0:
		Random = 0
	elif sites<0:
		Random = -np.random.randint(1, -sites+1)
	else:
		Random = np.random.randint(1, sites+1)
	await ctx.send(embed=discord.Embed(description=f"**D{sites}:**\n\n {Random}"))


@bot.command(name='rand', help=f'get a random number between start and stop')
async def rand(ctx, start, stop, Type=int):
	if type(Type)==str:
		try: Type=eval(Type)
		except: raise commands.UserInputError("Type not Supported, only int or float")
	Random = (int(stop)-int(start))*np.random.random()+int(start)
	if Type==int:
		Random = int(np.round(Random))
	await ctx.send(embed=discord.Embed(description=f"**Random between {start} and {stop} as {Type}:**\n\n {Random}"))


@bot.command(name='avatar', help='get avatar_url of member as format ‘webp’, ‘jpeg’, ‘jpg’, ‘png’ or ‘gif’ (default is ‘webp’)')
async def avatar(ctx, Member, Format="webp"):
	try:
		MEMBER = discord.utils.get(ctx.guild.members, id=int(Member[3:len(Member)-1]))
	except:
		MEMBER = discord.utils.get(ctx.guild.members, name=str(Member))
	await ctx.send(str(MEMBER.avatar_url_as(format=Format)))
	

@bot.command(name='rand_user', help='get random User on Server')
async def raffle(ctx):
	guild = ctx.guild
	rand_user = np.random.choice(guild.members)
	while rand_user.bot:
		rand_user = np.random.choice(guild.members)
	await ctx.send(embed=discord.Embed(description=f"<{rand_user.id}>"))


def StopServer():
	# unsubscribe for every existing Topics
	print("start Server shutdown!")
	for login in TwitchFeeds:
		asyncio.run_coroutine_threadsafe(SERVER.HookStream(loginName=login, mode="unsubscribe"), botloop)
	print("unsubscribed to all topics, waiting 10 seconds:")
	time.sleep(10) # to make sure handler is ready, increase time when neccessery
	SERVER.stop()
	print("done")
	return True


def SHUTDOWN(mode="shutdown"):
	global alive
	alive = False

	print("starting shutdown")
	if mode=="shutdown":
		StopServer()
	botloop.create_task(bot.logout())

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
		for thread in THREADS:
			thread[0].stop()
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


Preference_Thread = Thread(target=Preference)

Reset_Thread = Thread(target=daily_reset)
Reset_Thread.start()

# create Twitch-Thread
SERVER = SocketServer.Handler(
	CLIENTID=TWITCH_CLIENTID,
	SECRET=TWITCH_SECRET,
	CALLBACK=TWITCH_CALLBACK,
	DataHandler=data_handler
)

SERVER.start()
TwitchFeeds = []

# create Twitter-Threads
cursor.execute('SELECT * FROM twitter')
Feeds = cursor.fetchall()
for feed in Feeds:
	THREADS.append((checkTwitter(usertag=feed[0], channel_id=feed[1], CREATION_TIME=feed[2], guild_id=feed[3], feed_id=feed[4]), feed[4]))

botloop.run_until_complete(bot.start(TOKEN))

print("Bot has logged out")
