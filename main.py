import music
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from http import server


def run_bot():
    cogs = [music]

    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    for i in range(len(cogs)):
        cogs[i].setup(client)

    client.run(os.getenv('DISCORD_BOT_TOKEN'))


if __name__ == '__main__':
    load_dotenv()
    run_bot()
