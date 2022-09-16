import discord
import random
import math
import extras.IDS as ID
from extras.buttons import YesNo
from extras.card_generator import Generator
from extras.pages import BaseButtonPaginator
from passcodes import main
from discord.ext import commands
from wantstoparty._async import WantsToParty # made this myself :D
from io import BytesIO

XP_PER_LEVEL = 350
XP_PER_LEVEL_100 = 600
MSG_ATTACHMENT_XP_RATE = 5
EMBED_COLOR = 0xea69a5

def levelup_msg(msg, lvl):
    user = msg.author.mention

    if lvl == 100:
        warn = f"\n*Because you've reached level 100, XP per level is now {XP_PER_LEVEL_100}, not {XP_PER_LEVEL}!*"
    else:
        warn = ""

    msgs = [
        f"Yay, {user} has reached **level {lvl}**! Keep going! <a:woot:917617832655740969>{warn}",
        f"Woah, {user} has reached **level {lvl}**! Amazing! <a:woohoo:989342765672456222>{warn}",
        f"{user} has levelled up to **{lvl}**! Keep on going! <a:yay:989342786014810215>{warn}",
        f"{user}, Look at you go! You've reached **level {lvl}**! <:smug:961701793971175484>{warn}"
    ]
    
    return msgs

def calculate_level(xp, difficult=False):
    """Calculates a level based on the XP given."""
    xp_per = XP_PER_LEVEL if not difficult else XP_PER_LEVEL_100
    return math.trunc(xp / xp_per)

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 2, commands.BucketType.member)
    
        self.msg_attachment_xp_rate = 5

        self.wtp = WantsToParty(api_key=main.wtp_key, subdomain="femboy")

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return
        
        if msg.guild.id != ID.server.cafe or not msg.guild:
            return
        
        bucket = self.cooldown.get_bucket(msg)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            return # sending messages too quickly - likely spamming.
        
        xp = await self.bot.config.find(123)
        
        rand_xp = random.randint(2, 8)

        if not xp:
            await self.bot.config.upsert({"_id": 123, "doublexp": False})

        data = await self.bot.levels.find(msg.author.id)
        
        xp_per_level = XP_PER_LEVEL if data["level"] < 100 else XP_PER_LEVEL_100

        if msg.channel.id == ID.cafe.media.selfie:
            if not data or data.get("level", 0) < 3:
                await msg.delete()
                return await msg.author.send("Sorry, you must reach level 3 by chatting before you can post selfies. Thanks for understanding!")

        xp_rate = rand_xp if not xp["doublexp"] else rand_xp * 2

        if not data:
            await self.bot.levels.upsert(
                {
                    "_id": msg.author.id,
                    "xp": xp_rate,
                    "level": 0
                }
            )
        else:
            current_xp = data["xp"]
            level_to_get = data["level"] + 1
            xp_required = level_to_get * xp_per_level
            
            if current_xp >= xp_required:
                await self.bot.levels.upsert(
                    {
                        "_id": msg.author.id,
                        "xp": data["xp"] + xp_rate if not msg.attachments else data["xp"] + self.msg_attachment_xp_rate,
                        "level": level_to_get
                    }
                )
                
                bot = msg.guild.get_channel(ID.cafe.chat.bot)
                await bot.send(random.choice(levelup_msg(msg, level_to_get)))
            else:
                await self.bot.levels.upsert(
                    {
                        "_id": msg.author.id,
                        "xp": data["xp"] + xp_rate if not msg.attachments else data["xp"] + self.msg_attachment_xp_rate
                    }
                )

    @commands.command(hidden=True)
    async def fixlevels(self, ctx):
        """Fixes levels for everyone if there's a change in XPs needed per level."""
        if ctx.guild.id != ID.server.fbc:
            return

        if ctx.author.id != 599059234134687774:
            return

        data = await self.bot.levels.get_all()

        msg = await ctx.send("Working on it...")
        changed = 0
        for item in data:
            if item["level"] < 100:
                dif = False
            else:
                dif = True
            
            actual_level = calculate_level(item["xp"], dif)
            if item["level"] != actual_level:
                await self.bot.levels.upsert(
                    {
                        "_id": item["_id"],
                        "xp": item["xp"],
                        "level": actual_level
                    }
                )
                changed += 1

        await msg.edit(f"All done! Updated {changed} members' levels.")
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def addxp(self, ctx, member: discord.Member, xp: int):
        """(Fenne only) Adds XP to a member."""
        cur_xp = await self.bot.levels.find(member.id)

        if not cur_xp:
            return await ctx.send("I can't do that because they need some XP first.") 

        new_xp = cur_xp["xp"] + xp
        if cur_xp["level"] < 100:
            dif = False
        else:
            dif = True

        new_level = calculate_level(new_xp, dif)

        confirm = YesNo()
        confirm.ctx = ctx

        msg = await ctx.send(f"Are you sure you want add to the XP? Their new XP will be **{new_xp}** and new level will be **{new_level}**.", view=confirm)

        await confirm.wait()
        if not confirm.value:
            return await msg.delete()
        
        await msg.delete()

        await self.bot.levels.upsert(
            {
                "_id": member.id,
                "xp": new_xp,
                "level": new_level
            }
        )
        await ctx.send(f"Added {xp} XP to {member.display_name}! :tada:")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def removexp(self, ctx, member: discord.Member, xp: int):
        """(Fenne only) Adds XP to a member."""
        cur_xp = await self.bot.levels.find(member.id)

        if not cur_xp:
            return await ctx.send("I can't do that because they need some XP first.") 

        new_xp = cur_xp["xp"] - xp
        if cur_xp["level"] < 100:
            dif = False
        else:
            dif = True
        
        new_level = calculate_level(new_xp, dif)

        if new_xp < 0:
            return await ctx.send("That will make their XP negative and blow the bot up! >:o")

        confirm = YesNo()
        confirm.ctx = ctx

        msg = await ctx.send(f"Are you sure you want to remove the XP? Their new XP will be **{new_xp}** and new level will be **{new_level}**.", view=confirm)

        await confirm.wait()
        if not confirm.value:
            return await msg.delete()
        
        await msg.delete()

        await self.bot.levels.upsert(
            {
                "_id": member.id,
                "xp": new_xp,
                "level": new_level
            }
        )
        await ctx.send(f"Removed {xp} XP from {member.display_name}.")


    @commands.hybrid_command()
    @discord.app_commands.guilds(ID.server.fbc, ID.server.cafe)
    async def rank(self, ctx, member: discord.Member=None):
        """Shows a members XP and level from talking."""
        member = member if member else ctx.author

        data = await self.bot.levels.find(member.id)
        all_data = await self.bot.levels.get_all()

        
        all_data.sort(key=lambda item: item.get("xp"), reverse=True) # sort ranks in descending order

        index = 1
        for entry in all_data:
            if entry["_id"] == member.id:
                break
            index += 1

        xp_per_level = XP_PER_LEVEL if data["level"] < 100 else XP_PER_LEVEL_100
        xp = data["xp"]
        level = data["level"]
        lvl_xp = xp - (level * xp_per_level)
        rank = index
        next_xp = (level * xp_per_level) - (level + 1 * xp_per_level)
        xp_needed = ((level + 1) * xp_per_level) - xp

        if not data.get("bg"):
            if random.randint(0, 3) == 1:
                msg = ":bulb: **Tip:** you can customize your card by changing the background or text color! Use `.card color` or `.card bg`."
            else:
                msg = None
        else:
            msg = None

        card_data = {
            "bg_image": data.get("bg") if data.get("bg") else "https://media.discordapp.net/attachments/956915636582379560/995857644415889508/rank-card.png", # change to bg when fen gives it
            "profile_image": member.display_avatar.url,
            "level": level,
            "user_xp": lvl_xp,
            "next_xp": xp_per_level,
            "xp_needed": xp_needed,
            "user_position": rank,
            "user_name": member.name,
            "user_status": member.raw_status,
            "color": data.get("color") if data.get("color") else "#1b1b1b",
            "total": xp
        }

        img = Generator().generate_profile(**card_data)

        file = discord.File(fp=img, filename="rank.png")

        await ctx.send(content=msg, file=file)   
    
    @commands.group(invoke_without_command=True)
    async def card(self, ctx):
        await ctx.send("Do `.card bg` to change the background or `.card color` to change the color.")
    
    @card.command(aliases=["bg"])
    async def background(self, ctx):
        if not ctx.message.attachments:
            return await ctx.send("Please add (attach) an image when using this command!")
        
        attachment = ctx.message.attachments[0]
        extension = attachment.filename.split(".")
        extension = extension[len(extension)-1] 

        file = BytesIO(await attachment.read())
        
        url = await self.wtp.upload_from_bytes(file, extension)

        await self.bot.levels.upsert({"_id": ctx.author.id, "bg": str(url)})

        await ctx.send(f"All done!")


    @card.command(aliases=["colour"])
    async def color(self, ctx, hex=None):
        """Changes the colour of the text on the level card."""
        if not hex:
            return await ctx.send("To pick the text color, go to <https://rgbacolorpicker.com/hex-color-picker> and copy the hex code at the top.")
        
        if not hex.startswith("#"):
            hex = "#" + str(hex)

        await self.bot.levels.upsert({"_id": ctx.author.id, "color": hex})
        await ctx.send(f"All done! Card **text** color set to {hex}")

    @commands.hybrid_command(aliases=["lb"])
    @discord.app_commands.guilds(ID.server.fbc, ID.server.cafe)
    async def leaderboard(self, ctx):
        """Shows the top 15 people on the leaderboard."""
        if ctx.guild.id != ID.server.cafe:
            return await ctx.send("that command doesnt work in this server rn sorry")

        data = await self.bot.levels.get_all()
        data.sort(key=lambda item: item.get("xp"), reverse=True)
        
        out = []
        place = 1
        for item in data:
            member = ctx.guild.get_member(item["_id"])
            xp = "{:,}".format(item['xp'])
            if not member:
                return await self.bot.levels.delete(item["_id"])
            if place == 1:
                out.append(f":first_place: {member.mention} {xp} XP (level {item['level']})")
            elif place == 2:
                out.append(f":second_place: {member.mention} {xp} XP (level {item['level']})")
            elif place == 3:
                out.append(f":third_place: {member.mention} {xp} XP (level {item['level']})")
            else:
                out.append(f"**{place}.** {member.mention} {xp} XP (level {item['level']})")

            place += 1

        class Pages(BaseButtonPaginator):
            async def format_page(self, entries):
                embed = discord.Embed(
                    title="Leaderboard",
                    color=EMBED_COLOR
                )
                embed.description = "\n".join(entries)
                embed.set_author(name=f"Page {self.current_page}/{self.total_pages}")
                embed.set_footer(text=f"{len(out)} members on the leaderboard.")

                return embed

        await Pages.start(ctx, entries=out, per_page=15)

    @commands.command(hidden=True, name="doublexp")
    @commands.is_owner()
    async def doublexp(self, ctx):
        """(Fenne only) Enables double XP for everyone."""
        data = await self.bot.config.find(123)
        if not data["doublexp"]:
            confirm = YesNo()
            confirm.ctx = ctx
            msg = await ctx.send("**Double XP is not enabled.**\n\nDo you want to enable it?", view=confirm)

            await confirm.wait()
            if confirm.value:
                await self.bot.config.upsert({"_id": 123, "doublexp": True})
                await msg.delete()
                await msg.delete()
        
        else:
            confirm = YesNo()
            confirm.ctx = ctx
            msg = await ctx.send("**Double XP is enabled.**\n\nDo you want to disable it?", view=confirm)

            await confirm.wait()
            if confirm.value:
                await self.bot.config.upsert({"_id": 123, "doublexp": False})
                await msg.delete()
                await ctx.send("Double XP has been disabled.")
            else:
                await msg.delete()
    
    @commands.hybrid_command(aliases=["howlevelsworks"])
    @discord.app_commands.guilds(ID.server.fbc, ID.server.cafe)
    async def howxpworks(self, ctx):
        """Sends a message on how XP works."""
        content = """It works by adding between 2 and 8 XP (at random) every time you send a message (unless double XP is turned on, in which it's... you guessed it, double). Messages containing attachments (images, videos, etc) also get 5 extra XP on top of what you're already getting.

If you're level 100+, you'll need 600XP to advance a level.

You gain levels when you reach a number of XP which is a multiple of 350 (350, 700, 1050, etc...)

You can use `.rank` to check your statistics and `.leaderboard` to see who has the most XP in the entire server.

Spamming does not benefit you when it comes to gaining XP as there's a short cooldown period after sending a message. 

**Leaving the server resets your XP!**"""
        e = discord.Embed(title="How the levelling system works", color=EMBED_COLOR)
        e.description = content

        await ctx.send(embed=e)

    @commands.hybrid_command(aliases=["levelstatus"])
    @discord.app_commands.guilds(ID.server.fbc, ID.server.cafe)
    async def xpstatus(self, ctx):
        """Shows the current status on the levelling system."""
        data = await self.bot.config.find(123)
        if data["doublexp"] == True:
            doublexp = "Enabled - chatting will give you double XP"
        else:
            dobulexp = "Disabled - XP is not doubled."
        
        content = f"XP is random per-message. You get between 2 and 8 XP.\nSending media is a 5 XP bonus!\n\nDouble XP: {doublexp}"

        e = discord.Embed(color=EMBED_COLOR, title="XP Status")
        e.description = content

        await ctx.send(embed=e)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        ex=[760928339589726209]
        if member.id in ex:
            return
        try:
            await self.bot.levels.delete(member.id)
        except:
            pass