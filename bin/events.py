import discord
import asyncio
from discord.ext import commands
import mysql.connector
import numpy as np
from bin.importantFunctions import s, STDPREFIX

class events(commands.Cog):

	def __init__(self, bot, prefix, mysql_connector, botloop, func_member_join):
		global STDPREFIX
		STDPREFIX = prefix
		self.bot = bot
		self.conn = mysql_connector
		self.cursor = self.conn.cursor(buffered=True)
		self.botloop = botloop
		self.func_member_join = func_member_join

	# @commands.Cog.listener()
	# async def on_command_error(self, ctx, error):
	# 	try:
	# 		self.cursor.execute(f"SELECT _prefix FROM guilds WHERE _id={ctx.guild.id}")
	# 		prefix = self.cursor.fetchone()[0]
	# 		await ctx.send(str(error) + f". Try {prefix}help bzw. {prefix}help command for more infos.")
	# 	except:
	# 		prefix = STDPREFIX
	# 		await ctx.send(str(error) + f". Try {prefix}help bzw. {prefix}help command for more infos.")


	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		# add guild to DB:
		t = (guild.id, guild.name, STDPREFIX, 0, False, )
		self.cursor.execute(f'INSERT INTO guilds VALUES ({t[0]},"{s(t[1])}","{s(t[2])}",{t[3]},{t[4]});')

		# add all members of guild to DB:
		for member in guild.members:
			await self.func_member_join(member)
		self.conn.commit()


	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		# delete guild:
		self.cursor.execute(f'DELETE FROM guilds WHERE _id={guild.id}')
		# delete members on guild:
		self.cursor.execute(f'DELETE FROM members WHERE _guild={guild.id}')
		self.conn.commit()


	@commands.Cog.listener()
	async def on_guild_update(self, before, after):
		self.cursor.execute(f'UPDATE guilds SET _name="{s(after.name)}" WHERE _id={after.id}')
		self.conn.commit()


	@commands.Cog.listener()
	async def on_member_remove(self, member):
		if member.bot:
			return

		guild = member.guild
		# Delete members entry
		self.cursor.execute(f'DELETE FROM members WHERE _id={member.id} AND _guild={guild.id}')
		self.conn.commit()


	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		if before.bot or after.bot:
			return

		guild = after.guild
		# update member:
		t = (after.nick, after.name)
		self.cursor.execute(f'UPDATE members SET _nick="{s(t[0])}", _name="{s(t[1])}" WHERE _id={after.id} AND _guild={guild.id}')
		self.conn.commit()


