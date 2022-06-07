from discord.ext import tasks, commands
import discord
import sys
sys.path.append('..')
from extras.text_zone import all_id as id_0
import extras.IDS as ID
from zoneinfo import ZoneInfo
import datetime as dt

cog = commands.Cog
cafe = ID.cafe
Fenne = 474984052017987604 
Equinox = 599059234134687774
r1 = id_0.fenne
rcheck = id_0.check
r3 = id_0.heart
r4 = id_0.P_heart
r5 = id_0.thumb_up
null = None
botuser = 966392608895152228 

class special(commands.Cog):
  def __init__(self, bot):
    self.bot=bot
    
  @cog.listener()
  async def on_message(self, msg):
    if msg.guild is None:
      return

    if msg.author.id == botuser:
      return

    if msg.content.startswith(".speak") and msg.channel.id == cafe.AP.cmds:
      message = msg.content.removeprefix(".speak").lstrip()
      if message.endswith("GEN"):
        cha = self.bot.get_channel(cafe.chat.gen) or await self.bot.fetch_channel(cafe.chat.gen)
        text=message.removesuffix("GEN")
      elif message.endswith("MOD"):
        cha = self.bot.get_channel(cafe.chat.mod) or await self.bot.fetch_channel(cafe.chat.mod)
        text=message.removesuffix("MOD")
      elif message.endswith("NONE"):
        cha=msg.channel
        text = message.removesuffix("NONE")
      if msg.content.split()[-3] == "@":
        ping = msg.content.split()[-2]
        content = text.split()
        del content[-1] 
        del content[-1]
        tex = ' '.join(content)
        await cha.send(f"{tex}<@{ping}>")
      else:
        await cha.send(text)
    elif msg.channel.id != cafe.verify:
      if msg.channel.category_id != cafe.cats.verify:
        return

      if msg.reference == None:
        return

      welcomed= discord.Object(id=889011345712894002)
      unwelcomed= discord.Object(id=889011029428801607)
      admin= discord.utils.get(msg.author.guild.roles, name="Server Staff")
      reply = msg.reference.resolved
      member = reply.author
      gen = self.bot.get_channel(cafe.chat.gen) or await self.bot.fetch_channel(cafe.chat.gen)
      verify_logs = self.bot.get_channel(ID.fbc.logs.verify) or await self.bot.fetch_channel(ID.fbc.logs.verify)
      denied_logs = self.bot.get_channel(ID.fbc.logs.verify) or await self.bot.fetch_channel(ID.fbc.logs.denied)
      if admin not in msg.author.roles:
        return
      
      if msg.content == ".deny":
        await member.timeout(datetime.timedelta(days=7, reason="denied application try again later")) 
        time = await msg.channel.send("time holder(dont delete)")
        await verify_logs.send(f"\tDenied <@{member.id}>\n Denied id: {member.id}\nDenied:{member}\n{reply.content}\n\nDenied by: <@{msg.author.id}>\nDenied by user: {msg.author}\n\nDenied at: {time.created_at}")
        await msg.channel.delete()

      if msg.content == ".verify":
        await member.remove_roles(unwelcomed)
        await member.add_roles(welcomed)
        if msg.author.id == Fenne:
          await gen.send(f"Welcome <@{member.id}> please make a <#{cafe.friends.bio}> and enjoy your stay.")
        else:
          await gen.send(f"Welcome <@{member.id}> please make a <#{cafe.friends.bio}> and enjoy your stay. Welcomed by <@{msg.author.id}>")
        time = await msg.channel.send("time holder(dont delete)")
        await verify_logs.send(f"\tWelcome <@{member.id}>\nWelcome id: {member.id}\nWelcome:{member}\n{reply.content}\n\nWelcomed by: <@{msg.author.id}>\nWelcomer: {msg.author}\n\nWelcomed at: {time.created_at}")
        await msg.channel.delete()
