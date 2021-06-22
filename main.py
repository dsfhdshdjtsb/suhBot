from random import randint

import firebase_admin
from discord.ext import commands
from firebase_admin import credentials
from firebase_admin import firestore

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
async def gflip(ctx, call="", amount=1):
    if call == "":
        await ctx.send("```Coin call required (ex: gflip heads)```")

    flips = ["heads", "tails"]
    guess = f"{call.lower()}"
    amount = int(amount)

    if guess in flips:
        win = False
        doc_ref = db.collection(u'users').document(f'{ctx.author}')
        doc = doc_ref.get()

        if doc.get("score") == -100:
            doc_ref.set({
                u'score': -99
            }, merge=True)
            amount = 0
            doc = doc_ref.get()

        if not doc.exists:
            doc_ref.set({
                u'user': f'{ctx.author}',
                u'score': 0
            })
            doc = doc_ref.get()

        bot_guess = flips[randint(0, 1)]

        if guess == bot_guess and doc.get("score") - amount >= -100:
            win = True
            doc_ref.set({
                u'user': f'{ctx.author}',
                u'score': doc.get("score") + amount
            })
        elif doc.get("score") - amount >= -100:
            doc_ref.set({
                u'user': f'{ctx.author}',
                u'score': doc.get("score") - amount
            })
        else:
            await ctx.send("```You do not have enough points```")
            return


        doc = doc_ref.get()

        score = f"{doc.get('score')}"
        if win:
            score = score + f"(+{amount})"
            await ctx.send(f"```{'Your call' : <20}{guess: >20}\n"
                           f"{'The coin' : <20}{bot_guess: >20}\n\n"
                           f"{'Total score: ' : <20}{score: >20}```")

        else:
            score = score + f"(-{amount})"
            await ctx.send(f"```{'Your call' : <20}{guess: >20}\n"
                           f"{'The coin' : <20}{bot_guess: >20}\n\n"
                           f"{'Total score: ' : <20}{score: >20}```")


@client.command()
async def gflipscore(ctx):
    doc_ref = db.collection(u'users').document(f'{ctx.author}')
    doc = doc_ref.get()
    if doc.exists:
        await ctx.send(f"```{'User' : <20}{'Score' : >20}\n{doc.get('user'): <20}{doc.get('score'): >20}```")
    else:
        await ctx.send("```You do not have a flip score :(```")


@client.command(aliases=['gfliplb', 'gflipscores'])
async def gflipleaderboard(ctx):
    docs = db.collection(u'users').stream()

    message = f"{'User' : <20}{'Score' : >20}\n"
    for doc in docs:
        user = f"{doc.get('user')}"
        score = f"{doc.get('score')}"
        message = message + f"{user: <20}{score: >20}\n"

    await ctx.send("```" + message + "```")


@client.command()
async def give(ctx, target, amount):
    author = f"{ctx.author}"  # took 10 hours to figure out
    target = f"{target}"
    amount = int(amount)

    user_doc_ref = db.collection(u'users').document(f'{author}')
    user_doc = user_doc_ref.get()

    target_doc_ref = db.collection(u'users').document(f'{target}')
    target_doc = target_doc_ref.get()

    if user_doc.exists and target_doc.exists:
        if user_doc.get("score") >= amount > 0:
            user_doc_ref.set({
                u'score': user_doc.get("score") - amount
            }, merge=True)
            target_doc_ref.set({
                u'score': target_doc.get("score") + amount
            }, merge=True)
            user_doc = user_doc_ref.get()  # update docs
            target_doc = target_doc_ref.get()

            user_score = f"{user_doc.get('score')}(-{amount})"
            target_score = f"{target_doc.get('score')}(+{amount})"

            await ctx.send(f"```{'User' : <20}{'Score' : >20}\n"
                           f"{author: <20}{user_score: >20}\n"
                           f"{target: <20}{target_score: >20}\n\n"
                           f"{author} has given {amount} points to {target}```")

        elif user_doc.get("score") < amount:
            await ctx.send("```You do not have enough points```")
        else:
            await ctx.send("```Amount must be greater than 0```")
    else:
        await ctx.send("```Either you or the target person do not exist```")


@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        doc_ref = db.collection(u'servers').document(f'{message.guild.id}')
        doc = doc_ref.get()
        await message.channel.send("The prefix for this server is:  " + doc.get('prefix'))
    await client.process_commands(message)


client.run('Nzc1NTQ1MTMyMDY5NTUyMTI4.X6n4sA.1zCKZ4Qka8wBzypwWnv7GosIO5U')
