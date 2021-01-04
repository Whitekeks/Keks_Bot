import os, sys, psutil, logging, discord, time, asyncio, pytz, twitter
from dotenv import load_dotenv
from discord.ext import commands
from threading import Thread
import numpy as np
from datetime import datetime
import mysql.connector

SEED = str(np.random.randint(0,int(2.e9)))

print("starting...")

"""--------------environment variables------------------"""

PATH = os.path.dirname(os.path.abspath(__file__))
if not os.path.isfile(f'{PATH}/TOKEN_BOT.env'):
	print("TOKEN_BOT.env not found! Creating new:")
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
	with open(f'{PATH}/TOKEN_BOT.env', 'w') as w:
		w.write(f"# .env\nTOKEN={TOKEN}\nTWITTER_CONSUMER_KEY={TWITTER_CONSUMER_KEY}\nTWITTER_CONSUMER_SECRET={TWITTER_CONSUMER_SECRET}\nTWITTER_ACCESS_TOKEN_KEY={TWITTER_ACCESS_TOKEN_KEY}\nTWITTER_ACCESS_TOKEN_SECRET={TWITTER_ACCESS_TOKEN_SECRET}\nKEY={SEED}")
else:
	load_dotenv(f'{PATH}/TOKEN_BOT.env')
	TOKEN = os.getenv('TOKEN')
	TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
	TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
	TWITTER_ACCESS_TOKEN_KEY = os.getenv('TWITTER_ACCESS_TOKEN_KEY')
	TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
	SEED = os.getenv('KEY')

print("env's set")

"""-------------------------Database---------------------------"""

#security for Database:
np.random.seed(int(SEED))
KEY = np.random.rand()
now = datetime.now()
timezone = pytz.timezone("Europe/Berlin")
now = timezone.localize(now)


class CustomError(Exception):
	pass

#create Database:
conn = mysql.connector.connect(
	host="localhost",
	user="Whitekeks",
	password="Ludado80",
	database='Open_End'
)
cursor = conn.cursor(buffered=True)

