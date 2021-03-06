import discord
import asyncio
import aiohttp
from discord.ext import commands
import mysql.connector
import numpy as np
from bin.importantFunctions import s, STDPREFIX


class Commands(commands.Cog):

	def __init__(self, bot, prefix, mysql_connector, botloop):
		global STDPREFIX
		STDPREFIX = prefix
		self.bot = bot
		self.conn = mysql_connector
		self.cursor = self.conn.cursor(buffered=True)
		self.botloop = botloop

	
	@commands.command(name='set_prefix', help=f'choose a new prefix for this Server (Private allways "{STDPREFIX}")')
	@commands.has_guild_permissions(administrator=True)
	async def set_prefix(self, ctx, prefix: str):
		guild = ctx.guild
		t = (s(prefix), )
		if t[0] and t[0] != "":
			self.cursor.execute(f'UPDATE guilds SET _prefix="{s(t[0])}" WHERE _id={guild.id}')
			self.conn.commit()
			await ctx.send(embed=discord.Embed(description=f'New Prefix set: "{s(t[0])}"'))
		else:
			raise commands.UserInputError("Prefix not allowed!")


	@commands.command(name='bip', help='bop')
	async def bip(self, ctx):
		await ctx.send('bop')


	@commands.command(name='dice', help=f'just a variable dice, usage {STDPREFIX}dice sites(=6)')
	async def roll_dice(self, ctx, sites=6):
		if sites==0:
			Random = 0
		elif sites<0:
			Random = -np.random.randint(1, -sites+1)
		else:
			Random = np.random.randint(1, sites+1)
		await ctx.send(embed=discord.Embed(description=f"**D{sites}:**\n\n {Random}"))


	@commands.command(name='rand', help=f'get a random number between start and stop')
	async def rand(self, ctx, start, stop, Type="int"):
		Random = (float(stop)-float(start))*np.random.random()+float(start)
		if Type==int or Type=="int":
			Random = int(np.round(Random))
		elif Type==float or Type=="float":
			None
		else:
			raise commands.UserInputError("Type not Supported, only int or float")
		await ctx.send(embed=discord.Embed(description=f"**Random between {start} and {stop} as {Type}:**\n\n {Random}"))


	@commands.command(name='avatar', help='get avatar_url of member as format ‘webp’, ‘jpeg’, ‘jpg’, ‘png’ or ‘gif’ (default is ‘webp’)')
	async def avatar(self, ctx, Member, Format="webp"):
		try:
			MEMBER = discord.utils.get(ctx.guild.members, id=int(Member[3:len(Member)-1]))
		except:
			MEMBER = discord.utils.get(ctx.guild.members, name=str(Member))
		await ctx.send(str(MEMBER.avatar_url_as(format=Format)))
		

	@commands.command(name='rand_user', help='get random User on Server')
	async def raffle(self, ctx):
		guild = ctx.guild
		rand_user = np.random.choice(guild.members)
		while rand_user.bot:
			rand_user = np.random.choice(guild.members)
		await ctx.send(embed=discord.Embed(description=f"<@{rand_user.id}>"))


	@commands.command(name='random_comic', help='get a random Comic!')
	async def random_comic(self, ctx):
		url = "https://c.xkcd.com/random/comic/"
		async with aiohttp.ClientSession() as session:
			async with session.get(url=url) as resp:
				html = await resp.text()

		string = "Image URL (for hotlinking/embedding):"
		erg = html.find(string)
		html = html[erg + len(string) + 1:]
		html = html.split("\n")
		await ctx.send(content=f"A random Comic from xkcd:\n{html[0]}")
