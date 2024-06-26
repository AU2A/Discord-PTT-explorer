import discord, json, requests, datetime, time, os
from bs4 import BeautifulSoup
from discord.ext import commands, tasks


if os.path.exists("json/setting.json") == False:
    with open("json/setting.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "TOKEN": "YOUR_DISCORD_BOT_TOKEN",
                "Category": [""],
            },
            f,
            indent=4,
        )

if os.path.exists("json/search.json") == False:
    with open("json/search.json", "w", encoding="utf-8") as f:
        json.dump({}, f, indent=4)

if os.path.exists("json/history.json") == False:
    with open("json/history.json", "w", encoding="utf-8") as f:
        json.dump({}, f, indent=4)

with open("json/setting.json", "r", encoding="utf-8") as f:
    systemData = json.load(f)

with open("json/search.json", "r", encoding="utf-8") as f:
    channelSearchList = json.load(f)

categoryList = systemData["Category"]

for channelID in channelSearchList:
    searchList = channelSearchList[channelID]
    for category in categoryList:
        if category not in searchList:
            searchList[category] = []
    channelSearchList[channelID] = searchList
print(
    json.dumps(channelSearchList, ensure_ascii=False, indent=4),
    end="",
    file=open("json/search.json", "w", encoding="utf-8"),
)


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    "cookie": "over18=1",
}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="-", intents=intents)
bot.remove_command("help")


def nowTime():
    return (
        datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=+8)
    ).strftime("%Y-%m-%d %H:%M")


def sleep():
    time.sleep(0.3)


@bot.event
async def on_ready():
    print(f"Login --> {bot.user}")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="PTT -h")
    )
    autoSend.start()


@bot.command()
async def a(ctx, *args):
    print(nowTime(), "add", args)
    try:
        channelID = str(ctx.channel.id)
        if channelID not in [*channelSearchList]:
            channelSearchDict = {}
            for category in categoryList:
                channelSearchDict[category] = []
            channelSearchList[channelID] = channelSearchDict
        searchList = channelSearchList[channelID]
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
            json.dumps(channelSearchList, ensure_ascii=False, indent=4),
            end="",
            file=open("json/search.json", "w", encoding="utf-8"),
        )
        if response == "":
            await ctx.send(f"Add Nothing!")
        else:
            await ctx.send(f"Add {response} success!")
    except:
        embed = discord.Embed(
            title="How to use add command",
            description="-a [category/ID] [keyWord] [keyWord] ...",
            color=discord.Colour.orange(),
        )
        embed.add_field(
            name="[ID: category]",
            value="0: HardwareSale\n1: Rent_tao\nUse -c to see more category.",
            inline=False,
        )
        embed.add_field(
            name="[keyWord]",
            value='What you want to search.\n Use "ALL" to search all posts.',
            inline=False,
        )
        await ctx.send(embed=embed)


@bot.command()
async def c(ctx, *args):
    print(nowTime(), "category", args)
    content = ""
    for i in range(len(categoryList)):
        content += f"{i}: {categoryList[i]}\n"
    embed = discord.Embed(
        title="Category List",
        description=content,
        color=discord.Colour.orange(),
    )
    await ctx.send(embed=embed)


@bot.command()
async def d(ctx, *args):
    print(nowTime(), "delete", args)
    try:
        channelID = str(ctx.channel.id)
        if channelID not in [*channelSearchList]:
            await ctx.send(f"Delete Nothing!")
            return
        searchList = channelSearchList[channelID]
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
        isEmpty = True
        for category in searchList:
            if searchList[category] != []:
                isEmpty = False
                break
        if isEmpty:
            del channelSearchList[channelID]
        print(
            json.dumps(channelSearchList, ensure_ascii=False, indent=4),
            end="",
            file=open("json/search.json", "w", encoding="utf-8"),
        )
        if response == "":
            await ctx.send(f"Delete Nothing!")
        else:
            await ctx.send(f"Delete {response} success!")
    except:
        embed = discord.Embed(
            title="How to use delete command",
            description="-d [category/ID] [keyWord] [keyWord] ...",
            color=discord.Colour.orange(),
        )
        embed.add_field(
            name="[ID: category]",
            value="0: HardwareSale\n1: Rent_tao\nUse -c to see more category.",
            inline=False,
        )
        embed.add_field(
            name="[keyWord]", value="What keyword you want to delete", inline=False
        )
        await ctx.send(embed=embed)


