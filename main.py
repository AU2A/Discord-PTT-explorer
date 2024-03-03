import discord, json, requests
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from time import gmtime, strftime


with open("json/setting.json", "r", encoding="utf-8") as f:
    systemData = json.load(f)

with open("json/search.json", "r", encoding="utf-8") as f:
    searchList = json.load(f)["keyWord"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    "cookie": "over18=1",
}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
bot.remove_command("help")


def nowTime():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")
    autoSend.start()


@bot.command()
async def add(ctx, *args):
    print(nowTime(), "add", args)
    if len(args) == 0:
        await ctx.send(f"Add What?")
    else:
        response = ""
        for arg in args:
            if arg not in searchList:
                searchList.append(arg)
                response = (
                    "`" + arg + "`" if response == "" else response + ", `" + arg + "`"
                )
        print(
            json.dumps({"keyWord": searchList}, ensure_ascii=False),
            end="",
            file=open("json/search.json", "w", encoding="utf-8"),
        )
        await ctx.send(f"Add {response} success!")


@bot.command()
async def delete(ctx, *args):
    print(nowTime(), "delete", args)
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
        print(
            json.dumps({"keyWord": searchList}, ensure_ascii=False),
            end="",
            file=open("json/search.json", "w", encoding="utf-8"),
        )
        if response == "":
            await ctx.send(f"Delete Nothing!")
        else:
            await ctx.send(f"Delete {response} success!")


@bot.command()
async def list(ctx, *args):
    print(nowTime(), "list", args)
    response = (
        "Nothing" if len(searchList) == 0 else "`" + "`, `".join(searchList) + "`"
    )
    embed = discord.Embed(
        title="Search List", description=response, color=discord.Colour.orange()
    )
    await ctx.send(embed=embed)


@bot.command()
async def help(ctx, *args):
    print(nowTime(), "help", args)
    embed = discord.Embed(
        title="PTT Explorer",
        description="What U can use",
        color=discord.Colour.orange(),
    )
    embed.add_field(name="/add", value="Add search words", inline=False)
    embed.add_field(name="/delete", value="Delete search words", inline=False)
    embed.add_field(name="/list", value="Show search words", inline=False)
    await ctx.send(embed=embed)


@tasks.loop(seconds=20.0)
async def autoSend():
    print(nowTime(), "autoSend")
    with open("json/history.json", "r", encoding="utf-8") as f:
        historyData = json.load(f)
    url = "https://www.ptt.cc/bbs/HardwareSale/index.html"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text.encode("utf-8"), "html.parser")
    articles = soup.find_all("div", class_="r-ent")
    newArticle = []
    for article in articles:
        url = article.find("a")["href"] if article.find("a") else ""
        if url == "":
            continue
        title = article.find("div", class_="title").text.strip()
        if "[公告]" in title:
            continue
        if "刪除" in title:
            continue
        if "徵" in title:
            continue
        ID = url.split("/")[-1].split(".html")[0]
        if ID in historyData:
            continue
        if searchList != []:
            for search in searchList:
                if search in title:
                    articleData = {
                        "date": article.find("div", class_="date").text.strip(),
                        "title": title,
                        "url": "https://www.ptt.cc" + url,
                    }
                    historyData[ID] = articleData
                    with open("json/history.json", "w", encoding="utf-8") as f:
                        json.dump(historyData, f, indent=4)
                    channel = bot.get_channel(systemData["channel_id"])
                    embed = discord.Embed(
                        title=articleData["title"],
                        url=articleData["url"],
                        color=discord.Colour.orange(),
                    )
                    embed.add_field(
                        name="Date", value=articleData["date"], inline=False
                    )
                    returnString = ""
                    for search in searchList:
                        if search in title:
                            returnString += search + " "
                    embed.add_field(
                        name="KeyWord",
                        value=returnString,
                        inline=False,
                    )
                    await channel.send(embed=embed)
                    break


bot.run(systemData["TOKEN"])
