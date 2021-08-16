import discord
from discord.ext import commands
from discord_components import *
import datetime 
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType

client= commands.Bot(command_prefix='?')

@client.event
async def on_ready():
    print('Bot is online')
    DiscordComponents(client)

buttons = [
    [
        Button(style=ButtonStyle.gray, label='1'), 
        Button(style=ButtonStyle.gray, label='2'),
        Button(style=ButtonStyle.gray, label='3'),
        Button(style=ButtonStyle.blue, label='×'),
        Button(style=ButtonStyle.red, label='Exit')
    ],
    [
        Button(style=ButtonStyle.gray, label='4'),
        Button(style=ButtonStyle.gray, label='5'),
        Button(style=ButtonStyle.gray, label='6'),
        Button(style=ButtonStyle.blue, label='÷'),
        Button(style=ButtonStyle.red, label='←')
    ],
    [
        Button(style=ButtonStyle.gray, label='7'), 
        Button(style=ButtonStyle.gray, label='8'),
        Button(style=ButtonStyle.gray, label='9'),
        Button(style=ButtonStyle.blue, label='+'),
        Button(style=ButtonStyle.red, label='Clear')
    ],
    [
        Button(style=ButtonStyle.gray, label='00'),
        Button(style=ButtonStyle.gray, label='0'),
        Button(style=ButtonStyle.gray, label='.'),
        Button(style=ButtonStyle.blue, label='-'),
        Button(style=ButtonStyle.green, label='=')
    ]
]

def calculator(exp):
    o = exp.replace('×','*')
    o= o.replace('÷','/')
    result = ''
    try:
        result=str(eval(o))
    except:
        result="An Error Occoured"
    return result

@client.command()
async def calc(ctx):
    m = await ctx.send(content='Loading Calculator')
    expression='None'
    delta = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    e = discord.Embed(title=f'{ctx.author.name}\'s | {ctx.author.id}',description=expression,timestamp=delta)
    await m.edit(components = buttons, embed = e)
    while m.created_at < delta:
        res = await client.wait_for('button_click')
        if res.author.id == int(res.message.embeds[0].title.split('|')[1]) and res.message.embeds[0].timestamp < delta:
            expression = res.message.embeds[0].description
            if expression == 'None' or expression == 'An Error Occoured':
                expression = ''
        if res.component.label == 'Exit':
            await res.respond(content='Calculator Closed',type=7)
            break
        elif res.component.label == '←':
            expression = expression[:-1]
        elif res.component.label == 'Clear':
            expression=None
        elif res.component.label == '=':
            expression = calculator(expression)
        else:
            expression += res.component.label
        f=discord.Embed(title=f'{res.author.name}\'s calculator|{res.author.id}', description=expression, timestamp=delta)
        await res.respond(content='',embed=f, components=buttons, type=7)



client.run('ODc1MTU3OTYwMjE5ODM2NDY2.YRRcXQ.Ie-z7cOCsUe95-hBICvOzNsSxOs')
