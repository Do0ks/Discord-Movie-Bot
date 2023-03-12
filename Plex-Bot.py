import discord
import random
import os
from dotenv import load_dotenv
import requests
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_choice, create_option
from plexapi.video import Movie, Video
from plexapi.server import PlexServer
from plexapi.mixins import PosterUrlMixin

load_dotenv()
#_________________________________Fill This Out_________________________________________#
# Prerequisites
# pip install --no-cache-dir -r requirements.txt

#web address to Plex server e.g., http://192.168.1.19:32400
#Leave the ' '
baseurl = os.getenv('baseurl')

#Plex token. See: https://www.plexopedia.com/plex-media-server/general/plex-token/
#Leave the ' '
plextoken = os.getenv('plextoken')

#Discord bot token.
#Leave the " "
discordtoken = os.getenv('discordtoken')

#To get system(below), run the bot with the above filled out. In the console it'll print out avalable clients to connect to.
#After first run, stop the bot and place the client in the system = field.
#Leave the " "
system = os.getenv('system')

#Add the voice channel ID to connect to.
voicechannel = os.getenv('voicechannel')
#________________________________________________________________________________________#
plex = PlexServer(baseurl, plextoken)

Bot_Prefix = "!"
intents = discord.Intents.default()
bot = commands.Bot(command_prefix=Bot_Prefix, case_insensitive=True, self_bot=False, HelpCommand=False, intents=intents)
slash = SlashCommand(bot, sync_commands=True)

print("|_____________Available clients on local network_____________|")
clients = []
for client in plex.clients():
    clients.append(client.title)
    print(f"| •Name: \033[4m{client.title}\033[0m ({client.product})")
print("|____________________________________________________________|")

if clients[0] != system:
    print(f"{system} doesn't apper to be online. Quitting. ⛔")
    quit()
else:
    print(f"{system} online. ✔️")

movielist = []
movies = plex.library.section('Movies')
for video in movies.search():
    movielist.append('%s' % (video.title))
moviecount = len(movielist)
print(f"Loaded {moviecount} Movies. ✔️")

p = 0
r = 0


@slash.slash(name="Help", description="Pulls the help menu.")
async def help(ctx):
    embed = discord.Embed(title="Help", description=" ", color=0xf5dd03)
    embed.add_field(name="``/search <keyword>``", value="```fix\nUse this command to lookup a movies that has the keyword mentioned in the title.```", inline=False)
    embed.add_field(name="``/info <movie>``", value="```fix\nUse this command to get information about a movie like ratings, summary and duration.```", inline=False)
    embed.add_field(name="``/play <movie>``",value="```fix\nUse this command to play a movie (best to use search first then copy the movie title in the movie field).```",inline=False)
    embed.add_field(name="``/shuffle``",value="```fix\nUse this command if your not sure what to watch. Picks a random movie and plays it.```",inline=False)
    embed.add_field(name="``/pause``",value="```fix\nUse this command to pause the currently playing movie.```",inline=False)
    embed.add_field(name="``/resume``", value="```fix\nUse this command to resume the previously paused movie.```", inline=False)
    embed.add_field(name="``/stop``", value="```fix\nUse this command to stop the current movie from playing.```", inline=False)
    embed.set_footer(text="<keyword> = a word inside the title. \n⠀e.g., /search bob gets every movie with the word 'bob' in the title\n<movie> = movie title. \n⠀e.g., /play Step Brothers. (punctuation  matters)")
    await ctx.send(embed=embed)


@slash.slash(name="Search", description="Search a movie with a keyword.")
async def search(ctx, *, keyword):
    movie = []
    movies = plex.library.section('Movies')
    try:
        for video in movies.search(keyword):
            movie.append('%s' % (video.title))
        results = ('\n •'.join(movie))
        if movie == []:
            results = "No Movies Found!"
        embed = discord.Embed(title=f"__Search Results:__", description=f"•{results}", color=0xf5dd03)
        embed.set_footer(text=f"Keyword: {keyword}")
        await ctx.send(embed=embed)
    except:
        await ctx.send("Error!!")


@slash.slash(name="Info", description="Get information about a movie.")
async def info(ctx, *, movie):
    try:
        play = plex.library.section('Movies').get(movie)
        client = plex.client(system)
        client.proxyThroughServer()
        image = PosterUrlMixin.thumbUrl.fget(play)
        img_data = requests.get(image).content
        with open('movie.jpg', 'wb') as handler:
            handler.write(img_data)
        duration = int(play.duration / 60000)
        embed = discord.Embed(title=f"Infor For: {movie}", description=f"{play.summary}\n\n**Rotten Tomatoes Rating:** {play.audienceRating}\n**Content Rating:** {play.contentRating}\n**Duration:** {duration} Minutes", color=0xf5dd03)
        file = discord.File(f"{os.getcwd()}/movie.jpg", filename="movie.jpg")
        embed.set_image(url="attachment://movie.jpg")
        embed.set_footer(text=f"{play.year} - {play.studio}")
        await ctx.send(file=file, embed=embed)
    except:
        embed = discord.Embed(title=f"I couldn't find: {movie}.", description="If you're having trouble, use /search to search for the movie then copy and paste (punctuation matters).", color=0xf5dd03)
        await ctx.send(embed=embed)