#create tables if they do not exist:
cursor.execute('CREATE TABLE IF NOT EXISTS guilds (_id BIGINT, _name TEXT, _prefix TEXT, _stdrole BIGINT, _message TEXT, _autodelete BOOL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
cursor.execute('CREATE TABLE IF NOT EXISTS members (_id BIGINT, _name TEXT, _nick TEXT, _guild BIGINT, _regist BIGINT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
cursor.execute('CREATE TABLE IF NOT EXISTS twitter (_usertag TEXT, _channel_id BIGINT, _creation_time TEXT, _guild_id BIGINT, _feed_id BIGINT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
cursor.execute('CREATE TABLE IF NOT EXISTS bonds (_role_id BIGINT, _emoji TEXT, _guild_id BIGINT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
cursor.execute('CREATE TABLE IF NOT EXISTS sr_messages (_message_id BIGINT, _guild_id BIGINT, _jump_url TEXT, _user_id BIGINT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
cursor.execute('CREATE TABLE IF NOT EXISTS bot (_key DOUBLE, _creation_time TEXT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')

#check if key is right:
cursor.execute(f'SELECT _key FROM bot WHERE _key={KEY}')

# # Old Setup, now Secured over MySQL
# if not cursor.fetchone():
# 	#if key is not the same or does not exist, raise error:
# 	raise CustomError("End_Bot.db corrupted! To fix this problem simply delete End_Bot.db")
# else:
# 	g = (KEY, now.strftime('%a %b %d %X %z %Y'), 722511309622607922,  )
# 	cursor.execute(f'INSERT INTO bot VALUES ({g[0]},"{g[1]}",{g[2]})')

# if Bot does not Exist:
if not cursor.fetchone():
	g = (KEY, now.strftime('%a %b %d %X %z %Y'), 722511309622607922,  )
	cursor.execute(f'INSERT INTO bot VALUES ({g[0]},"{g[1]}")')

conn.commit()
print("database set")

"""------------------important functions---------------------"""

def s(dirtyString):
	cleanString = None
	if dirtyString:
		cleanString = dirtyString.translate({ord(i): None for i in [";"]})
	return cleanString

def getter(item, table, column, value):
	"""cursor.execute(f'SELECT {item} FROM {table} WHERE {column}={value}')
	WARNING: if type(value) == String then value must be f'\"{value}\"' """
	cursor.execute(f'SELECT {item} FROM {table} WHERE {column}={value}')
	return cursor.fetchone()[0]

def Prefix(Bot, Message):
	try :
		pfx = getter("_prefix", "guilds", "_id", Message.guild.id)
	except:
		pfx = STDPREFIX
	return pfx

"""---------------------Bot-----------------------------"""

bot = commands.Bot(command_prefix=Prefix, intents=discord.Intents.all())
botloop = asyncio.get_event_loop()
# Games = ["v. 1.2.2","/help for infos","try /bip","!shutdown don't...", "/restart: While True: Bot()",\
# 		"/set_prefix nobody is Safe", "/register_guild with the boys", "/register without the boys"]
Games = ["v. 1.3.1","/help for infos"]

print("bot set")

"""---------------------Twitter-------------------------"""

twitter_api = twitter.Api(consumer_key=TWITTER_CONSUMER_KEY,
				consumer_secret=TWITTER_CONSUMER_SECRET,
				access_token_key=TWITTER_ACCESS_TOKEN_KEY,
				access_token_secret=TWITTER_ACCESS_TOKEN_SECRET)

print("twitter set")


"""----------------------Globals------------------------"""

with open(f'{PATH}/register_message.txt', 'r') as w:
	REGISTER_MESSAGE = w.read()

REGISTER_EMOJI_ACCEPT = "👍"
REGISTER_EMOJI_DENY = "👎"
GUEST_ROLE = "Gast" # todo
BOT_CREATION_TIME = datetime.strptime(getter("_creation_time", "bot", "_key", KEY), '%a %b %d %X %z %Y') #type = datetime
# GUILD_ID = 722511309622607922 #for twitter-thread, here fix for faster usage -> applied in on_ready
STDPREFIX = "/"
THREADS = []
alive = True

print("globals set")

"""---------------------functions----------------------"""

# custom sleep function which breaks when alive = False
def sleep(Interval, Condition=True):
	time_1 = time.time()
	while time.time()-time_1<Interval and alive and Condition:
		None

# changes the bots activity, just for misscalanios purpose
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

class checkTwitter:

	def __init__(self, **kwargs):

		self.CREATION_TIME = kwargs['CREATION_TIME']
		self.usertag = kwargs['usertag']
		self.feed_id = kwargs['feed_id']
		self.guild_id = kwargs['guild_id']
		self.channel_id = kwargs['channel_id']

		self.CREATION_TIME = datetime.strptime(self.CREATION_TIME, '%a %b %d %X %z %Y')
		self.Stop = False
		self.Thread = Thread(target=self.checkTwitter)
		self.table = f'twitter_{self.feed_id}'

	def checkTwitter(self):
		Tconn = mysql.connector.connect(
			host="localhost",
			user="Whitekeks",
			password="Ludado80",
			database='Open_End'
		)
		c = Tconn.cursor(buffered=True)

		while alive and not self.Stop:
			statuses = twitter_api.GetUserTimeline(screen_name=self.usertag, count=100)
			for rank, status in enumerate(statuses):
				#check if status.id exists:
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
			
			#send new tweets:
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

async def send_private(user, message):
	DM = await user.create_dm()
	return await DM.send(message)



"""----------------------- Events ----------------------------"""

@bot.event
async def on_ready():
	print("")
	print("Update DataBase...")
	
	#check for new members and missing guilds:
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
					cursor.execute(f'DELETE FROM members WHERE _id={member_id[0]} AND _guild={guild.id}')
		else:
			cursor.execute(f'DELETE FROM guilds WHERE _id={ID[0]}')
	
	#check if Guild is registered:
	for Guild in bot.guilds:
		cursor.execute(f'SELECT _id FROM guilds WHERE _id={Guild.id}')
		if not cursor.fetchone():
			await on_guild_join(Guild)

	conn.commit()

	print(f'{bot.user.name} has connected to Discord!')
	
	Preference_Thread.start()
	print('Preference has started')

	# start Twitter-Threads
	for thread in THREADS:
		thread[0].start()

	print("Twitter-Threads have started")


@bot.event
async def on_command_error(ctx, error):
	with open("err.log", "a") as a:
		a.write(f"From {ctx.author.name}, command error: {error}\n")
	print(error)
	try:
		prefix = getter("_prefix", "guilds", "_id", ctx.guild.id)
		await ctx.send(str(error) + f". Try {prefix}help bzw. {prefix}help command for more infos.")
	except:
		prefix = STDPREFIX
		await ctx.send(str(error) + f". Try {prefix}help bzw. {prefix}help command for more infos.")

@bot.event
async def on_guild_join(guild):
	#add guild to DB:
	t = (guild.id, guild.name, STDPREFIX, 0, '0', False, )
	cursor.execute(f'INSERT INTO guilds VALUES ({t[0]},"{s(t[1])}","{s(t[2])}",{t[3]},"{t[4]}",{t[5]});')	
	
	#add all members of guild to DB:
	for member in guild.members:
		await on_member_join(member)
	conn.commit()

@bot.event
async def on_guild_remove(guild):
	global THREADS

	#delete guild:
	cursor.execute(f'DELETE FROM guilds WHERE _id={guild.id}')
	#delete members on guild:
	cursor.execute(f'DELETE FROM members WHERE _guild={guild.id}')

	#delete twitter feeds and tables:
	cursor.execute(f'SELECT * FROM twitter WHERE _guild_id={guild.id};')
	Feeds = cursor.fetchall()
	for feed in Feeds:
		for i,thread in enumerate(THREADS):
			if thread[1]==feed[4]:
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

	cursor.execute(f'SELECT * FROM twitter WHERE _channel_id={channel.id} AND _guild_id={channel.guild.id};')
	Feeds = cursor.fetchall()
	for feed in Feeds:
		for i,thread in enumerate(THREADS):
			if thread[1]==feed[4]:
				thread[0].stop()
				del THREADS[i]
				break
		
		cursor.execute(f'DELETE FROM twitter WHERE _feed_id={feed[4]};')
		cursor.execute(f'DROP TABLE twitter_{feed[4]};')
	conn.commit()

@bot.event
async def on_member_join(member):
	guild = member.guild
	if not member.bot:
		stdrole = getter("_stdrole", "guilds", "_id", guild.id)
		if len(member.roles) == 1 and stdrole:
			regist = 2
		else:
			regist = 1

		t = (member.id, member.name, member.nick, guild.id, regist, )
		cursor.execute(f'INSERT INTO members VALUES ({t[0]},"{s(t[1])}","{s(t[2])}",{t[3]},{t[4]})')
		conn.commit()
		
		if regist >= 2 and stdrole:
			Message = await send_private(member, getter("_message", "guilds", "_id", guild.id))
			await Message.add_reaction(REGISTER_EMOJI_ACCEPT)
			await Message.add_reaction(REGISTER_EMOJI_DENY)
			return False
		return True

@bot.event
async def on_member_remove(member):
	if member.bot:
		return
	
	guild = member.guild
	cursor.execute(f'DELETE FROM members WHERE _id={member.id} AND _guild={guild.id}')
	conn.commit()

@bot.event
async def on_member_update(before, after):
	if before.bot or after.bot:
		return
	
	guild = after.guild
	#update member:
	t = (after.nick, after.name )
	cursor.execute(f'UPDATE members SET _nick="{s(t[0])}", _name="{s(t[1])}" WHERE _id={after.id} AND _guild={guild.id}')
	conn.commit()

	if len(after.roles)>1:
		Guest = discord.utils.get(after.roles, id=getter("_stdrole", "guilds", "_id", guild.id))
		
		if Guest:
			cursor.execute(f'SELECT _regist FROM members WHERE _id={after.id} AND _guild={guild.id}')
			regist = cursor.fetchone()[0]
			cursor.execute(f'SELECT _autodelete FROM guilds WHERE _id={guild.id}')
			autodelete = cursor.fetchone()[0]
			# if registered (because member has more than one Role):
			if regist>>0 & 0x01 and len(after.roles)>2 and autodelete:
				await after.remove_roles(Guest)
			elif regist>>1 & 0x01:
				regist |= 0x01 # 3 is possible

			cursor.execute(f'UPDATE members SET _regist={regist} WHERE _id={after.id} AND _guild={guild.id}')
	
	conn.commit()

@bot.event
async def on_reaction_add(reaction, user):
	if user.bot:
		return

	if reaction.message.channel.type == discord.ChannelType.private:
		
		cursor.execute(f'SELECT _guild FROM members WHERE _id={user.id} AND _regist>=2')
		GUILDS = cursor.fetchall()
		for ID in GUILDS:
			
			cursor.execute(f'SELECT _message, _stdrole FROM guilds WHERE _id={ID[0]}')
			regis_message, stdrole = cursor.fetchone()
			if stdrole and s(reaction.message.content)==regis_message:

				guild = discord.utils.get(bot.guilds, id=ID[0])
				member = discord.utils.get(guild.members, id=user.id)
				if reaction.emoji==REGISTER_EMOJI_ACCEPT:
					try:
						role = discord.utils.get(guild.roles, id=stdrole)
						await member.add_roles(role)			
						cursor.execute(f'UPDATE members SET _regist=1 WHERE _id={user.id} AND _guild={guild.id}')
						await user.send(f"Willkommen auf dem {guild.name} Discord!")
						await reaction.message.delete()
					except:
						raise commands.UserInputError("Registration failed, please contact an admin or the developer (Whitekeks)")
				elif reaction.emoji==REGISTER_EMOJI_DENY:
					cursor.execute(f'DELETE FROM members WHERE _id={member.id} AND _guild={guild.id}')
					await user.send("Bedingungen müssen akzeptiert werden!")
					await reaction.message.delete()
					await member.kick()
				conn.commit()

@bot.event
async def on_raw_reaction_add(payload):
	if not payload.guild_id or payload.user_id==bot.user.id:
		return

	# check if message id is in sr_messages:
	cursor.execute(f'SELECT _message_id FROM sr_messages WHERE _guild_id = {payload.guild_id} AND _message_id = {payload.message_id}')
	if cursor.fetchone():
		guild = discord.utils.get(bot.guilds, id=payload.guild_id)
		member = discord.utils.get(guild.members, id=payload.user_id)
		cursor.execute(f'SELECT _role_id, _emoji FROM bonds WHERE _guild_id={payload.guild_id}')
		for role_id in cursor.fetchall():
			if role_id[1]==payload.emoji.name:
				role = discord.utils.get(guild.roles, id=role_id[0])
				await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
	if not payload.guild_id or payload.user_id==bot.user.id:
		return

	# check if message id is in sr_messages:
	cursor.execute(f'SELECT _message_id FROM sr_messages WHERE _guild_id = {payload.guild_id} AND _message_id = {payload.message_id}')
	if cursor.fetchone():
		guild = discord.utils.get(bot.guilds, id=payload.guild_id)
		member = discord.utils.get(guild.members, id=payload.user_id)
		cursor.execute(f'SELECT _role_id, _emoji FROM bonds WHERE _guild_id = {payload.guild_id}')
		for role_id in cursor.fetchall():
			if role_id[1]==payload.emoji.name:
				role = discord.utils.get(guild.roles, id=role_id[0])
				await member.remove_roles(role)

@bot.event
async def on_raw_message_delete(payload):
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
async def twitter_set(ctx, twitter_tag : str, channel : str):
	global THREADS

	guild_id = ctx.guild.id
	Channel = discord.utils.get(ctx.guild.channels, name=channel)
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
	for i,j in enumerate(cursor.fetchall()):
		if i!=j[0]:
			feed_id = i
			break
		else:
			feed_id = i+1

	cursor.execute(f'INSERT INTO twitter VALUES ("{usertag}", {channel_id}, "{creation_time}", {guild_id}, {feed_id});')
	cursor.execute(f'CREATE TABLE IF NOT EXISTS twitter_{feed_id} (_rank BIGINT, _id BIGINT, _created_at TEXT, _send BOOL, _retweet BOOL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
	conn.commit()

	THREADS.append( (checkTwitter(usertag=usertag, channel_id=channel_id, CREATION_TIME=creation_time, guild_id=guild_id, feed_id=feed_id), feed_id) )
	THREADS[len(THREADS)-1][0].start()

	await Channel.send(f"Twitter-Feed for {usertag} successfully set in #{Channel.name}")

@bot.command(name='twitter_delete', help=f'deletes news-feed, usage: {STDPREFIX}twitter_delete twitter_tag(without "@") channel')
@commands.has_guild_permissions(administrator=True)
async def twitter_delete(ctx, twitter_tag : str, channel : str):
	global THREADS

	guild_id = ctx.guild.id
	Channel = discord.utils.get(ctx.guild.channels, name=channel)
	channel_id = Channel.id
	usertag = "@" + s(twitter_tag)

	cursor.execute(f'SELECT * FROM twitter WHERE _channel_id={channel_id} AND _usertag="{usertag}" AND _guild_id={guild_id};')
	feed = cursor.fetchone()
	if not feed:
		raise commands.UserInputError("News-Feed does not exist")
	
	for i,thread in enumerate(THREADS):
		if thread[1]==feed[4]:
			thread[0].stop()
			del THREADS[i]
			break
	
	cursor.execute(f'DELETE FROM twitter WHERE _feed_id={feed[4]};')
	cursor.execute(f'DROP TABLE twitter_{feed[4]};')
	conn.commit()
	await Channel.send(f"Twitter-Feed for {usertag} in #{Channel.name} successfully deleted")

@bot.command(name='twitter_show', help='shows active twitter-feeds')
@commands.has_guild_permissions(administrator=True)
async def twitter_show(ctx):
	cursor.execute(f'SELECT _usertag, _channel_id, _creation_time FROM twitter WHERE _guild_id={ctx.guild.id};')
	Feeds = cursor.fetchall()
	if Feeds:
		Message = "The following Twitter-Feeds are active:\n\n"
		for i, feed in enumerate(Feeds):
			channel = discord.utils.get(ctx.guild.channels, id=feed[1])
			Message += f"Usertag: {feed[0]}, Channel: {channel.name}, Created at: {feed[2]}\n"
	else:
		Message = "No active feeds detected"
	await ctx.send(Message)

@bot.command(name='set_prefix', help=f'choose a new prefix for this Server (Private allways "{STDPREFIX}")')
@commands.has_guild_permissions(administrator=True)
async def set_prefix(ctx, prefix : str):
	guild = ctx.guild
	t = (s(prefix), )
	if t[0] and t[0]!="":
		cursor.execute(f'UPDATE guilds SET _prefix="{s(t[0])}" WHERE _id={guild.id}')
		conn.commit()
		await ctx.send(f'New Prefix set: "{getter("_prefix", "guilds", "_id", guild.id)}"')
	else:
		raise commands.UserInputError("Prefix not allowed!")

@bot.command(name='stdrole', help=f'toggles autoregistration usage: {STDPREFIX}stdrole role(name or id) Message(as String or txt-File-Attachement)')
@commands.has_guild_permissions(administrator=True)
async def stdrole(ctx, role_id, Message = None):
	if type(role_id) == int:
		role = discord.utils.get(ctx.guild.roles, id=role_id)
	elif type(role_id) == str:
		role = discord.utils.get(ctx.guild.roles, name=role_id)
	
	if not Message:
		message = await ctx.message.attachments[0].read()
		message = message.decode("utf-8")
	elif Message:
		message = Message
	
	cursor.execute(f'UPDATE guilds SET _stdrole = {role.id}, _message = "{s(message)}" WHERE _id = {ctx.guild.id}')
	conn.commit()
	await ctx.send("standart-role set")

@bot.command(name='stdrole_delete', help=f'turns off autoregistration and autodelete')
@commands.has_guild_permissions(administrator=True)
async def stdrole_delete(ctx):
	guild = ctx.guild
	t = (0, '0', False, )
	cursor.execute(f'UPDATE guilds SET _stdrole = {t[0]}, _message = "{t[1]}", _autodelete = {t[2]} WHERE _id = {guild.id}')	
	conn.commit()
	await ctx.send("autoregistration and autodelete successfully turned off")

@bot.command(name='autodelete', help=f'toggles autodelete for stdrole if User has another Role, usage {STDPREFIX}autodelete True/False')
@commands.has_guild_permissions(administrator=True)
async def autodelete(ctx, bed : bool):
	cursor.execute(f'UPDATE guilds SET _autodelete = {bed} WHERE _id = {ctx.guild.id}')
	conn.commit()
	await ctx.send(f"autodelete set to {bed}")

@bot.command(name='stdrole_show', help='shows stdrole and welcome-message')
@commands.has_guild_permissions(administrator=True)
async def stdrole_show(ctx):

	cursor.execute(f'SELECT _stdrole, _message FROM guilds WHERE _id = {ctx.guild.id}')
	stdrole, message = cursor.fetchone()
	role = discord.utils.get(ctx.guild.roles, id=stdrole)
	await ctx.send(f"Role: {role.name}\n\nMessage:\n{message}")

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
	await ctx.send(f"bond {role.name} -> {emoji} successfully created")

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
	await ctx.send(f"bond {role.name} -> {emoji} successfully deleted")

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
	message="Active Bonds:\n\n"
	cursor.execute(f'SELECT _role_id, _emoji FROM bonds WHERE _guild_id = {ctx.guild.id}')
	for i, bond in enumerate(cursor.fetchall()):
		rolename = discord.utils.get(ctx.guild.roles, id=bond[0]).name
		message += f"{i}: {rolename} -> {bond[1]}\n"
	await ctx.send(message)

@bot.command(name='sr_message', help=f'creates message for self-role or binds existing message, usage: {STDPREFIX}sr_message message(id (must be new) or str) emojis(*args, ...)')
@commands.has_guild_permissions(administrator=True)
async def sr_message(ctx, message_id, *args):
	try: 
		message = discord.utils.get(bot.cached_messages, id=int( message_id[ int(len(message_id)-18) :] ))
	except:
		message = await ctx.send(message_id)

	cursor.execute(f'INSERT INTO sr_messages VALUES ({message.id}, {ctx.guild.id}, "{message.jump_url}", {message.author.id})')
	conn.commit()
	for emoji in args:
		try: await message.add_reaction(emoji)
		except: None

@bot.command(name='sr_message_show', help=f'shows created messages for self-role')
@commands.has_guild_permissions(administrator=True)
async def sr_message_show(ctx):
	message = "Active Self-Role Messages:\n\n"
	cursor.execute(f'SELECT _jump_url, _user_id FROM sr_messages WHERE _guild_id = {ctx.guild.id}')
	for i, msg in enumerate(cursor.fetchall()):
		username = discord.utils.get(ctx.guild.members, id=msg[1]).name
		message += f"Message at {msg[0]} created by {username}\n"
	await ctx.send(message)

@bot.command(name='register_guild', help='registers Guild. WARNING: deletes Meta-Data if Guild allready exists')
@is_guild_owner()
async def register_guild(ctx):
	guild = ctx.guild
	await on_guild_remove(guild)
	await on_guild_join(guild)
	await guild.owner.send('Guild successfully registered!') 

@bot.command(name='register', help='register yourself. WARNING: deletes your Meta-Data')
@is_in_guild()
async def register(ctx):
	member = ctx.member
	await on_member_remove(member)
	await on_member_join(member)

@bot.command(name='bip', help='bop')
async def bip(ctx):
	await ctx.send('bop')
	print(ctx.author.roles,"len(roles):",len(ctx.author.roles))
	print(ctx.author.name, "bop")

@bot.command(name='test', hidden=True)
async def test(ctx, *args):
	# await ctx.send( int( args[0][ int(len(args[0])-18) :] ))
	# message = discord.utils.get(bot.cached_messages, id=int( args[0][ int(len(args[0])-18) :] ))
	# await ctx.send(message.content)

	for i in bot.cached_messages:
		print(i.content)

@bot.command(name='shutdown', help="shuts down the System")
@commands.is_owner()
async def shutdown(ctx):
	await ctx.send('Shutting down... Bye!')
	SHUTDOWN()

@bot.command(name='restart', help="restarts the System")
@commands.is_owner()
async def restart(ctx):
	await ctx.send('Restarting...')
	RESTART()

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

	# close running loops
	while True:
		try: 
			loop = asyncio.get_running_loop()
			loop.close()
		except:
			break

	try:
		alive = False
		Preference_Thread.join()
		for thread in THREADS:
			thread[0].stop()
	except: None

	conn.close()

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


Preference_Thread = Thread(target=Preference)

# create Twitter-Threads
cursor.execute('SELECT * FROM twitter')
Feeds = cursor.fetchall()
for feed in Feeds:
	THREADS.append( (checkTwitter(usertag=feed[0], channel_id=feed[1], CREATION_TIME=feed[2], guild_id=feed[3], feed_id = feed[4]), feed[4]) )

botloop.run_until_complete(bot.start(TOKEN))

print("Bot has logged out")
