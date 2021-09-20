import discord
import random
import asyncio
import time
from discord.ext import commands
from discord_components.component import ActionRow
import youtube_dl
from discord_components import DiscordComponents, ComponentsBot, Button, ActionRow
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
# importing the os module


def format_song(song):
    title = song['title']
    if len(title) > 50:
        title = f'{title[:47]}...'
    return f"[{title}]({song['webpage_url']} '{song['title']}') | `{format_duration(song['duration'])}` \n"


def format_duration(duration):
    seconds = duration % 60
    if seconds < 10:
        seconds = f"0{seconds}"
    return f'{duration//60}:{seconds}'


class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []
        self.paused = False
        self.playing = False
        self.current_song_ends_at = 0
        self.current_song = None

    def remaining_queue_time(self, play_top):
        if (len(self.queue) == 0 and self.playing == False):
            return 'Now'
        remaining_time = int(self.current_song_ends_at) - int(time.time())
        if remaining_time < 0:
            remaining_time = 0
        if not play_top:
            for song in self.queue:
                remaining_time += song['duration']
        return format_duration(remaining_time)

    async def process_queue(self, ctx):
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        vc = ctx.voice_client
        if vc is not None:
            self.playing = vc.is_playing()
        else:
            self.playing = False
        if (vc is None):
            return
        if (not vc.is_playing()) and not self.paused and len(self.queue) != 0:
            self.current_song = self.queue[0]
            self.current_song_ends_at = int(
                time.time()) + self.queue[0]['duration']
            if (os.getenv('IS_CLOUD') == "False"):
                vc.play(discord.FFmpegOpusAudio(
                    executable=os.getenv('FFMPEG_EXECUTABLE_PATH'), source=self.queue.pop(0)["url"], **FFMPEG_OPTIONS))
            else:
                source = await discord.FFmpegOpusAudio.from_probe(self.queue.pop(0)["url"], **FFMPEG_OPTIONS)
                vc.play(source)
        await asyncio.sleep(1)
        loop = asyncio.get_event_loop()
        loop.create_task(self.process_queue(ctx))

    @commands.command()
    async def join(self, ctx):
        self.queue = []
        self.current_song_ends_at = 0
        self.paused = False
        self.playing = False
        if ctx.author.voice is None:
            await ctx.send("Nejsi v channeli")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
            loop = asyncio.get_event_loop()
            print('somtu')
            loop.create_task(self.process_queue(ctx))
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command()
    async def rytmo(self, ctx):
        print(os.getenv('SPOTIFY_API_KEY'))
        res = requests.get(url='https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO0GYzBD?fields=tracks(items(track(name)))&limit=100',
                           headers={'Content-Type': 'application/json', "Accept": "application/json", "Authorization": f"Bearer {os.getenv('SPOTIFY_API_KEY')}"})
        response = json.loads(res.text)
        random_song = random.choice(response['tracks']['items'])
        await self.play(ctx, random_song['track']['name'])

    @commands.command()
    async def remove(self, ctx, index):
        index = int(index)
        if (index > len(self.queue) or index == 0):
            return await ctx.send("Please provide a valid song index")
        song_info = self.queue.pop(index-1)
        embedVar = discord.Embed(
            title=song_info["title"], description="removed from queue", url=song_info["webpage_url"], color=0x00ff00)
        await ctx.channel.send(embed=embedVar)

    @commands.command()
    async def skip(self, ctx):
        ctx.voice_client.stop()

    @commands.command()
    async def disconnect(self, ctx):
        self.queue = []
        await ctx.voice_client.disconnect()

    async def play_song(self, ctx, name, play_top):
        if (len(name) < 3):
            return await ctx.channel.send("Name of the song has to be at least 3 characters long")
        # join if not in channel
        if ctx.voice_client is None:
            await self.join(ctx)
        remaining_time = self.remaining_queue_time(play_top)
        YDL_OPTIONS = {'format': 'bestaudio'}
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(
                f"ytsearch:{name}", download=False)
            entry = info['entries'][0]
            song_info = {
                "query": name,
                "title": entry['title'],
                "url": entry['url'],
                "webpage_url": entry['webpage_url'],
                "duration": entry['duration'],
                "author": ctx.message.author
            }
            embedVar = discord.Embed(
                title=song_info["title"], description="added to queue", url=song_info["webpage_url"], color=0x00ff00)
            embedVar.add_field(
                name="Duration", value=format_duration(song_info["duration"]), inline=True)
            embedVar.add_field(name="Time until playing",
                               value=remaining_time, inline=True)
            if (play_top):
                self.queue.insert(0, song_info)
            else:
                self.queue.append(song_info)
            await ctx.channel.send(embed=embedVar)

    @commands.command()
    async def playtop(self, ctx, *params):
        await self.play_song(ctx, ' '.join(params), True)

    @commands.command()
    async def play(self, ctx, *params):
        await self.play_song(ctx, ' '.join(params), False)

    @commands.command()
    async def pause(self, ctx):
        self.paused = True
        await ctx.voice_client.pause()

    @commands.command()
    async def resume(self, ctx):
        await ctx.voice_client.resume()
        self.paused = False

    @commands.command()
    async def q(self, ctx):
        if self.current_song is None:
            await ctx.channel.send('The queue is empty')
        current_song_string = format_song(self.current_song)
        embedVar = discord.Embed(
            title=f"Queue for {ctx.message.guild.name}", color=0x00ff00)
        embedVar.add_field(
            name="Now playing:", value=current_song_string, inline=False)
        page = 0
        if (len(self.queue) > 0):
            pages = []
            for index, song in enumerate(self.queue):
                if index % 5 == 0:
                    pages.append('')
                pages[index//5] += f'`{index+1}.` '
                pages[index//5] += format_song(song)
            embedVar.add_field(
                name="Up next:", value=pages[page], inline=False)
        embedVar.add_field(
            name="Songs in queue:", value=len(self.queue), inline=True)
        embedVar.add_field(
            name="Playtime duration:", value=self.remaining_queue_time(False), inline=True)
        message = await ctx.channel.send(embed=embedVar)
        # await message.add_reaction('⏮')
        # await message.add_reaction('◀')
        # await message.add_reaction('▶')
        # await message.add_reaction('⏭')
        # i = 0
        # emoji = ''

        # while True:
        #     if emoji == '⏮':
        #         i = 0
        #         await self.client.edit_message(message, embed=pages[i])
        #     elif emoji == '◀':
        #         if i > 0:
        #             i -= 1
        #             await self.client.edit_message(message, embed=pages[i])
        #     elif emoji == '▶':
        #         if i < 2:
        #             i += 1
        #             await self.client.edit_message(message, embed=pages[i])
        #     elif emoji == '⏭':
        #         i = 2
        #         await self.client.edit_message(message, embed=pages[i])

        #     res = await message.wait_for_reaction(message=message, timeout=30.0)
        #     if res == None:
        #         break
        #     if str(res[1]) != '<Bots name goes here>':  # Example: 'MyBot#1111'
        #         emoji = str(res[0].emoji)
        #         await client.remove_reaction(message, res[0].emoji, res[1])

        # await client.clear_reactions(message)


def setup(client):
    client.add_cog(music(client))
