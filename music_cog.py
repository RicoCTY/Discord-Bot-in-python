import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import youtube_dl



youtube_dl.utils.bug_reports_message = lambda: ''


#Music setting
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s', 
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

def is_connected(ctx):
    voice_client = ctx.message.guild.voice_client
    return voice_client and voice_client.is_connected()



queue = []
loop = False


class Music_cog(commands.Cog):

    def __init__(self,client):
        self.client = client

    @commands.command(name='join', help='This command makes the bot join the voice channel')
    async def join(self,ctx):
        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel")
            return
        
        else:
            channel = ctx.message.author.voice.channel

        await channel.connect()
        
    @commands.command(name='leave', help='This command stops the music and makes the bot leave the voice channel')
    async def leave(self,ctx):
        voice_client = ctx.message.guild.voice_client
        await voice_client.disconnect()

    @commands.command(name='loop', help='This command toggles loop mode')
    async def loop_(self,ctx):
        global loop

        if loop:
            await ctx.send('Loop mode is now `False!`')
            loop = False
        
        else: 
            await ctx.send('Loop mode is now `True!`')
            loop = True

    @commands.command(name='play', help='This command plays music')
    async def play(self,ctx):
        global queue

        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel")
            return
        
        else:
            channel = ctx.message.author.voice.channel

        try: await channel.connect()
        except: pass

        server = ctx.message.guild
        voice_channel = server.voice_client
        
        try:
            async with ctx.typing():
                player = await YTDLSource.from_url(queue[0], loop=client.loop)
                voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                
                if loop:
                    queue.append(queue[0])

                del(queue[0])
                
            await ctx.send('**Now playing:** {}'.format(player.title))

        except:
            await ctx.send('Nothing in your queue! Use `s/queue` to add a song!')



    @commands.command(name='stop', help='This command stops the song!')
    async def stop(self,ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.stop()

    @commands.command(name='queue')
    async def queue_(self,ctx, url):
        global queue

        queue.append(url)
        await ctx.send(f'`{url}` added to queue!')

    @commands.command(name='remove')
    async def remove(self,ctx, number):
        global queue

        try:
            del(queue[int(number)])
            await ctx.send(f'Your queue is now `{queue}!`')
        
        except:
            await ctx.send('Your queue is either **empty** or the index is **out of range**')

    @commands.command(name='view', help='This command shows the queue')
    async def view(self,ctx):
        await ctx.send(f'Your queue is now `{queue}!`')


    @commands.command(name='pause', help='This command pauses the song')
    async def pause(self,ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.pause()


    @commands.command(name='resume', help='This command resumes the song!')
    async def resume(self,ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.resume()

    @commands.command()
    async def playfile(self,ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {query}')

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")



def setup(client):
    client.add_cog(Music_cog(client))
