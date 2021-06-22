from random import randint

import firebase_admin
from discord.ext import commands
from firebase_admin import credentials
from firebase_admin import firestore

import discord
from discord.ext.commands import bot
import requests
import json

cred = credentials.Certificate('suhbot-ff7d8-f8cf0aaaa3d5.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


def get_prefix(client, message):
    doc_ref = db.collection(u'servers').document(f'{message.guild.id}')
    doc = doc_ref.get()
    return doc.get('prefix')


client = commands.Bot(command_prefix=get_prefix)


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote


def get_joke():
    response = requests.get('https://official-joke-api.appspot.com/random_joke')
    json_data = json.loads(response.text)
    joke = json_data["setup"] + " " + json_data["punchline"]
    return joke


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_guild_join(guild):
    print(guild.id)
    doc_ref = db.collection(u'servers').document(f'{guild.id}')
    doc_ref.set({
        u'prefix': '.'
    })


@client.command()
@commands.has_permissions(administrator=True)
async def changeprefix(ctx, prefix):
    doc_ref = db.collection(u'servers').document(f'{ctx.guild.id}')
    doc_ref.set({
        u'prefix': prefix
    })
    doc = doc_ref.get()
    await ctx.send("The prefix has been changed to: " + doc.get('prefix'))


@client.command()
async def ping(ctx):
    await ctx.send(f'Ping is {round(client.latency * 1000, 1)} ms')


@client.command()
async def joke(ctx):
    await ctx.send(get_joke())


@client.command()
async def quote(ctx):
    await ctx.send(get_quote())


@client.command()
async def flip(ctx):
    flips = ["heads", "tails"]
    await ctx.send(flips[randint(0, 1)])


@client.command()
async def ball(ctx):
    responses = [
        "It is Certain",
        "It is decidedly so",
        "Without a doubt",
        "Yes definitely",
        "You may rely on it",
        "As I see it, yes",
        "Most likely",
        "Outlook good",
        "Yes",
        "Signs point to yes",
        "Reply hazy, try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
        "Don't count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful"
    ]
    await ctx.send(responses[randint(0, 19)])


@client.command()
async def gflip(ctx, arg1):
    flips = ["heads", "tails"]
    guess = arg1.lower()

    if guess in flips:
        win = False
        doc_ref = db.collection(u'users').document(f'{ctx.author}')
        doc = doc_ref.get()

        bot_guess = flips[randint(0, 1)]

        if guess == bot_guess:
            win = True
            if doc.exists:
                doc_ref.set({
                    u'user': f'{ctx.author}',
                    u'score': doc.get("score") + 1
                })
            else:
                doc_ref.set({
                    u'user': f'{ctx.author}',
                    u'score': 1
                })
        else:
            if not doc.exists:
                doc_ref.set({
                    u'user': f'{ctx.author}',
                    u'score': 0
                })
        doc = doc_ref.get()

        if win:
            await ctx.send("Your call is: " + guess + "\n" +
                           "The coin is: " + bot_guess + "\n" +
                           "Your guess was correct!" + "\n" +
                           "Your overall score is: " + f'{doc.get("score")}')
        else:
            await ctx.send("Your call is: " + guess + "\n" +
                           "The coin is: " + bot_guess + "\n" +
                           "Your guess was not correct" + "\n" +
                           "Your overall score is: " + f'{doc.get("score")}')


@client.command()
async def flipscore(ctx):
    doc_ref = db.collection(u'users').document(f'{ctx.author}')
    doc = doc_ref.get()
    if doc.exists:
        await ctx.send("Your flip score is: " + f'{doc.get("score")}')
    else:
        await ctx.send("You do not have a flip score :(")


@client.command()
async def flipleaderboard(ctx):
    docs = db.collection(u'users').stream()

    for doc in docs:
        await ctx.send(f'{doc.get("user")}       : {doc.get("score")}')


@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        doc_ref = db.collection(u'servers').document(f'{message.guild.id}')
        doc = doc_ref.get()
        await message.channel.send("The prefix for this server is:  " + doc.get('prefix'))
    await client.process_commands(message)


client.run('Nzc1NTQ1MTMyMDY5NTUyMTI4.X6n4sA.1zCKZ4Qka8wBzypwWnv7GosIO5U')
