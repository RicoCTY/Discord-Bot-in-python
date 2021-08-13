import discord
from discord.ext import commands, tasks
import datetime
import json

from random import choice
import random

client = commands.Bot(command_prefix='s/',description="置頂留言")

status = ['Nothing To Do.', 'Eating ù w ú', 'Sleeping Zzz']


@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')

@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))
    
client.run('TOKEN')
