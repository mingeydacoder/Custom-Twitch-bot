from twitchio.ext import commands
from dataclasses import dataclass
import json
import requests
import random
import time


def make_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return response.json()  # Return the JSON response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Print HTTP error
    except Exception as err:
        print(f"Other error occurred: {err}")  # Print any other error

def rank():
    apikey = 'RIOT_API_KEY'
    url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/TARGET_SUMMONER_ID?api_key={apikey}"  # Replace with your request URL
    result = make_request(url)

    if result:
        print("Request was successful.")
        print("Response:")
        #print(result)
        return(result[0]['tier'],result[0]['leaguePoints'],result[0]['wins'],result[0]['losses'])
    else:
        print("Failed to retrieve data.")

@dataclass
class MessageData:
    author: str
    content: str
    channel: str
    is_mod: bool

class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token='TOKEN', prefix='!', initial_channels=['TARGET_CHANNEL'])
        self.author_names = []
        self.last_announcement_time = 0
        self.cooldown_period = 90  # Cooldown period in seconds

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Make a chat announcement whenever chats misbehave
        
        def chat_announcement(self):
            current_time = time.time()
            if current_time - self.last_announcement_time < self.cooldown_period:
                return

            url = 'https://api.twitch.tv/helix/chat/announcements'
            params = {
                'broadcaster_id': '...',
                'moderator_id': '...'
            }
            headers = {
                'Authorization': 'Bearer TOKEN',
                'Client-Id': '...',
                'Content-Type': 'application/json'
            }
            data = {
                'message': 'imGlitch This channel of strongly condemns any form of malicious and inappropriate speech. Statements made in the chat and through donations DO NOT represent the views of the channel owner.⚠️ ⚠️ ',
                'color': 'purple'
            }

            response = requests.post(url, headers=headers, params=params, json=data)

            if response.status_code == 204:
                print('Announcement sent successfully!')
                self.last_announcement_time = time.time()
                return(response)
            else:
                print(f'Failed to send announcement: {response.status_code}')
                print(response.json())

        if message.content == "TARGET_HATRED_WORD":
            chat_announcement(self)

        # Make a chat announcement whenever somebody ask about the name of game being played 
        
        def chat_announcement2(self):
            current_time = time.time()
            if current_time - self.last_announcement_time < self.cooldown_period:
                return

            def get_channel_info():
                url = f'https://api.twitch.tv/helix/channels?broadcaster_id=...'
                headers = {
                    'Authorization': 'Bearer TOKEN',
                    'Client-Id': '...'
                }

                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    title = [item['title'] for item in data['data']]
                    game = [item['game_name'] for item in data['data']]
                    return(title, game)
                else:
                    print(f'Failed to retrieve channel info: {response.status_code}')
                    return None
            channel_info = get_channel_info()
            if channel_info:
                for title, game in zip(channel_info[0], channel_info[1]):
                    title = title
                    game = game

            url = 'https://api.twitch.tv/helix/chat/announcements'
            params = {
                'broadcaster_id': '...',
                'moderator_id': '...'
            }
            headers = {
                'Authorization': 'Bearer TOKEN',
                'Client-Id': '...',
                'Content-Type': 'application/json'
            }
            data = {
                'message': f'imGlitch 🎬Steam Title: {title} || 🎮Now Playing: {game}',
                'color': 'green'
            }

            response = requests.post(url, headers=headers, params=params, json=data)

            if response.status_code == 204:
                print('Announcement sent successfully!')
                self.last_announcement_time = time.time()
                return(response)
            else:
                print(f'Failed to send announcement: {response.status_code}')
                print(response.json())

        def contains_keyword(string, keyword):
            return any(keyword in string for keyword in keywords)

        keywords = ["game?","what is this game","name of this game","title","are you playing"]
        if contains_keyword(message.content, keywords):
            chat_announcement2(self)
        
        print(message.author.name,':',message.content)

        self.author_names.append(message.author.name)

        # Auto-timeout with reasons given

        def timeout(id):
            broadcaster_id = "..."
            moderator_id = ".."
            user_id = id
            duration = 600
            reason = "Potential spamming (excuted by bot)"

            headers = {
                "Client-Id": '...',
                "Authorization": "Bearer TOKEN",
                "Content-Type": "application/json"
            }

            url = f"https://api.twitch.tv/helix/moderation/bans?broadcaster_id={broadcaster_id}&moderator_id={moderator_id}"

            json_data = {
            'data': {
                'user_id': user_id,
                'duration': duration,
                'reason': reason
                }
            }
            json_payload = json.dumps(json_data)
            response = requests.post(url, headers=headers, data=json_payload)

        # Channel status checker

        def check_if_live(username):
            try:
                response = requests.get(f"https://twitch.tv/{username}")
                response.raise_for_status()
                source_code = response.text

                if "isLiveBroadcast" in source_code:
                    return 1
                else:
                    return 0
            except requests.exceptions.RequestException as error:
                print("Error occurred:", error)

        # Punishment Mechanism for Spamming

        if len(self.author_names) >= 6 and self.author_names[-1] == self.author_names[-2] == self.author_names[-3] and check_if_live("XXX") == 1:
            if message.author.name == 'Nightbot' or message.author.name == 'XXX':
                pass
            elif self.author_names[-1] == self.author_names[-2] == self.author_names[-3] == self.author_names[-4]:
                pass
            elif self.author_names[-1] == self.author_names[-2] == self.author_names[-3] == self.author_names[-4] == self.author_names[-5]:
                pass
            elif self.author_names[-1] == self.author_names[-2] == self.author_names[-3] == self.author_names[-4] == self.author_names[-5] == self.author_names[-6]:
                pass
            elif message.author.is_mod == 1:
                pass
            elif message.author.is_vip == 1:
                pass
            elif message.author.is_mod == 0:
                await bot.connected_channels[0].send(f'@{message.author.name} Stop spamming the chat!')
                timeout(message.author.id)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)
        return message.author.name

    # Custom Channel Commands 

    @commands.command(name='commands')
    async def cmd(self, ctx: commands.Context):
        await ctx.send('!600 \n !please \n !rank or !r \n !dice \n !songlist \n')

    @commands.command(name='600')
    async def vanish(self, ctx):
        broadcaster_id = "..."
        moderator_id = "."
        user_id = ctx.author.id
        duration = 600
        reason = "They wanna timeout themselves"

        headers = {
            "Client-Id": '...',
            "Authorization": "Bearer TOKEN",
            "Content-Type": "application/json"
        }

        url = f"https://api.twitch.tv/helix/moderation/bans?broadcaster_id={broadcaster_id}&moderator_id={moderator_id}"

        json_data = {
        'data': {
            'user_id': user_id,
            'duration': duration,
            'reason': reason
            }
        }
        json_payload = json.dumps(json_data)
        response = requests.post(url, headers=headers, data=json_payload)


        respond_list = ['0.0', 'See u in 600 seconds!']

        if response.status_code == 200:
            await ctx.send(f" @{ctx.author.name} {random.choice(respond_list)}")
        else:
            print(response.text)
            await ctx.send(f" @{ctx.author.name} Can't do nothing to you Mods")


    @commands.command(name='6OO')
    async def vanish2(self, ctx):
        broadcaster_id = "..."
        moderator_id = "."
        user_id = ctx.author.id
        duration = 600
        reason = "They wanna timeout themselves"

        headers = {
            "Client-Id": '...',
            "Authorization": "Bearer TOKEN",
            "Content-Type": "application/json"
        }

        url = f"https://api.twitch.tv/helix/moderation/bans?broadcaster_id={broadcaster_id}&moderator_id={moderator_id}"

        json_data = {
        'data': {
            'user_id': user_id,
            'duration': duration,
            'reason': reason
            }
        }
        json_payload = json.dumps(json_data)
        response = requests.post(url, headers=headers, data=json_payload)


    @commands.command(name='600 ')
    async def vanish3(self, ctx):
        broadcaster_id = "..."
        moderator_id = "."
        user_id = ctx.author.id
        duration = 600
        reason = "They wanna timeout themselves"

        headers = {
            "Client-Id": '...',
            "Authorization": "Bearer TOKEN",
            "Content-Type": "application/json"
        }

        url = f"https://api.twitch.tv/helix/moderation/bans?broadcaster_id={broadcaster_id}&moderator_id={moderator_id}"

        json_data = {
        'data': {
            'user_id': user_id,
            'duration': duration,
            'reason': reason
            }
        }
        json_payload = json.dumps(json_data)
        response = requests.post(url, headers=headers, data=json_payload)


    @commands.command(name='6᱐᱐')
    async def vanish4(self, ctx):
        broadcaster_id = "..."
        moderator_id = "."
        user_id = ctx.author.id
        duration = 600
        reason = "They wanna timeout themselves"

        headers = {
            "Client-Id": '...',
            "Authorization": "Bearer TOKEN",
            "Content-Type": "application/json"
        }

        url = f"https://api.twitch.tv/helix/moderation/bans?broadcaster_id={broadcaster_id}&moderator_id={moderator_id}"

        json_data = {
        'data': {
            'user_id': user_id,
            'duration': duration,
            'reason': reason
            }
        }
        json_payload = json.dumps(json_data)
        response = requests.post(url, headers=headers, data=json_payload)

    @commands.command(name='rank')
    async def points(self, ctx: commands.Context):
        point = rank()
        winrate= "{:.1f}".format(float((point[2]/(point[2]+point[3]))*100))
        output = str(f'Hi! @{ctx.author.name} Current Scores :\nxxxxx#123:{point[0]} {point[1]}分, Winrate:{winrate}%')
        await ctx.send(output)

    @commands.command(name='r')
    async def rpoints(self, ctx: commands.Context):
        point = rank()
        winrate= "{:.1f}".format(float((point[2]/(point[2]+point[3]))*100))
        output = str(f'Hi! @{ctx.author.name} Current Scores :\nxxxxx#123:{point[0]} {point[1]}分, Winrate:{winrate}%')
        await ctx.send(output)

    @commands.command(name='rk')
    async def rrpoints(self, ctx: commands.Context):
        point = rank()
        winrate= "{:.1f}".format(float((point[2]/(point[2]+point[3]))*100))
        output = str(f'Hi! @{ctx.author.name} Current Scores :\nxxxxx#123:{point[0]} {point[1]}分, Winrate:{winrate}%')
        await ctx.send(output)

    @commands.command(name='R')
    async def Rpointss(self, ctx: commands.Context):
        point = rank()
        winrate= "{:.1f}".format(float((point[2]/(point[2]+point[3]))*100))
        output = str(f'Hi! @{ctx.author.name} Current Scores :\nxxxxx#123:{point[0]} {point[1]}分, Winrate:{winrate}%')
        await ctx.send(output)

    @commands.command(name='songlist')
    async def playlist(self, ctx: commands.Context):
        await ctx.send(f' @{ctx.author.name} https://www.youtube.com/playlist?list=PLi6wzs-FmmftsTQ6YW2jmES01JhLj07WA ')

    @commands.command(name='dice')
    async def dice(self, ctx: commands.Context):
        def weighted_roll(sides, weights):
            """
            Rolls a weighted die and returns one of the sides based on the specified weights.

            :param sides: A list of the sides of the die.
            :param weights: A list of weights corresponding to the probability of each side.
            :return: A side of the die.
            """
            if len(sides) != len(weights):
                raise ValueError("Sides and weights must be of the same length.")

            total_weight = sum(weights)
            rnd = random.uniform(0, total_weight)
            upto = 0
            for side, weight in zip(sides, weights):
                if upto + weight >= rnd:
                    return side
                upto += weight

        sides = [1, 2, 3, 4, 5, 6]
        weights = [1, 1, 1, 1, 1, 1]
        results = weighted_roll(sides, weights)
        output = results
        if ctx.author.is_mod == 1:
            await ctx.send(f'🎲 The result is：{output}！')
        elif ctx.author.is_mod == 0:
            await ctx.send(f'@{ctx.author.name} Need a Mod to execute this command')

bot = Bot()
bot.run()
