import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
userlist = "subscribed.txt"

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    for guild in client.guilds:
        print("Connected to " + guild.name)
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user or not message.content.startswith('!valbot'):
        return

    if message.content.startswith('!valbot sub'):
        await sub(message)
    elif message.content.startswith('!valbot unsub'):
        if (not checkinfile(str(message.author))):
            users = open(userlist, "r")
            hold = []
            for line in users:
                if str.strip(line) != str(message.author):
                    hold.append(line)

            users.close()
            users = open(userlist, "w")
            for user in hold:
                users.write(user)

            users.close()
            await message.channel.send("You've unsubscribed to ValBot Alerts!")
        else:
            await message.channel.send("You aren't subscribed to ValBot Alerts")
    elif message.content.startswith('!valbot currentsubs'):
        users = open(userlist, "r")
        string = "Current Subscribers to ValBot are:\n"
        for line in users:
            string += line

        users.close()
        await message.channel.send(string)

    elif message.content.startswith('!valbot alert'):
        specified = message.content.split(" ")

        users = open(userlist, "r")
        hold = []
        numping = 0
        pinged = ""

        print(specified)
        if len(specified) > 2:
            for user in users:
                username = str.strip(user)
                if username in specified or username[:len(username) - 5] in specified:
                    hold.append(username)
            users.close()
        else:
            for user in users:
                username = str.strip(user)
                hold.append(username)

            users.close()

        for member in message.guild.members:
            if member.name+"#"+member.discriminator in hold and member != message.author:
                pinged += member.name + " "
                numping += 1
                await member.send("Hello " + member.name + "! Currently " + message.author.name + " is playing Valorant on "
                                  " the server " + message.guild.name)

        await message.channel.send("Pinged " + str(numping) + " friends: "+ pinged)
    elif message.content.startswith('!valbot help'):
        await message.channel.send("Current commands include: \n"
                                   "!valbot sub - Subscribes you to valbot alerts \n"""
                                   "!valbot unsub - Unsubscribes you to alerts \n"
                                   "!valbot currentsubs - Shows all members subscribed in the guild \n"
                                   "!valbot alert <optional list of names> - Dms all members subscribed"
                                   " or only the ones that have been listed")
    else:
        await message.channel.send("Unknown command, " + message.content + "\n Type !valbot help"
                                                                           " for list of commands")



async def sub(message):
    if (checkinfile(str(message.author))):
        users = open(userlist, "a")
        users.write(str(message.author) + "\n")
        users.close()
        await message.channel.send("You've been subscribed to ValBot Alerts,"
                                   + " type !valbot unsub to unsubscribe")
    else:
        await message.channel.send("You're already subscribed to ValBot Alerts!")


def checkinfile(subber):
    users = open(userlist, "r")
    for line in users:

        if str.strip(line) == subber:
            users.close()
            return False

    users.close()
    return True



client.run(TOKEN)