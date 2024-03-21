import os
import discord
import random
from discord.ext import commands
from datetime import datetime, timedelta
import sqlite3

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
client = commands.Bot(command_prefix='!', intents=discord.Intents.all())
token = 'MTEzODEwNDg4MDI1OTY2NjA4MA.G8BoZj.6IcaNhnIAiXs5eYBc9nTLMjCxgfHlIa2YfiWaE'

pis_cooldown = {}
excluded_users = [1138101790450139196, 1138095987450200145, 1138089178815528991, 1138104880259666080, 1138132085798879383, 1116272877818355773, 988380732210679818, 193762296923815937, 1115955982649016480, 552560239304507403]  # Внесите нужные айди пользователей в список исключений
connection = sqlite3.connect("pis_stats.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stats (
        user_id INTEGER PRIMARY KEY,
        pis_count INTEGER
    )
""")

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global pis_cooldown
    if message.content.startswith('!писявочник'):
        if message.author.id in pis_cooldown and datetime.now() - pis_cooldown[message.author.id] < timedelta(minutes=120):
            await message.channel.send(f'{message.author.mention}, писявочника можно искать только раз в 120 минут.')
        else:
            pis_cooldown[message.author.id] = datetime.now()
            members = message.guild.members
            random_member = random.choice(members)
			
            # Проверяем, является ли выбранный пользователь исключением			
            while random_member.id in excluded_users:			
                random_member = random.choice(members)			
						
            await message.channel.send(f'{message.author.mention} Кручу-верчу, писявочника ищу...')
            await message.channel.send(f'Писявочник найден, это {random_member.mention}! Открывай рот :open_mouth:')

            cursor.execute("SELECT pis_count FROM stats WHERE user_id=?", (random_member.id,))
            row = cursor.fetchone()

            if row is None:
                cursor.execute("INSERT INTO stats (user_id, pis_count) VALUES (?, 1)", (random_member.id,))
            else:
                cursor.execute("UPDATE stats SET pis_count=pis_count+1 WHERE user_id=?", (random_member.id,))

            connection.commit()

    elif message.content.startswith('!статписявочник'):
        cursor.execute("SELECT user_id, pis_count FROM stats")
        stats = cursor.fetchall()

        if stats:
            stats_message = 'Стата по писявочникам:\n'
            for user_id, pis_count in stats:
                member = message.guild.get_member(user_id)
                if member:
                    stats_message += f'{member.mention}: {pis_count} раз(а)\n'
            await message.channel.send(stats_message)
        else:
            await message.channel.send('Стата по писявочникам пуста :upside_down:')

@client.command()
async def статписявочник(ctx):
    cursor.execute("SELECT user_id, pis_count FROM stats")
    stats = cursor.fetchall()

    if stats:
        stats_message = 'Стата по писявочникам:\n'
        for user_id, pis_count in stats:
            member = ctx.guild.get_member(user_id)
            if member:
                stats_message += f'{member.mention}: {pis_count} раз(а)\n'
        await ctx.send(stats_message)
    else:
        stats_message = 'Стата по писявочникам:\n'
client.run(token)