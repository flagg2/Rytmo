import discord
from discord.ext import commands
import music

cogs = [music]


client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

client.run("ODg4OTAxMDkwNTQ2OTQ2MDQ5.YUZbpg.BnV1ioPqHSyxuBtuVb7nO8xciZw")
