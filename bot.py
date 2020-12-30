import discord
import os
import requests
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get('DISCORD_TOKEN')
WEATHER = os.environ.get('WEATHERAPI-KEY')
PREFIX = "!v"
userlist = "Discord-ValBot\subscribed.txt"

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
    if message.author == client.user or not message.content.startswith(PREFIX):
        return

    if message.content.startswith(PREFIX + " sub"):
        await sub(message)
    elif message.content.startswith(PREFIX + " unsub"):
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
    elif message.content.startswith(PREFIX + " currentsubs"):
        users = open(userlist, "r")
        string = "Current Subscribers to ValBot are:\n"
        for line in users:
            string += line

        users.close()
        await message.channel.send(string)

    elif message.content.startswith(PREFIX + " alert"):
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
                await member.send("Hello " + member.name + "! Currently " + message.author.name +
                                  " is playing Valorant on" " the server " + message.guild.name)

        await message.channel.send("Pinged " + str(numping) + " friends: "+ pinged)
    elif message.content.startswith(PREFIX + " help"):
        await message.channel.send("Current commands include: \n" +
                                   PREFIX + " sub - Subscribes you to valbot alerts \n" +
                                   PREFIX + " unsub - Unsubscribes you to alerts \n" +
                                   PREFIX + " currentsubs - Shows all members subscribed in the guild \n" +
                                   PREFIX + " weather <Name of City> "
                                   "<Name of Region> - Shows current weather at that location \n" +
                                   PREFIX + " alert <optional list of names> - Dms all members subscribed"
                                   " or only the ones that have been listed")
    elif message.content.startswith(PREFIX + " weather"):
        req = message.content.split(" ", 2)
        if len(req) < 3:
            await message.channel.send("Please include the City, for example: type !valbot Toronto Ontario")
        else:
            reqs = message.content.split(" ", 2)[2]
            response = requests.get("http://api.weatherapi.com/v1/current.json?key=" + WEATHER + "&q=" +
                                reqs)
            if (response.status_code) != 200:
                print(response.status_code)
                await message.channel.send("The city was not able to be found? Please refine your search")
            else:
                print(reqs)
                weatherjson = response.json()
                weather = weatherjson['current']
                icon = discord.File(BytesIO(requests.get("https:" + weather['condition']['icon']).content))
                embedicon = discord.Embed(title="Weather in " + weatherjson['location']['name'] +
                                           ", " + weatherjson['location']['region'] + ", " +
                                           weatherjson['location']['country'] + ":",
                                          description= "Temperature of " + str(weather['temp_c']) + "C, feels like " +
                                           str(weather['feelslike_c']) + "C with " + weather['condition']['text'])
                embedicon.set_image(url="https:" + weather['condition']['icon'])
                await message.channel.send("Report generated as of: " + weather['last_updated'] + " (UST)", tts = False,
                                           embed=embedicon)



    else:
        await message.channel.send("Unknown command, " + message.content + "\n Type " + PREFIX + " help"
                                                                           " for list of commands")



async def sub(message):
    if (checkinfile(str(message.author))):
        users = open(userlist, "a")
        users.write(str(message.author) + "\n")
        users.close()
        await message.channel.send("You've been subscribed to ValBot Alerts,"
                                   + " type " + PREFIX + " unsub to unsubscribe")
    else:
        await message.channel.send("You're already subscribed to ValBot Alerts!")


def checkinfile(subber):
    print(os.listdir())
    users = open(userlist, "r")
    for line in users:

        if str.strip(line) == subber:
            users.close()
            return False

    users.close()
    return True



client.run(TOKEN)