'''
I made this revision to the code as a more user friendly approch for those who dont want to use dockers and such. 
Make sure you update the file paths, and everything in the "Fill This Out"
This should work without any other requirments. 
'''


import discord
from discord import app_commands
from discord.ext import commands
import random
import requests
from plexapi.video import Movie, Video
from plexapi.server import PlexServer
from plexapi.mixins import PosterUrlMixin

#_________________________________Fill This Out_________________________________________#
baseurl = 'LOCAL_IP_HERE'  # Web address to Plex server e.g., http://192.168.1.19:32400
plextoken = 'PLEX_TOKEN_HERE'  # Plex token. See: https://www.plexopedia.com/plex-media-server/general/plex-token/
discordtoken = "DISCORD_BOT_TOKEN_HERE"  # Discord bot token
system = "SYSTEM_ID_HERE"  # After first run, update this with the client ID
voicechannel = 'VOICE_CHANNEL_ID_HERE'  # Add the voice channel ID to connect to
#________________________________________________________________________________________#

plex = PlexServer(baseurl, plextoken)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

class PlexBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.movielist = []
        self.p = 0
        self.r = 0
        self.system = system
        self.plex = plex
        self.currentlyplaying = None
        self.savemovietitle = ""

        print("|_____________Available clients on local network_____________|")
        clients = []
        for client in plex.clients():
            clients.append(client.title)
            print(f"| •Name: \033[4m{client.title}\033[0m ({client.product})")
        print("|____________________________________________________________|")

        if clients[0] != self.system:
            print(f"{self.system} doesn't appear to be online. Quitting. ⛔")
            quit()
        else:
            print(f"{self.system} online. ✔️")

        movies = plex.library.section('Movies')
        for video in movies.search():
            self.movielist.append('%s' % (video.title))
        moviecount = len(self.movielist)
        print(f"Loaded {moviecount} Movies. ✔️")

    @app_commands.command(name="help", description="Pulls the help menu.")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Help", description=" ", color=0xf5dd03)
        embed.add_field(name="``/search <keyword>``", value="```fix\nUse this command to lookup movies that have the keyword mentioned in the title.```", inline=False)
        embed.add_field(name="``/info <movie>``", value="```fix\nUse this command to get information about a movie like ratings, summary, and duration.```", inline=False)
        embed.add_field(name="``/play <movie>``", value="```fix\nUse this command to play a movie.```", inline=False)
        embed.add_field(name="``/shuffle``", value="```fix\nUse this command if you're not sure what to watch. Picks a random movie and plays it.```", inline=False)
        embed.add_field(name="``/pause``", value="```fix\nUse this command to pause the currently playing movie.```", inline=False)
        embed.add_field(name="``/resume``", value="```fix\nUse this command to resume the previously paused movie.```", inline=False)
        embed.add_field(name="``/stop``", value="```fix\nUse this command to stop the current movie from playing.```", inline=False)
        embed.set_footer(text="<keyword> = a word inside the title.\n<movie> = movie title.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="search", description="Search a movie with a keyword.")
    async def search(self, interaction: discord.Interaction, keyword: str):
        movie = []
        try:
            for video in self.plex.library.section('Movies').search(keyword):
                movie.append('%s' % (video.title))
            results = ('\n •'.join(movie))
            if movie == []:
                results = "No Movies Found!"
            embed = discord.Embed(title=f"__Search Results:__", description=f"•{results}", color=0xf5dd03)
            embed.set_footer(text=f"Keyword: {keyword}")
            await interaction.response.send_message(embed=embed)
        except:
            await interaction.response.send_message("Error!!")

    @app_commands.command(name="info", description="Get information about a movie.")
    async def info(self, interaction: discord.Interaction, movie: str):
        try:
            play = self.plex.library.section('Movies').get(movie)
            client = self.plex.client(self.system)
            client.proxyThroughServer()
            image = PosterUrlMixin.thumbUrl.fget(play)
            img_data = requests.get(image).content
            with open('movie.jpg', 'wb') as handler:
                handler.write(img_data)
            duration = int(play.duration / 60000)
            embed = discord.Embed(title=f"Info For: {movie}", description=f"{play.summary}\n\n**Rotten Tomatoes Rating:** {play.audienceRating}\n**Content Rating:** {play.contentRating}\n**Duration:** {duration} Minutes", color=0xf5dd03)
            file = discord.File("movie.jpg", filename="movie.jpg")
            embed.set_image(url="attachment://movie.jpg")
            embed.set_footer(text=f"{play.year} - {play.studio}")
            await interaction.response.send_message(file=file, embed=embed)
        except:
            embed = discord.Embed(title=f"I couldn't find: {movie}.", description="If you're having trouble, use /search to search for the movie then copy and paste (punctuation matters).", color=0xf5dd03)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="play", description="Play a movie.")
    async def play(self, interaction: discord.Interaction, movie: str):
        try:
            self.savemovietitle = movie
            play = self.plex.library.section('Movies').get(movie)
            client = self.plex.client(self.system)
            client.proxyThroughServer()
            client.playMedia(play)
            client.setParameters(volume=100, shuffle=0, repeat=0)
            image = PosterUrlMixin.thumbUrl.fget(play)
            img_data = requests.get(image).content
            with open('movie.jpg', 'wb') as handler:
                handler.write(img_data)
            duration = int(play.duration / 60000)
            embed = discord.Embed(title=f"Playing: {movie}", description=f"{play.summary}\n\n**Rotten Tomatoes Rating:** {play.audienceRating}\n**Content Rating:** {play.contentRating}\n**Duration:** {duration} Minutes", color=0xf5dd03)
            file = discord.File("movie.jpg", filename="movie.jpg")
            embed.set_image(url="attachment://movie.jpg")
            embed.set_footer(text=f"{play.year} - {play.studio}")
            await interaction.response.send_message(file=file, embed=embed)
        except:
            embed = discord.Embed(title=f"I couldn't find: {movie}.", description="If you're having trouble, use /search to search for the movie then copy and paste (punctuation matters).", color=0xf5dd03)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stop", description="Stop the current movie.")
    async def stop(self, interaction: discord.Interaction):
        self.currentlyplaying = self.plex.sessions()
        if self.currentlyplaying == []:
            embed = discord.Embed(title="Ops!", description="Nothing currently playing.", color=0xf5dd03)
            await interaction.response.send_message(embed=embed)
        else:
            client = self.plex.client(self.system)
            client.proxyThroughServer()
            client.stop()
            embed = discord.Embed(title="__Stopped Playing__:", description=f"{self.savemovietitle}", color=0xf5dd03)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pause", description="Pause the current movie.")
    async def pause(self, interaction: discord.Interaction):
        self.currentlyplaying = self.plex.sessions()
        if self.p == 1:
            embed = discord.Embed(title="Ops!", description=f"{self.savemovietitle} is already paused.", color=0xf5dd03)
            await interaction.response.send_message(embed=embed)
        else:
            client = self.plex.client(self.system)
            client.proxyThroughServer()
            client.pause()
            embed = discord.Embed(title="__Paused__:", description=f"{self.savemovietitle}", color=0xf5dd03)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="resume", description="Resume the previously played movie.")
    async def resume(self, interaction: discord.Interaction):
        self.currentlyplaying = self.plex.sessions()
        if self.r == 1:
            embed = discord.Embed(title="Ops!", description=f"{self.savemovietitle} is already playing.", color=0xf5dd03)
            await interaction.response.send_message(embed=embed)
        else:
            client = self.plex.client(self.system)
            client.proxyThroughServer()
            client.play()
            embed = discord.Embed(title="__Resumed__:", description=f"{self.savemovietitle}", color=0xf5dd03)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shuffle", description="Play a random movie. Please wait...")
    async def shuffle(self, interaction: discord.Interaction):
        rc = random.choice(self.movielist)
        self.savemovietitle = rc
        play = self.plex.library.section('Movies').get(rc)
        client = self.plex.client(self.system)
        client.proxyThroughServer()
        client.playMedia(play)
        client.setParameters(volume=100, shuffle=0, repeat=0)
        image = PosterUrlMixin.thumbUrl.fget(play)
        img_data = requests.get(image).content
        with open('movie.jpg', 'wb') as handler:
            handler.write(img_data)
        duration = int(play.duration / 60000)
        embed = discord.Embed(title=f"**Playing:** {rc}", description=f"{play.summary}\n\n**Rotten Tomatoes Rating:** {play.audienceRating}\n**Content Rating:** {play.contentRating}\n**Duration:** {duration} Minutes", color=0xf5dd03)
        file = discord.File("movie.jpg", filename="movie.jpg")
        embed.set_image(url="attachment://movie.jpg")
        embed.set_footer(text=f"{play.year} - {play.studio}")
        await interaction.response.send_message(file=file, embed=embed)

@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.add_cog(PlexBot(bot))
bot.run(discordtoken)
