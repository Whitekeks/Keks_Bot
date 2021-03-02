import discord
import asyncio
from discord.ext import commands
import mysql.connector
from bin.importantFunctions import s, CustomError, STDPREFIX


class selfrole(commands.Cog):

	def __init__(self, bot, prefix, mysql_connector, botloop):
		global STDPREFIX
		STDPREFIX = prefix
		self.bot = bot
		self.conn = mysql_connector
		self.cursor = self.conn.cursor(buffered=True)
		self.botloop = botloop


	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		# delete sr_messages and bonds:
		self.cursor.execute(f'DELETE FROM sr_messages WHERE _guild_id={guild.id}')
		self.cursor.execute(f'DELETE FROM bonds WHERE _guild_id={guild.id}')
		self.conn.commit()


	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel):
		# delete srmassages:
		self.cursor.execute(f'DELETE FROM sr_messages WHERE _message_id={channel.id} AND _guild_id={guild.id}')
		self.conn.commit()


	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if payload.user_id == self.bot.user.id:
			return

		if payload.guild_id:
			# check if message id is in sr_messages:
			self.cursor.execute(f'SELECT _message_id FROM sr_messages WHERE _guild_id = {payload.guild_id} AND _message_id = {payload.message_id}')
			if self.cursor.fetchone():
				guild = discord.utils.get(self.bot.guilds, id=payload.guild_id)
				member = discord.utils.get(guild.members, id=payload.user_id)
				self.cursor.execute(f'SELECT _role_id, _emoji FROM bonds WHERE _guild_id={payload.guild_id}')
				for role_id in self.cursor.fetchall():
					if role_id[1] == payload.emoji.name:
						role = discord.utils.get(guild.roles, id=role_id[0])
						await member.add_roles(role)

	
	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		if not payload.guild_id or payload.user_id == self.bot.user.id:
			return

		# check if message id is in sr_messages:
		self.cursor.execute(f'SELECT _message_id FROM sr_messages WHERE _guild_id = {payload.guild_id} AND _message_id = {payload.message_id}')
		if self.cursor.fetchone():
			guild = discord.utils.get(self.bot.guilds, id=payload.guild_id)
			member = discord.utils.get(guild.members, id=payload.user_id)
			self.cursor.execute(f'SELECT _role_id, _emoji FROM bonds WHERE _guild_id = {payload.guild_id}')
			for role_id in self.cursor.fetchall():
				if role_id[1] == payload.emoji.name:
					role = discord.utils.get(guild.roles, id=role_id[0])
					await member.remove_roles(role)

	
	@commands.Cog.listener()
	async def on_raw_message_delete(self, payload):
		if not payload.guild_id:
			return
		
		self.cursor.execute(f'DELETE FROM sr_messages WHERE _message_id = {payload.message_id} AND _guild_id = {payload.guild_id}')
		self.conn.commit()


	@commands.command(name='sr_bond', help=f'binds emoji to role, usage: {STDPREFIX}sr_bond role(name or id) emoji')
	@commands.has_guild_permissions(administrator=True)
	async def sr_bond(self, ctx, role_id, emoji):
		guild = ctx.guild

		try:
			role = discord.utils.get(ctx.guild.roles, id=int(role_id))
		except:
			try:
				role = discord.utils.get(ctx.guild.roles, id=int(role_id[3:len(role_id)-1])) #Bsp.: <@&775092589447741540>
			except:
				role = discord.utils.get(ctx.guild.roles, name=role_id)
		if not role: raise commands.UserInputError("Role not found")

		self.cursor.execute(f'DELETE FROM bonds WHERE _role_id = {role.id} AND _emoji = "{emoji}" AND _guild_id = {guild.id}')
		self.cursor.execute(f'INSERT INTO bonds VALUES ({role.id}, "{emoji}", {guild.id})')
		self.conn.commit()
		await ctx.send(embed=discord.Embed(description=f"bond {role.name} -> {emoji} successfully created"))


	@commands.command(name='sr_bond_delete', help=f'deletes bond of emoji to role, usage: {STDPREFIX}sr_bond_delete role(name or id) emoji')
	@commands.has_guild_permissions(administrator=True)
	async def sr_bond_delete(self, ctx, role_id, emoji):
		guild = ctx.guild

		try:
			role = discord.utils.get(ctx.guild.roles, id=int(role_id))
		except:
			try:
				role = discord.utils.get(ctx.guild.roles, id=int(role_id[3:len(role_id)-1])) #Bsp.: <@&775092589447741540>
			except:
				role = discord.utils.get(ctx.guild.roles, name=role_id)
		if not role: raise commands.UserInputError("Role not found")

		self.cursor.execute(f'DELETE FROM bonds WHERE _role_id = {role.id} AND _emoji = "{emoji}" AND _guild_id = {guild.id}')
		self.conn.commit()
		await ctx.send(embed=discord.Embed(description=f"bond {role.name} -> {emoji} successfully deleted"))


	@commands.command(name='sr_bond_show', help=f'shows bonds of emojis to roles')
	@commands.has_guild_permissions(administrator=True)
	async def sr_bond_show(self, ctx):
		# check if role in bond still exists:
		self.cursor.execute(f'SELECT _role_id FROM bonds WHERE _guild_id = {ctx.guild.id}')
		for role in self.cursor.fetchall():
			if not ctx.guild.get_role(role[0]):
				self.cursor.execute(f'DELETE FROM bonds WHERE _role_id = {role[0]}')
				break
		self.conn.commit()
		Embed = discord.Embed(title="Active Bonds:\n\n")
		self.cursor.execute(f'SELECT _role_id, _emoji FROM bonds WHERE _guild_id = {ctx.guild.id}')
		for i, bond in enumerate(self.cursor.fetchall()):
			rolename = discord.utils.get(ctx.guild.roles, id=bond[0]).name
			Embed.add_field(name=f'Bond {i}:', value=f"{i}: {rolename} -> {bond[1]}")
		await ctx.send(embed=Embed)


	@commands.command(name='sr_message', help=f'creates message for self-role or binds existing message, usage: {STDPREFIX}sr_message Message(as String or ID(same Channel)) emojis(*args, ...)')
	@commands.has_guild_permissions(administrator=True)
	async def sr_message(self, ctx, message_id=None, *args):
		try:
			message = await ctx.channel.fetch_message(int(message_id[int(len(message_id)-18):]))
			if not message:
				raise CustomError()
		except CustomError:
			raise commands.UserInputError("Could not find Message, make sure the Command is in the same Channel as the Message")
		except:
			message = await ctx.send(embed=discord.Embed(description=message_id))
		
		# test if Message allready exists in Database (then this is a update):
		self.cursor.execute(f'SELECT * FROM sr_messages WHERE _message_id={message.id} AND _guild_id={ctx.guild.id} AND _jump_url="{message.jump_url}" AND _user_id={message.author.id}')
		if not self.cursor.fetchone():
			self.cursor.execute(f'INSERT INTO sr_messages VALUES ({message.id}, {ctx.guild.id}, "{message.jump_url}", {message.author.id})')
		self.conn.commit()
		
		for emoji in args:
			try:
				await message.add_reaction(emoji)
			except:
				None


	@commands.command(name='sr_message_show', help=f'shows created messages for self-role')
	@commands.has_guild_permissions(administrator=True)
	async def sr_message_show(self, ctx):
		Embed = discord.Embed(title="Active Self-Role Messages:")
		self.cursor.execute(f'SELECT _jump_url, _user_id FROM sr_messages WHERE _guild_id = {ctx.guild.id}')
		for i, msg in enumerate(self.cursor.fetchall()):
			user = discord.utils.get(ctx.guild.members, id=msg[1])
			Embed.add_field(name=f"Message {i}", value=f"Message [here]({msg[0]})\n created by <@{user.id}>")
		await ctx.send(embed=Embed)