@slash.slash(name="Play", description="Play a movie.")
async def play(ctx, *, movie):
    try:
        global currentlyplaying
        global savemovietitle
        savemovietitle=movie
        play = plex.library.section('Movies').get(movie)
        client = plex.client(system)
        client.proxyThroughServer()
        client.playMedia(play)
        client.setParameters(volume=100, shuffle=0, repeat=0)
        image = PosterUrlMixin.thumbUrl.fget(play)
        img_data = requests.get(image).content
        with open('movie.jpg', 'wb') as handler:
            handler.write(img_data)
        duration = int(play.duration / 60000)
        embed = discord.Embed(title=f"Playing: {movie}", description=f"{play.summary}\n\n**Rotten Tomatoes Rating:** {play.audienceRating}\n**Content Rating:** {play.contentRating}\n**Duration:** {duration} Minutes", color=0xf5dd03)
        file = discord.File(f"{os.getcwd()}/movie.jpg", filename="movie.jpg")
        embed.set_image(url="attachment://movie.jpg")
        embed.set_footer(text=f"{play.year} - {play.studio}")
        await ctx.send(file=file, embed=embed)
    except:
        embed = discord.Embed(title=f"I couldn't find: {movie}.", description="If you're having trouble, use /search to search for the movie then copy and paste (punctuation matters).", color=0xf5dd03)
        await ctx.send(embed=embed)


@slash.slash(name="Stop", description="Stop the current movie.")
async def stop(ctx):
    global savemovietitle
    currentlyplaying = plex.sessions()
    if currentlyplaying == []:
        embed = discord.Embed(title=f"Ops!", description="Nothing currently playing.", color=0xf5dd03)
        await ctx.send(embed=embed)
    else:
        client = plex.client(system)
        client.proxyThroughServer()
        client.stop()
        embed = discord.Embed(title=f"__Stopped Playing__:", description=f"{savemovietitle}", color=0xf5dd03)
        await ctx.send(embed=embed)


@slash.slash(name="Pause", description="Pause the currently movie.")
async def pause(ctx):
    global savemovietitle
    currentlyplaying = plex.sessions()
    if p==1:
        embed = discord.Embed(title=f"Ops!", description=f"{savemovietitle} is already paused.", color=0xf5dd03)
        await ctx.send(embed=embed)
    else:
        client = plex.client(system)
        client.proxyThroughServer()
        client.pause()
        embed = discord.Embed(title=f"__Paused__:", description=f"{savemovietitle}", color=0xf5dd03)
        await ctx.send(embed=embed)


@slash.slash(name="Resume", description="Resume the previously played movie.")
async def resume(ctx):
    global savemovietitle
    currentlyplaying = plex.sessions()
    if r==1:
        embed = discord.Embed(title=f"Ops!", description=f"{savemovietitle} is already playing.", color=0xf5dd03)
        await ctx.send(embed=embed)
    else:
        client = plex.client(system)
        client.proxyThroughServer()
        client.play()
        embed = discord.Embed(title=f"__Resumed__:", description=f"{savemovietitle}", color=0xf5dd03)
        await ctx.send(embed=embed)


@slash.slash(name="Shuffle", description="Play a random movie. Please wait...")
async def shuffle(ctx):
    global currentlyplaying
    global savemovietitle
    rc = random.choice(movielist)
    savemovietitle = rc
    play = plex.library.section('Movies').get(rc)
    client = plex.client(system)
    client.proxyThroughServer()
    client.playMedia(play)
    client.setParameters(volume=100,shuffle=0,repeat=0)
    image = PosterUrlMixin.thumbUrl.fget(play)
    img_data = requests.get(image).content
    with open('movie.jpg', 'wb') as handler:
        handler.write(img_data)
    duration = int(play.duration / 60000)
    embed = discord.Embed(title=f"**Playing:** {rc}", description=f"{play.summary}\n\n**Rotten Tomatoes Rating:** {play.audienceRating}\n**Content Rating:** {play.contentRating}\n**Duration:** {duration} Minutes" ,color=0xf5dd03)
    file = discord.File(f"{os.getcwd()}/movie.jpg", filename="movie.jpg")
    embed.set_image(url="attachment://movie.jpg")
    embed.set_footer(text=f"{play.year} - {play.studio}")
    await ctx.send(file=file, embed=embed)
    playtime = int(play.duration / 1000)


@bot.event
async def on_ready():
    try:
        await bot.wait_until_ready()
        for channely in bot.get_all_channels():
            print(channely)
        channel = bot.get_channel(voicechannel)
        print(bot.user, 'is online. ✔️')
        print(f"Connected to voice channel: {channel.name} ✔️")
        await channel.connect()
    except Exception as error:
        print(error)

bot.run(discordtoken, bot=True, reconnect=True)
