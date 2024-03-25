import discord, json, requests, datetime, time
from bs4 import BeautifulSoup
from discord.ext import commands, tasks

with open("json/setting.json", "r", encoding="utf-8") as f:
    systemData = json.load(f)

with open("json/search.json", "r", encoding="utf-8") as f:
    allSearchList = json.load(f)


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    "cookie": "over18=1",
}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
bot.remove_command("help")


def nowTime():
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=+8)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def sleep():
    time.sleep(0.3)


@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="PTT /help")
    )
    # autoSend.start()


@bot.command()
async def add(ctx, *args):
    print(nowTime(), "add", args)
    try:
        if ctx.channel.id not in [*allSearchList]:
            allSearchList[ctx.channel.id] = {"HardwareSale": [], "Rent_tao": []}
        searchList = allSearchList[ctx.channel.id]
        if len(args) < 2:
            raise
        category = args[0]
        if category.isnumeric():
            categoryID = int(category)
            if categoryID >= len(searchList):
                raise
            category = [*searchList][categoryID]
        if category not in searchList.keys():
            raise
        response = ""
        for arg in args[1:]:
            if arg not in searchList[category]:
                searchList[category].append(arg)
                response = (
                    "`" + arg + "`" if response == "" else response + ", `" + arg + "`"
                )
        print(
            json.dumps(allSearchList, ensure_ascii=False, indent=4),
            end="",
            file=open("json/search.json", "w", encoding="utf-8"),
        )
        await ctx.send(f"Add {response} success!")
    except:
        embed = discord.Embed(
            title="How to use **add** command",
            description="/add [category/ID] [keyWord] [keyWord] ...",
            color=discord.Colour.orange(),
        )
        embed.add_field(
            name="[category]", value="0: HardwareSale\n1: Rent_tao", inline=False
        )
        embed.add_field(name="[keyWord]", value="What you want to search", inline=False)
        await ctx.send(embed=embed)


@bot.command()
async def delete(ctx, *args):
    print(nowTime(), "delete", args)
    try:
        if ctx.channel.id not in [*allSearchList]:
            await ctx.send(f"Delete Nothing!")
            return
        searchList = allSearchList[ctx.channel.id]
        if len(args) < 2:
            raise
        category = args[0]
        if category.isnumeric():
            categoryID = int(category)
            if categoryID >= len(searchList):
                raise
            category = [*searchList][categoryID]
        if category not in searchList.keys():
            raise
        response = ""
        for arg in args[1:]:
            if arg in searchList[category]:
                searchList[category].remove(arg)
                response = (
                    "`" + arg + "`" if response == "" else response + ", `" + arg + "`"
                )
        print(
            json.dumps(allSearchList, ensure_ascii=False, indent=4),
            end="",
            file=open("json/search.json", "w", encoding="utf-8"),
        )
        if response == "":
            await ctx.send(f"Delete Nothing!")
        else:
            await ctx.send(f"Delete {response} success!")
    except:
        embed = discord.Embed(
            title="How to use **delete** command",
            description="/delete [category/ID] [keyWord] [keyWord] ...",
            color=discord.Colour.orange(),
        )
        embed.add_field(
            name="[category]", value="0: HardwareSale\n1: Rent_tao", inline=False
        )
        embed.add_field(
            name="[keyWord]", value="What keyword you want to delete", inline=False
        )
        await ctx.send(embed=embed)


# @bot.command()
# async def list(ctx, *args):
#     print(nowTime(), "list", args)
#     response = (
#         "Nothing" if len(searchList) == 0 else "`" + "`, `".join(searchList) + "`"
#     )
#     embed = discord.Embed(
#         title="Search List", description=response, color=discord.Colour.orange()
#     )
#     await ctx.send(embed=embed)


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


async def sendAritcle(channelID, pageID, articleData, historyData):
    for search in allSearchList[channelID][articleData["category"]]:
        if not search in articleData["title"]:
            continue
        historyData[pageID] = articleData
        with open("json/history.json", "w", encoding="utf-8") as f:
            json.dump(historyData, f, indent=4)
        channel = bot.get_channel(channelID)
        embed = discord.Embed(
            title=articleData["title"],
            url=articleData["url"],
            color=discord.Colour.orange(),
        )
        embed.add_field(name="Category", value=articleData["category"], inline=True)
        embed.add_field(name="Author", value=articleData["author"], inline=True)
        embed.add_field(name="Date", value=articleData["date"], inline=True)
        returnString = ""
        for search in allSearchList[channelID][articleData["category"]]:
            if search in articleData["title"]:
                returnString += search + " "
        embed.add_field(
            name="KeyWord",
            value=returnString,
            inline=True,
        )
        embed.set_footer(text=f"{nowTime()}")
        await channel.send(embed=embed)
        break


@tasks.loop(seconds=20.0)
async def autoSend():
    print(nowTime(), "autoSend")
    with open("json/history.json", "r", encoding="utf-8") as f:
        historyData = json.load(f)
    for channelID in allSearchList:
        searchList = allSearchList[channelID]
        for key in searchList:
            sleep()
            if searchList[key] == []:
                continue
            url = f"https://www.ptt.cc/bbs/{key}/index.html"
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text.encode("utf-8"), "html.parser")
            articles = soup.find_all("div", class_="r-ent")
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
                pageID = url.split("/")[-1].split(".html")[0]
                userID = article.find("div", class_="author").text.strip()
                if pageID in historyData:
                    continue
                articleData = {
                    "title": title,
                    "url": "https://www.ptt.cc" + url,
                    "category": key,
                    "author": userID,
                    "date": article.find("div", class_="date").text.strip(),
                }
                await sendAritcle(channelID, pageID, articleData, historyData)


bot.run(systemData["TOKEN"])
