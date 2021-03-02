import twitter
import pytz
import discord
import time
import asyncio
import mysql.connector
from threading import Thread
from datetime import datetime
from discord.ext import commands
from bin.importantFunctions import s, sleep, STDPREFIX


class checkTwitter:

	def __init__(self, **kwargs):
		
		self.bot = kwargs['bot']
		self.CREATION_TIME = kwargs['CREATION_TIME']
		self.usertag = kwargs['usertag']
		self.feed_id = kwargs['feed_id']
		self.guild_id = kwargs['guild_id']
		self.channel_id = kwargs['channel_id']
		self.conn = kwargs['mysql_connector']
		# self.cursor = self.conn.cursor(buffered=True)
		self.twitter_api = kwargs['twitter_api']
		self.botloop = kwargs['botloop']

		self.CREATION_TIME = datetime.strptime(self.CREATION_TIME, '%a %b %d %X %z %Y')
		self.Stop = False
		self.Thread = Thread(target=self.checkTwitter)
		self.table = f'twitter_{self.feed_id}'

	def checkTwitter(self):
		# need a standalone Connection because auf heavy duty
		Tconn = mysql.connector.connect(
			host=self.conn._host,
			user=self.conn._user,
			password=self.conn._password,
			database=self.conn._database
		)
		c = Tconn.cursor(buffered=True)

		while not self.Stop:
			statuses = self.twitter_api.GetUserTimeline(screen_name=self.usertag, count=100)
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
					guild = discord.utils.get(self.bot.guilds, id=self.guild_id)
					channel = discord.utils.get(guild.channels, id=self.channel_id)
					if i[2]:
						url = f'{self.usertag} hat auf Twitter folgendes Retweetet:\n{url}'
					asyncio.run_coroutine_threadsafe(channel.send(url), self.botloop)
					c.execute(f'UPDATE {self.table} SET _send=1 WHERE _id={i[0]}')

				Tconn.commit()

			sleep(30, not self.Stop)
		Tconn.close()

	def start(self):
		self.Thread.start()

	def stop(self):
		self.Stop = True
		self.Thread.join()


