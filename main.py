import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import discord
import requests
import json

client = discord.Client()


cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': 'suhbot-ff7d8',
})

db = firestore.client()


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
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$inspire'):
        await message.channel.send(get_quote())

    if message.content.startswith("$joke"):
        await message.channel.send(get_joke())



client.run('Nzc1NTQ1MTMyMDY5NTUyMTI4.X6n4sA.1zCKZ4Qka8wBzypwWnv7GosIO5U')
