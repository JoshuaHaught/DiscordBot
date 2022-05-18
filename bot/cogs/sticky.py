import discord
from discord.ext import tasks, commands
import sys
sys.path.append('..')
from extras.text_zone import BIG as b
from extras.text_zone import all_id as id_0
import extras.System_Id as ID

cog = commands.Cog
botuser = 966392608895152228
cafe = ID.cafe
class sticky(commands.Cog):
  def __init__(self, bot):
    self.bot=bot
  
  @cog.listener()
  async def on_message(self, msg):
    if msg.guild is None:return
    if msg.author.id == botuser:return
    def is_me(msg):
      return msg.author.id == botuser
    if msg.channel.id == cafe.Chat.Promo:
      cha = self.bot.get_channel(cafe.Chat.Promo) or await self.bot.fetch_channel(cafe.Chat.Promo)
      await cha.purge(limit=2, check=is_me)
      await cha.send("Server boosters can post <#904501391299608586> in every 30 minutes!")
    elif msg.channel.id == cafe.Chat.Bio:
      cha = self.bot.get_channel(cafe.Chat.Bio) or await self.bot.fetch_channel(cafe.Chat.Bio)   
      await cha.purge(limit=2, check=is_me)
      await cha.send(b.bt)
    elif msg.channel.id == 973436882799177768:
      cha = self.bot.get_channel(973436882799177768) or await self.bot.fetch_channel(973436882799177768)
      await cha.purge(limit=2, check=is_me)
      await cha.send("This is only for asking members to DM. Any advertising of your own DM's or friend requests may be removed and warned!")
    elif msg.channel.id == 976322762631172147:
      cha = self.bot.get_channel(976322762631172147) or await self.bot.fetch_channel(976322762631172147)
      await cha.purge(limit=2, check=is_me)
      await cha.send("Connect Post Example:\n```Status:\nMood:\nTopics of interest right now:```\n\nMust be text only, you can delete your status at any time!")