@bot.command()
async def l(ctx, *args):
    print(nowTime(), "list", args)
    channelID = str(ctx.channel.id)
    if channelID not in [*channelSearchList]:
        await ctx.send(f"Nothing")
        return
    searchList = channelSearchList[channelID]
    embed = discord.Embed(title="Search List", color=discord.Colour.orange())
    for category in searchList:
        if searchList[category] != []:
            returnString = ""
            for search in searchList[category]:
                returnString = (
                    "`" + search + "`"
                    if returnString == ""
                    else returnString + ", `" + search + "`"
                )
            embed.add_field(name=category, value=returnString, inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def h(ctx, *args):
    print(nowTime(), "help", args)
    embed = discord.Embed(
        title="PTT Explorer",
        description="What U can use",
        color=discord.Colour.orange(),
    )
    embed.add_field(name="-a", value="Add search words", inline=False)
    embed.add_field(name="-c", value="List all categories", inline=False)
    embed.add_field(name="-d", value="Delete search words", inline=False)
    embed.add_field(name="-l", value="Show search words", inline=False)
    embed.add_field(name="-h", value="Help", inline=False)
    await ctx.send(embed=embed)


async def sendArticle(articleData, channelID, keywordString):
    embed = discord.Embed(
        title=articleData["title"],
        url=articleData["url"],
        color=discord.Colour.orange(),
    )
    embed.add_field(name="Category", value=articleData["category"], inline=True)
    embed.add_field(name="Author", value=articleData["author"], inline=True)
    embed.add_field(name="Date", value=articleData["date"], inline=True)
    embed.add_field(
        name="KeyWord",
        value=keywordString,
        inline=True,
    )
    embed.set_footer(text=f"{nowTime()}")
    channel = bot.get_channel(int(channelID))
    await channel.send(embed=embed)


async def checkArticleInChannel(articleData):
    for channelID in channelSearchList:
        channelInfo = channelSearchList[channelID]
        if channelInfo[articleData["category"]] == []:
            continue
        if "ALL" in channelInfo[articleData["category"]]:
            await sendArticle(articleData, channelID, ".")
            break
        keywordString = ""
        for search in channelInfo[articleData["category"]]:
            keywordString += (search + " ") if search in articleData["title"] else ""
        if keywordString != "":
            await sendArticle(articleData, channelID, keywordString)
            break


async def searchArticles(articles, key):
    with open("json/history.json", "r", encoding="utf-8") as f:
        historyData = json.load(f)
    if key not in [*historyData]:
        historyData[key] = {}
    for article in articles:
        url = article.find("a")["href"] if article.find("a") else ""
        if url == "":
            continue
        title = article.find("div", class_="title").text.strip()
        check = False
        for avoidKeyword in ["公告", "刪除", "徵"]:
            if avoidKeyword in title:
                check = True
                continue
        if check:
            continue
        pageID = url.split("/")[-1].split(".html")[0]
        userID = article.find("div", class_="author").text.strip()
        if pageID in historyData[key]:
            continue
        articleData = {
            "title": title,
            "url": "https://www.ptt.cc" + url,
            "category": key,
            "author": userID,
            "date": article.find("div", class_="date").text.strip(),
        }
        historyData[key][pageID] = articleData
        with open("json/history.json", "w", encoding="utf-8") as f:
            json.dump(historyData, f, indent=4)
        await checkArticleInChannel(articleData)


@tasks.loop(seconds=20.0)
async def autoSend():
    print(nowTime(), "autoSend")
    if [*channelSearchList] == []:
        return
    keyList = [*channelSearchList[[*channelSearchList][0]]]
    for key in keyList:
        sleep()
        url = f"https://www.ptt.cc/bbs/{key}/index.html"
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text.encode("utf-8"), "html.parser")
        articles = soup.find_all("div", class_="r-ent")
        await searchArticles(articles, key)


bot.run(systemData["TOKEN"])
