import pytz
import discord
import time
import asyncio
from bin import SocketServer
import mysql.connector
from threading import Thread
from datetime import datetime
from discord.ext import commands
from bin.importantFunctions import s, sleep, STDPREFIX

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

class Twitch(commands.Cog):

	def __init__(self, bot, prefix, mysql_connector, botloop, CLIENTID, SECRET, CALLBACK):
		global STDPREFIX
		STDPREFIX = prefix
		self.SERVER = SocketServer.Handler(
			CLIENTID=CLIENTID,
			SECRET=SECRET,
			CALLBACK=CALLBACK,
			DataHandler=self.data_handler
		)
		self.bot = bot
		self.conn = mysql_connector
		self.cursor = self.conn.cursor(buffered=True)
		self.botloop = botloop
		self.TwitchFeeds = []
		
		print("Twitch set")

	def start(self):
		self.SERVER.start()
		print("Twitch Server started")

		# subscribe to Twitch_Topics:
		self.cursor.execute(f"SELECT _login FROM twitch_topics")
		Topics = self.cursor.fetchall()
		for topic in Topics:
			asyncio.run_coroutine_threadsafe(self.SERVER.HookStream(loginName=topic[0], mode="subscribe"), self.botloop)
			self.TwitchFeeds.append(topic[0])
		
		print("Successfully subscribed to Twitch_Topics")

	def stop(self):
		# unsubscribe for every existing Topics
		print("start Server shutdown!")
		for login in self.TwitchFeeds:
			asyncio.run_coroutine_threadsafe(self.SERVER.HookStream(loginName=login, mode="unsubscribe"), self.botloop)
		print("unsubscribed to all topics, waiting 10 seconds:")
		time.sleep(10) # to make sure handler is ready, increase time when neccessery
		self.SERVER.stop()
		print("done")

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		# delete Twitch_Feeds and Tables:
		self.cursor.execute(f'SELECT * FROM twitch_feeds WHERE _guild_id={guild.id}')
		Feeds = self.cursor.fetchall()
		for feed in Feeds:
			self.cursor.execute(f'SELECT _login FROM twitch_topics WHERE _topic_id={feed[2]}')
			login = self.cursor.fetchone()
			await self.subscription(guild, None, login[0], feed[1], "unsubscribe")
		self.conn.commit()

	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel):
		# delete Twitch_Feeds and Tables:
		self.cursor.execute(f'SELECT * FROM twitch_feeds WHERE _channel_id={channel.id} AND _guild_id={guild.id}')
		Feeds = self.cursor.fetchall()
		for feed in Feeds:
			self.cursor.execute(f'SELECT _login FROM twitch_topics WHERE _topic_id={feed[2]}')
			login = self.cursor.fetchone()
			await self.subscription(guild, None, login[0], feed[1], "unsubscribe")
		self.conn.commit()

	async def subscription(self, guild, Channel, login_name, channel_id, mode):
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

		User = await self.SERVER.GETRequest(
			url='https://api.twitch.tv/helix/users',
			params={'login': login_name},
			headers = {
				'Authorization': await self.SERVER.getToken(),
				'Client-Id': self.SERVER.CLIENTID
			}
		)
		try:
			UserID = User['data'][0]['id']
		except:
			raise commands.UserInputError("Twitch-Topic not found")

		if mode=="subscribe":
			self.cursor.execute(f'INSERT INTO twitch_feeds VALUES ({guild.id},{channel.id},{UserID},0)')

			Embed = discord.Embed(description=f"**Subscription successfully for [{login_name}](https://twitch.tv/{login_name}) in <#{channel.id}>**")

			self.cursor.execute(f'SELECT _topic_id FROM twitch_topics WHERE _topic_id={UserID}')
			if not self.cursor.fetchall():
				Response = await self.SERVER.HookStream(login_name, 'subscribe')
				if not Response:
					self.cursor.execute(f'INSERT INTO twitch_topics VALUES ({UserID}, "{s(login_name)}")')
					self.TwitchFeeds.append(login_name)
					self.conn.commit()
					return (None, Embed)
				else:
					self.conn.commit()
					return (Response, None)
			
			self.conn.commit()
			return (None, Embed)

		elif mode=="unsubscribe":
			self.cursor.execute(f'DELETE FROM twitch_feeds WHERE _guild_id={guild.id} AND _channel_id={channel.id} AND _topic_id={UserID}')

			Embed = discord.Embed(description=f"**Successfully unsubscribed for [{login_name}](https://twitch.tv/{login_name}) in <#{channel.id}>**")

			# if no feeds for topic left, delete Topic as well and unsubscribe:
			self.cursor.execute(f'SELECT * FROM twitch_feeds WHERE _topic_id={UserID}')
			if not self.cursor.fetchall():
				Response = await self.SERVER.HookStream(login_name, 'unsubscribe')
				if not Response:
					self.cursor.execute(f'DELETE FROM twitch_topics WHERE _topic_id={UserID}')
					self.TwitchFeeds.remove(login_name)
					try:
						self.cursor.execute(f"DROP TABLE twitch_{UserID}")
					except:
						None
					self.conn.commit()
					return (None, Embed)
				else:
					self.conn.commit()
					return (Response, None)

			self.conn.commit()
			return (None, Embed)

	@commands.command(name='twitch_sub', help=f'creates Twitch-Topic subscription (leave Channel empty if calling from same channel), \
		usage: {STDPREFIX}twitch_sub login_name login_name Channel[optional]')
	@commands.has_guild_permissions(administrator=True)
	async def twitch_sub(self, ctx, login_name : str, Channel = None):
		content, embed = await self.subscription(ctx.guild, ctx.channel, login_name, Channel, "subscribe")
		await ctx.send(content=content, embed=embed)

	@commands.command(name='twitch_unsub', help=f'unsub from existing Twitch-Topic (leave Channel empty if calling from same channel), \
		usage: {STDPREFIX}twitch_unsub login_name Channel[optional]')
	@commands.has_guild_permissions(administrator=True)
	async def twitch_unsub(self, ctx, login_name : str, Channel = None):
		content, embed = await self.subscription(ctx.guild, ctx.channel, login_name, Channel, "unsubscribe")
		await ctx.send(content=content, embed=embed)

	@commands.command(name='twitch_show', help=f'shows active twitch_feeds for this Channel')
	@commands.has_guild_permissions(administrator=True)
	async def twitch_show(self, ctx):
		self.cursor.execute(f'SELECT _channel_id, _topic_id FROM twitch_feeds WHERE _guild_id={ctx.guild.id}')
		Feeds = self.cursor.fetchall()
		Embed = discord.Embed(title="Twitch Feeds")
		for feed in Feeds:
			Channel = discord.utils.get(ctx.guild.channels, id=feed[0])
			self.cursor.execute(f'SELECT _login FROM twitch_topics WHERE _topic_id={feed[1]}')
			Name = self.cursor.fetchone()[0]
			Embed.add_field(name=f'<#{Channel.name}>', value=f"[{Name}](https://twitch.tv/{Name})")
		await ctx.send(embed=Embed)

	@commands.command(name='show_subs', hidden=True)
	@commands.is_owner()
	async def show_subs(self, ctx):
		headers={
				'Authorization': await self.SERVER.getToken(),
				'Client-Id': self.SERVER.CLIENTID
			}
		Subs = await self.SERVER.GETRequest(
			url="https://api.twitch.tv/helix/webhooks/subscriptions",
			params=None,
			headers=headers
		)
		
		Embed = discord.Embed(title=f"{Subs['total']} active Twitch subscriptions found")
		user_list = []
		sub_infos = []
		
		for sub in Subs['data']:
			user_list.append( ['id', str(int(sub['topic'].replace("https://api.twitch.tv/helix/streams?user_id=", "")))] )
		
		Users = await self.SERVER.GETRequest(
			url="https://api.twitch.tv/helix/users",
			params=user_list,
			headers=headers
		)

		for i, user in enumerate(Users['data']):
			data = Subs['data'][i]
			Embed.add_field(name=f'{user["login"]}', value=f'callback: {data["callback"]}\nexpires_at: {data["expires_at"]}')

		await ctx.send(embed=Embed)

	async def twitchOffMessage(self, topic, NOW):
		Server = self.SERVER
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
		self.cursor.execute(f"SELECT * FROM twitch_{topic}")
		Times = self.cursor.fetchall()
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

	async def twitchOnMessage(self, topic, NOW, footer, Data):
		Server = self.SERVER
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

	def data_handler(self, query):
		_NOW = datetime.now()
		timezone = pytz.timezone("Europe/Berlin")
		NOW = timezone.localize(_NOW)
		print(f"Request at {NOW}:\n{query}\n")

		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		
		Data = query['data']
		UserID = int(query['topic'])

		# Creates Table for Topic if not exists and updates stream change for later usage
		self.cursor.execute(f"CREATE TABLE IF NOT EXISTS twitch_{UserID} (_timestamp TEXT, _game TEXT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;")

		# 'twitch_feeds (_guild_id BIGINT, _channel_id BIGINT, _topic_id BIGINT, _message_id BIGINT)')
		self.cursor.execute(f"SELECT * FROM twitch_feeds WHERE _topic_id={UserID}")
		Feeds = self.cursor.fetchall()
		
		# type(Data) = array and right now only a Stream Topic,
		# if Change in Future necessary, scan over request.path and change callback properly,
		# or make a different handler for every callback
		if Data:
			data = Data[0]
			self.cursor.execute(f"INSERT INTO twitch_{UserID} VALUES ('{NOW.strftime('%a %b %d %X %z %Y')}','{s(data['game_name'])}')")
			# data has content, upgrade existing message (if message_id is not 0), or create message (and update message_id):
			for feed in Feeds:
				guild = discord.utils.get(self.bot.guilds, id=int(feed[0]))
				channel = discord.utils.get(guild.channels, id=int(feed[1]))
				if feed[3]:
					message = asyncio.run_coroutine_threadsafe(channel.fetch_message(int(feed[3])), self.botloop)
					message = message.result()
					embed = loop.run_until_complete(self.twitchOnMessage(topic=UserID, NOW=NOW, footer="Streaming", Data=data))
					asyncio.run_coroutine_threadsafe(message.edit(content=f"**{data['user_login']}** is now online!\nhttps://twitch.tv/{data['user_login']}", embed=embed), self.botloop)
				else:
					embed = loop.run_until_complete(self.twitchOnMessage(topic=UserID, NOW=NOW, footer="Started streaming", Data=data))
					message = asyncio.run_coroutine_threadsafe(channel.send(content=f"**{data['user_login']}** is now online!\nhttps://twitch.tv/{data['user_login']}", embed=embed), self.botloop)
					message = message.result()
					self.cursor.execute(f"UPDATE twitch_feeds SET _message_id={message.id} WHERE _topic_id={UserID} AND _channel_id={channel.id}")	
		else:
			self.cursor.execute(f"INSERT INTO twitch_{UserID} VALUES ('{NOW.strftime('%a %b %d %X %z %Y')}','')")
			OffMessage, UserName = loop.run_until_complete(self.twitchOffMessage(topic=UserID, NOW=NOW))
			# data is empty, upgrade message to offline_message and set message_id to 0
			for feed in Feeds:
				guild = discord.utils.get(self.bot.guilds, id=int(feed[0]))
				channel = discord.utils.get(guild.channels, id=int(feed[1]))
				message = asyncio.run_coroutine_threadsafe(channel.fetch_message(int(feed[3])), self.botloop)
				message = message.result()
				asyncio.run_coroutine_threadsafe(message.edit(content=f"**{UserName}** was online" ,embed=OffMessage), self.botloop)
				# clean Database
				self.cursor.execute(f"UPDATE twitch_feeds SET _message_id=0 WHERE _topic_id={UserID} AND _channel_id={channel.id}")
			# delete topic database:
			self.cursor.execute(f"DROP TABLE twitch_{UserID}")
		
		self.conn.commit()