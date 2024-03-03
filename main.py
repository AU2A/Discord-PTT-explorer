import discord, json
from discord.ext import commands, tasks

with open("setting.json", "r", encoding="utf8") as f:
    systemData = json.load(f)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
bot.remove_command("help")

searchList = set()


@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")
    autoSend.start()


@bot.command()
async def add(ctx, *args):
    if len(args) == 0:
        await ctx.send(f"Add What?")
    else:
        response = ""
        for arg in args:
            searchList.add(arg)
            response = (
                "`" + arg + "`" if response == "" else response + ", `" + arg + "`"
            )
        await ctx.send(f"Add {response} success!")


@bot.command()
async def delete(ctx, *args):
    if len(args) == 0:
        await ctx.send(f"Delete What?")
    else:
        response = ""
        for arg in args:
            if arg in searchList:
                searchList.remove(arg)
                response = (
                    "`" + arg + "`" if response == "" else response + ", `" + arg + "`"
                )
        if response == "":
            await ctx.send(f"Delete Nothing!")
        else:
            await ctx.send(f"Delete {response} success!")


@bot.command()
async def list(ctx, *args):
    response = (
        "Nothing" if len(searchList) == 0 else "`" + "`, `".join(searchList) + "`"
    )
    embed = discord.Embed(
        title="Search List", description=response, color=discord.Colour.orange()
    )
    await ctx.send(embed=embed)


@bot.command()
async def help(ctx, *args):
    embed = discord.Embed(
        title="PTT Explorer",
        description="What U can use",
        color=discord.Colour.orange(),
    )
    embed.add_field(name="/add", value="Add search words", inline=False)
    embed.add_field(name="/delete", value="Delete search words", inline=False)
    embed.add_field(name="/list", value="Show search words", inline=False)
    await ctx.send(embed=embed)


@tasks.loop(seconds=5.0)
async def autoSend():
    channel = bot.get_channel(systemData["channel_id"])
    await channel.send("GOOD MORNING!")


bot.run(systemData["TOKEN"])
