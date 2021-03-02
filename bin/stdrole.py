import discord
import os
import asyncio
from discord.ext import commands
from threading import Thread
import mysql.connector
from bin.importantFunctions import send_private, CustomError, STDPREFIX, s


class stdrole(commands.Cog):

	def __init__(self, bot, prefix, mysql_connector, botloop, PATH, REGISTER_EMOJI_ACCEPT, REGISTER_EMOJI_DENY):
		global STDPREFIX
		STDPREFIX = prefix
		self.bot = bot
		self.conn = mysql_connector
		self.cursor = self.conn.cursor(buffered=True)
		self.botloop = botloop
		self.PATH = PATH
		self.REGISTER_EMOJI_ACCEPT = REGISTER_EMOJI_ACCEPT
		self.REGISTER_EMOJI_DENY = REGISTER_EMOJI_DENY


	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		# delete stdrole_message if exists:
		try: os.remove(self.PATH + f"/stdrole_messages/{guild.id}.txt")
		except: None


	@commands.Cog.listener()
	async def on_member_join(self, member):
		if member.bot:
			return

		# set registration status
		guild = member.guild
		self.cursor.execute(f"SELECT _stdrole FROM guilds WHERE _id={guild.id}")
		stdrole = self.cursor.fetchone()[0]
		if len(member.roles) == 1 and stdrole:
			regist = 2
		else:
			regist = 1

		# DB-registration
		t = (member.id, member.name, member.nick, guild.id, regist, )
		self.cursor.execute(f'INSERT INTO members VALUES ({t[0]},"{s(t[1])}","{s(t[2])}",{t[3]},{t[4]})')

		# send Registration-Message
		if regist >= 2 and stdrole:
			with open(file=self.PATH + f"/stdrole_messages/{guild.id}.txt", mode="r", encoding="utf8") as r:
				message = r.read()
			Message = await send_private(member, message)
			# (_message_id BIGINT, _guild_id BIGINT, _jump_url TEXT, _user_id BIGINT)
			self.cursor.execute(f'INSERT INTO sr_messages VALUES ({Message.id},{guild.id},"0",{member.id})')
			await Message.add_reaction(self.REGISTER_EMOJI_ACCEPT)
			await Message.add_reaction(self.REGISTER_EMOJI_DENY)
		self.conn.commit()

	
	@commands.Cog.listener()
	async def on_member_remove(self, member):
		if member.bot:
			return
		guild = member.guild
		# Delete selfrole created for this Member within stdrole (selfrole ticket for stdrole)
		self.cursor.execute(f'DELETE FROM sr_messages WHERE _user_id={member.id} AND _guild_id={guild.id} AND _jump_url="0"')
		self.conn.commit()


	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		if before.bot or after.bot:
			return
		guild = after.guild

		# autodeletion of stdrole:
		if len(after.roles) > 1:
			self.cursor.execute(f"SELECT _stdrole FROM guilds WHERE _id={guild.id}")
			Guest = discord.utils.get(after.roles, id=self.cursor.fetchone()[0])

			if Guest:
				self.cursor.execute(f'SELECT _regist FROM members WHERE _id={after.id} AND _guild={guild.id}')
				regist = self.cursor.fetchone()[0]
				self.cursor.execute(f'SELECT _autodelete FROM guilds WHERE _id={guild.id}')
				autodelete = self.cursor.fetchone()[0]
				# if registered (because member has more than one Role):
				if regist >> 0 & 0x01 and len(after.roles) > 2 and autodelete:
					await after.remove_roles(Guest)
				elif regist >> 1 & 0x01:
					regist |= 0x01  # 3 is possible

				self.cursor.execute(f'UPDATE members SET _regist={regist} WHERE _id={after.id} AND _guild={guild.id}')
		self.conn.commit()


	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if payload.user_id == self.bot.user.id:
			return

		# stdrole:
		if not payload.guild_id:
			self.cursor.execute(f'SELECT _guild_id FROM sr_messages WHERE _jump_url="0" AND _user_id={payload.user_id} AND _message_id={payload.message_id}')
			guild_id = self.cursor.fetchone()
			if guild_id:

				self.cursor.execute(f'SELECT _stdrole FROM guilds WHERE _id={guild_id[0]}')
				stdrole = self.cursor.fetchone()[0]
				if stdrole:

					guild = discord.utils.get(self.bot.guilds, id=guild_id[0])
					member = discord.utils.get(guild.members, id=payload.user_id)
					# channel = discord.utils.get(bot.private_channels, id=payload.channel_id)
					channel = await member.create_dm()
					message = await channel.fetch_message(payload.message_id)
					if payload.emoji.name == self.REGISTER_EMOJI_ACCEPT:
						try:
							role = discord.utils.get(guild.roles, id=stdrole)
							await member.add_roles(role)
							self.cursor.execute(f'UPDATE members SET _regist=1 WHERE _id={payload.user_id} AND _guild={guild.id}')
							self.cursor.execute(f'DELETE FROM sr_messages WHERE _user_id={payload.user_id} AND _guild_id={guild.id} AND _jump_url="0"')
							await send_private(member, embed=discord.Embed(description=f"Welcome at the {guild.name} Discord!"))
							await message.delete()
						except:
							raise commands.UserInputError(f"Registration failed, please contact an admin or the developer (Whitekeks#3762)")
					elif payload.emoji.name == self.REGISTER_EMOJI_DENY:
						self.cursor.execute(f'DELETE FROM members WHERE _id={member.id} AND _guild={guild.id}')
						await send_private(member, embed=discord.Embed(description="Conditions must be accepted!"))
						await message.delete()
						await member.kick()
					self.conn.commit()

	
	@commands.command(name='stdrole', help=f'toggles autoregistration usage: {STDPREFIX}stdrole role(name or id) Message(as String, ID(same Channel) or txt-File-Attachement)')
	@commands.has_guild_permissions(administrator=True)
	async def stdrole(self, ctx, role_id, message_id=None):
		try:
			role = discord.utils.get(ctx.guild.roles, id=int(role_id))
		except:
			try:
				role = discord.utils.get(ctx.guild.roles, id=int(role_id[3:len(role_id)-1])) #Bsp.: <@&775092589447741540>
			except:
				role = discord.utils.get(ctx.guild.roles, name=role_id)
		if not role: raise commands.UserInputError("Role not found")

		if not message_id:
			try:
				message = await ctx.message.attachments[0].read()
				message = message.decode("utf-8")
			except:
				raise commands.UserInputError("No right attachement found")
		elif message_id:
			try:
				message = await ctx.channel.fetch_message(int(message_id[int(len(message_id)-18):]))
				if not message:
					raise CustomError()
				message = message.content
			except CustomError:
				raise commands.UserInputError("Could not find Message, make sure the Command is in the same Channel as the Message")
			except:
				message = message_id

		self.cursor.execute(f'UPDATE guilds SET _stdrole = {role.id} WHERE _id = {ctx.guild.id}')
		self.conn.commit()
		with open(file=self.PATH + f"/stdrole_messages/{ctx.guild.id}.txt", mode="w", encoding="utf8") as w:
			w.write(message)
		await ctx.send(embed=discord.Embed(description="standart-role set"))


	@commands.command(name='stdrole_delete', help=f'turns off autoregistration and autodelete')
	@commands.has_guild_permissions(administrator=True)
	async def stdrole_delete(self, ctx):
		guild = ctx.guild
		self.cursor.execute(f'UPDATE guilds SET _stdrole = 0, _autodelete = {False} WHERE _id = {guild.id}')
		self.conn.commit()
		try: os.remove(self.PATH + f"/stdrole_messages/{guild.id}.txt")
		except: commands.UserInputError("No stdrole was set!")
		await ctx.send(embed=discord.Embed(description="autoregistration and autodelete successfully turned off"))


	@commands.command(name='autodelete', help=f'toggles autodelete for stdrole if User has another Role, default = False, usage: {STDPREFIX}autodelete True/False')
	@commands.has_guild_permissions(administrator=True)
	async def autodelete(self, ctx, con: bool):
		self.cursor.execute(f'UPDATE guilds SET _autodelete = {con} WHERE _id = {ctx.guild.id}')
		self.conn.commit()
		await ctx.send(embed=discord.Embed(description=f"autodelete set to {con}"))


	@commands.command(name='stdrole_show', help='shows stdrole and welcome-message')
	@commands.has_guild_permissions(administrator=True)
	async def stdrole_show(self, ctx):
		self.cursor.execute(f'SELECT _stdrole FROM guilds WHERE _id = {ctx.guild.id}')
		stdrole = self.cursor.fetchone()[0]
		role = discord.utils.get(ctx.guild.roles, id=stdrole)
		with open(file=self.PATH + f"/stdrole_messages/{ctx.guild.id}.txt", mode="r", encoding="utf8") as r:
			message = r.read()
		await ctx.send(f"**Role:** {role.name}\n\n**Message:**\n{message}")
