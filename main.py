from random import randint
import yfinance as yf
import firebase_admin
from discord.ext import commands
from firebase_admin import credentials
from firebase_admin import firestore
from Share import Share
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
    bot_guess = flips[randint(0, 1)]

    if amount <= 0:
        await ctx.send("```Number must be > 0```")
        return

    if guess in flips:
        win = False
        doc_ref = db.collection(u'users').document(f'{ctx.author}')
        doc = doc_ref.get()

        if not doc.exists:
            doc_ref.set({
                u'user': f'{ctx.author}',
                u'score': 0
            })
            doc = doc_ref.get()

        if doc.get("score") <= -100:
            doc_ref.set({
                u'score': -100
            }, merge=True)
            amount = 1
            bot_guess = guess
            doc = doc_ref.get()

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
            await ctx.send(f"```{'Your call' : <15}{guess: >15}\n"
                           f"{'The coin' : <15}{bot_guess: >15}\n\n"
                           f"{'Total score: ' : <15}{score: >15}```")

        else:
            score = score + f"(-{amount})"
            await ctx.send(f"```{'Your call' : <15}{guess: >15}\n"
                           f"{'The coin' : <15}{bot_guess: >15}\n\n"
                           f"{'Total score: ' : <15}{score: >15}```")
    else:
        await ctx.send("```Invalid coin call(format is gflip [heads/tails] [numerial amount])```")


@client.command(aliases=["score", "flipscore"])
async def gflipscore(ctx):
    doc_ref = db.collection(u'users').document(f'{ctx.author}')
    doc = doc_ref.get()
    if doc.exists:
        await ctx.send(f"```{'User' : <15}{'Score' : >15}\n{doc.get('user'): <15}{doc.get('score'): >15}```")
    else:
        await ctx.send("```You do not have a flip score :(```")


@client.command(aliases=['gfliplb', 'gflipscores'])
async def gflipleaderboard(ctx):
    docs = db.collection(u'users').stream()

    message = f"{'User' : <15}{'Score' : >15}\n"
    for doc in docs:
        user = f"{doc.get('user')}"
        score = f"{doc.get('score')}"
        message = message + f"{user: <15}{score: >15}\n"

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

            await ctx.send(f"```{'User' : <15}{'Score' : >15}\n"
                           f"{author: <15}{user_score: >15}\n"
                           f"{target: <15}{target_score: >15}\n\n"
                           f"{author} has given {amount} points to {target}```")

        elif user_doc.get("score") < amount:
            await ctx.send("```You do not have enough points```")
        else:
            await ctx.send("```Amount must be greater than 0```")
    else:
        await ctx.send("```Either you or the target person do not exist```")


# future note: make it so u must have >100 points in order to give away points
@client.command()
async def declarebankruptcy(ctx):
    doc_ref = db.collection(u'users').document(f"{ctx.author}")
    doc = doc_ref.get()

    if doc.exists and doc.get("score") <= -90:
        doc_ref.set({
            u'score': 0
        }, merge=True)
        await ctx.send("```Your balance has been reset to 0```")
    elif not doc.exists:
        await ctx.send("```You do exist in the database```")
    else:
        await ctx.send("```You score must be below -90 to declare bankruptcy```")


@client.command()
async def getprice(ctx, *tickers):
    message = f"```{'Stock' : <15}{'Price' : >15}\n"
    for ticker in tickers:
        ticker_yahoo = yf.Ticker(ticker)
        data = ticker_yahoo.history()
        last_quote = (data.tail(1)['Close'].iloc[0])
        message += f"{ticker: <15} {last_quote:>15.2f}\n"
    await ctx.send(message + "```")


@client.command()
async def buy(ctx, name, amount):
    try:
        name = name.upper()
        amount = int(amount)
        ticker = yf.Ticker(name)
    except:
        await ctx.send("```Error```")
    else:
        if amount <= 0:
            await ctx.send("```amount must be greater than 0```")
            return
        doc_ref = db.collection(u'users').document(f'{ctx.author}')
        score = doc_ref.get().get("score")

        data = ticker.history()
        price = (data.tail(1)['Close'].iloc[0])
        price = int(price * 100) / 100.0

        stock_doc_ref = doc_ref.collection(u'stocks').document(f'{name}')
        stock_doc = stock_doc_ref.get()
        if score >= amount * price:
            if not stock_doc.exists:
                stock_doc_ref.set({
                    u'ticker': f"{name}",
                    u'amount': amount,
                    u'price': price
                })
                doc_ref.set({
                    u'score': score - (amount * price)
                }, merge=True)
                await ctx.send(
                    f"```{amount} shares of {name} at ${price} have been bought (${amount * price} total)```")

            else:
                stock_doc_ref.set({
                    u'amount': stock_doc.get("amount") + amount,
                    u'price': (stock_doc.get("price") + price) / 2.0
                }, merge=True)
                doc_ref.set({
                    u'score': score - (amount * price)
                }, merge=True)
                await ctx.send(
                    f"```{amount} shares of {name} at ${price} have been bought (${amount * price} total)```")
        else:
            await ctx.send("```You do not have enough points```")


@client.command()
async def profile(ctx):
    stocks = db.collection(u'users').document(f"{ctx.author}").collection(u'stocks').stream()

    message = f"```{'Ticker' : <15}{'Amount' : ^15}{'Balance': ^15}" \
              f"{'% gain/loss': ^15}{'Purchase Price': ^15}{'Current Price': >15}\n"

    total_sum = 0
    amount_sum = 0
    purc_total_sum = 0
    count = 0
    for stock in stocks:
        amount_num = stock.get(u'amount')
        price_num = stock.get(u'price')
        ticker_name = f"{stock.get(u'ticker')}"
        amount = f"{amount_num}"
        price = f"{price_num}"

        ticker = yf.Ticker(ticker_name)
        data = ticker.history()
        current_price = (data.tail(1)['Close'].iloc[0])
        current_price = int(current_price * 100) / 100.0

        value = int(amount_num * current_price * 100) / 100.0
        percent = -int((price_num * amount_num - current_price * amount_num) * 10000) / 100.0

        message += f"{ticker_name: <15}{amount: ^15}{value: ^15}{percent: ^15}{price: ^15}{current_price: >15}\n"
        total_sum += value
        purc_total_sum += amount_num * price_num
        amount_sum += amount_num
        count += 1

    total_percent = -int(((purc_total_sum - total_sum) / purc_total_sum) * 10000) / 100
    message += f"\n" \
               f"{'Total': <15}{amount_sum: ^15}{(int(total_sum * 100) / 100.0): ^15}{total_percent: ^15}"
    await ctx.send(message + "```")


@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        doc_ref = db.collection(u'servers').document(f'{message.guild.id}')
        doc = doc_ref.get()
        await message.channel.send("The prefix for this server is:  " + doc.get('prefix'))
    await client.process_commands(message)


client.run('Nzc1NTQ1MTMyMDY5NTUyMTI4.X6n4sA.1zCKZ4Qka8wBzypwWnv7GosIO5U')