class Twitter(commands.Cog):

	def __init__(self, bot, prefix, mysql_connector, botloop, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET):
		global STDPREFIX
		STDPREFIX = prefix
		self.bot = bot
		self.conn = mysql_connector
		self.cursor = self.conn.cursor(buffered=True)
		self.botloop = botloop
		self.twitter_api = twitter.Api(
			consumer_key=CONSUMER_KEY,
			consumer_secret=CONSUMER_SECRET,
			access_token_key=ACCESS_TOKEN_KEY,
			access_token_secret=ACCESS_TOKEN_SECRET
		)

		self.cursor.execute('SELECT * FROM twitter')
		Feeds = self.cursor.fetchall()
		THREADS = []
		for feed in Feeds:
			THREADS.append((
				checkTwitter(
					bot=self.bot,
					usertag=feed[0], 
					channel_id=feed[1], 
					CREATION_TIME=feed[2], 
					guild_id=feed[3], 
					feed_id=feed[4], 
					mysql_connector=self.conn, 
					twitter_api=self.twitter_api, 
					botloop=self.botloop), 
				feed[4]
			))
		self.THREADS = THREADS
		print("twitter set")

	def start(self):
		for thread in self.THREADS:
			thread[0].start()
		print("Twitter-Threads have started")

	def stop(self):
		for thread in self.THREADS:
			thread[0].stop()
		print("All Twitter Feeds stopped")

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		# delete twitter feeds and tables:
		self.cursor.execute(f'SELECT * FROM twitter WHERE _guild_id={guild.id};')
		Feeds = self.cursor.fetchall()
		for feed in Feeds:
			for i, thread in enumerate(self.THREADS):
				if thread[1] == feed[4]:
					thread[0].stop()
					del self.THREADS[i]
					break

			self.cursor.execute(f'DELETE FROM twitter WHERE _feed_id={feed[4]};')
			self.cursor.execute(f'DROP TABLE twitter_{feed[4]};')
		self.conn.commit()

	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel):
		# delete twitter feeds and tables:
		self.cursor.execute(f'SELECT * FROM twitter WHERE _channel_id={channel.id} AND _guild_id={channel.guild.id};')
		Feeds = self.cursor.fetchall()
		for feed in Feeds:
			for i, thread in enumerate(self.THREADS):
				if thread[1] == feed[4]:
					thread[0].stop()
					del self.THREADS[i]
					break

			self.cursor.execute(f'DELETE FROM twitter WHERE _feed_id={feed[4]};')
			self.cursor.execute(f'DROP TABLE twitter_{feed[4]};')
		self.conn.commit()
	
	@commands.command(name='twitter_set', help=f'set channel for twitter_news twitter_tag without "@" usage: {STDPREFIX}twitter_set twitter_tag(without "@") channel')
	@commands.has_guild_permissions(administrator=True)
	async def twitter_set(self, ctx, twitter_tag: str, channel: str):
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

		self.cursor.execute(f'SELECT * FROM twitter WHERE _channel_id={channel_id} AND _usertag="{usertag}" AND _guild_id={guild_id}')
		if self.cursor.fetchall():
			raise commands.UserInputError("Twitter-Feed allready set")

		now = datetime.now()
		timezone = pytz.timezone("Europe/Berlin")
		now = timezone.localize(now)
		creation_time = now.strftime('%a %b %d %X %z %Y')

		feed_id = 0
		self.cursor.execute('SELECT _feed_id FROM twitter ORDER BY _feed_id')
		for i, j in enumerate(self.cursor.fetchall()):
			if i != j[0]:
				feed_id = i
				break
			else:
				feed_id = i+1

		self.cursor.execute(f'INSERT INTO twitter VALUES ("{usertag}", {channel_id}, "{creation_time}", {guild_id}, {feed_id})')
		self.cursor.execute(f'CREATE TABLE IF NOT EXISTS twitter_{feed_id} (_rank BIGINT, _id BIGINT, _created_at TEXT, _send BOOL, _retweet BOOL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci')
		self.conn.commit()

		self.THREADS.append((
			checkTwitter(
				bot=self.bot,
				usertag=usertag, 
				channel_id=channel_id, 
				CREATION_TIME=creation_time, 
				guild_id=guild_id, 
				feed_id=feed_id,
				mysql_connector=self.conn, 
				twitter_api=self.twitter_api, 
				botloop=self.botloop), 
			feed_id
		))
		self.THREADS[len(self.THREADS)-1][0].start()

		await Channel.send(embed=discord.Embed(description=f"Twitter-Feed for {usertag} successfully set in #{Channel.name}"))


	@commands.command(name='twitter_delete', help=f'deletes news-feed, usage: {STDPREFIX}twitter_delete twitter_tag(without "@") channel')
	@commands.has_guild_permissions(administrator=True)
	async def twitter_delete(self, ctx, twitter_tag: str, channel: str):
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

		self.cursor.execute(f'SELECT * FROM twitter WHERE _channel_id={channel_id} AND _usertag="{usertag}" AND _guild_id={guild_id}')
		Feed = self.cursor.fetchall()
		if not Feed:
			raise commands.UserInputError("News-Feed does not exist")
		
		message = ctx.send(embed=discord.Embed(description=f"Deleting Twitter-Feed for {usertag} in #{Channel.name}, this may take some time..."))

		feed = Feed[0]
		for i, thread in enumerate(self.THREADS):
			if thread[1] == feed[4]:
				thread[0].stop()
				del self.THREADS[i]
				break

		self.cursor.execute(f'DELETE FROM twitter WHERE _feed_id={feed[4]}')
		self.cursor.execute(f'DROP TABLE twitter_{feed[4]}')
		self.conn.commit()
		await message.edit(embed=discord.Embed(description=f"Twitter-Feed for {usertag} in #{Channel.name} successfully deleted"))


	@commands.command(name='twitter_show', help='shows active twitter-feeds')
	@commands.has_guild_permissions(administrator=True)
	async def twitter_show(self, ctx):
		self.cursor.execute(f'SELECT _usertag, _channel_id, _creation_time FROM twitter WHERE _guild_id={ctx.guild.id};')
		Feeds = self.cursor.fetchall()
		if Feeds:
			Embed = discord.Embed(title="Twitter Feeds")
			for i, feed in enumerate(Feeds):
				channel = discord.utils.get(ctx.guild.channels, id=feed[1])
				Embed.add_field(name=f'#{channel.name}', value=f"Usertag: {feed[0]}\n Channel: {channel.name}\n Created at: {feed[2]}")
		else:
			Embed = discord.Embed(description="No Feeds found")
		await ctx.send(embed=Embed)