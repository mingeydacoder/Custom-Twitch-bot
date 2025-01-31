from twitchio.ext import commands
from dataclasses import dataclass
import json
import requests
import aiohttp
import asyncio
import random
import time
import sqlite3
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
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
    apikey = 'RGAPI-fa134c9f-770a-464c-94a7-b61e47b84d3e'
    url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/tr835MMdj1ZWBhegcGXjiCk4cU2c5GXGMRJXo3p3px9Rdso?api_key={apikey}"  # Replace with your request URL
    result = make_request(url)

    if result:
        print("Request was successful.")
        print("Response:")
        #print(result)
        return(result[0]['tier'],result[0]['rank'],result[0]['leaguePoints'],result[0]['wins'],result[0]['losses'])
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
        super().__init__(token='8qi84ffjuedzanri1vs74dhfu0rmd3', prefix='!', initial_channels=['guanweiboy'])
        self.author_names = []
        self.last_announcement_time = 0
        self.cooldown_period = 90  # Cooldown period in seconds


        self.conn = sqlite3.connect('global_cooldown.db')
        self.cursor = self.conn.cursor()
        # 建立資料表，儲存命令的全局冷卻時間
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_cooldown (
                command_name TEXT,
                last_used REAL,
                PRIMARY KEY (command_name)
            )
        ''')
        self.conn.commit()


    def check_and_update_cooldown(self, command_name: str, cooldown: int):
        """
        檢查冷卻時間是否已過，並更新冷卻時間。
        :param command_name: 指令名稱
        :param cooldown: 冷卻時間（秒）
        :return: 剩餘冷卻時間（如果冷卻中）或 None
        """
        current_time = time.time()
        self.cursor.execute('SELECT last_used FROM global_cooldown WHERE command_name = ?', (command_name,))
        result = self.cursor.fetchone()

        if result:
            last_used = result[0]
            if current_time - last_used < cooldown:
                return cooldown - (current_time - last_used)

        # 更新冷卻時間
        self.cursor.execute('''
            INSERT INTO global_cooldown (command_name, last_used)
            VALUES (?, ?)
            ON CONFLICT(command_name) DO UPDATE SET last_used = excluded.last_used
        ''', (command_name, current_time))
        self.conn.commit()
        return None
    
    

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        #asyncio.create_task(self.check_periodically())

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        '''
        def chat_announcement(self):
            current_time = time.time()
            if current_time - self.last_announcement_time < self.cooldown_period:
                return

            url = 'https://api.twitch.tv/helix/chat/announcements'
            params = {
                'broadcaster_id': '150989534',
                'moderator_id': '653847938'
            }
            headers = {
                'Authorization': 'Bearer 8qi84ffjuedzanri1vs74dhfu0rmd3',
                'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5',
                'Content-Type': 'application/json'
            }
            data = {
                'message': 'imGlitch 本台嚴厲斥責任何形式之惡意言論，聊天室言論及抖內發言皆不代表本台主之立場。This channel of Guanweiboy strongly condemns any form of malicious and inappropriate speech. Statements made in the chat and through donations DO NOT represent the views of the channel owner.⚠️ ⚠️ ',
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

        if message.content == "嚴厲斥責":
            chat_announcement(self)
        '''
         
        def chat_announcement2(self):
            current_time = time.time()
            if current_time - self.last_announcement_time < self.cooldown_period:
                return

            def get_channel_info():
                url = f'https://api.twitch.tv/helix/channels?broadcaster_id=150989534'
                headers = {
                    'Authorization': 'Bearer 8qi84ffjuedzanri1vs74dhfu0rmd3',
                    'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'
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
                'broadcaster_id': '150989534',
                'moderator_id': '653847938'
            }
            headers = {
                'Authorization': 'Bearer 8qi84ffjuedzanri1vs74dhfu0rmd3',
                'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5',
                'Content-Type': 'application/json'
            }
            data = {
                'message': f'imGlitch 🎬實況標題: {title} || 🎮正在遊玩: {game}',
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

        keywords = ["遊戲叫什麼","遊戲叫甚麼","遊戲的名字","title"]
        if contains_keyword(message.content, keywords):
            chat_announcement2(self)

        print(message.author.name,':',message.content)

        self.author_names.append(message.author.name)

        def timeout(id):
            broadcaster_id = "150989534"
            moderator_id = "653847938"
            user_id = id
            duration = 600
            reason = "Potential spamming (excuted by lavendertree's bot)"

            headers = {
                "Client-Id": 'gp762nuuoqcoxypju8c569th9wz7q5',
                "Authorization": "Bearer 8qi84ffjuedzanri1vs74dhfu0rmd3",
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


        if len(self.author_names) >= 6 and self.author_names[-1] == self.author_names[-2] == self.author_names[-3] and check_if_live("guanweiboy") == 1:
            if message.author.name == 'Nightbot' or message.author.name == 'guanweiboy':
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
                if message.author.name == 'q89675851':
                    await bot.connected_channels[0].send(f'@{message.author.name} 此用戶持有三行pass，免除禁言處分 guanwe1Mao6')
                else:
                    await bot.connected_channels[0].send(f'@{message.author.name} cmonBruh 偵測到三行，請節制發言 👉🏿👈🏿')
                    timeout(message.author.id)

        await self.handle_commands(message)
        return message.author.name


    @commands.command()
    async def apex(self, ctx: commands.Context):
        await ctx.send(f' @{ctx.author.name} 點擊觀看冠緯Apex爆殺四名頂獵 guanwe1Bang https://www.youtube.com/watch?v=mZNc3zHd-XQ&t=52s&pp=ygUL5Yag57evIGFwZXg%3D')

    @commands.command()
    async def Apex(self, ctx: commands.Context):
        await ctx.send(f' @{ctx.author.name} 點擊觀看冠緯Apex爆殺四名頂獵 guanwe1Bang https://www.youtube.com/watch?v=mZNc3zHd-XQ&t=52s&pp=ygUL5Yag57evIGFwZXg%3D')

    @commands.command(name='600')
    async def vanish(self, ctx):
        broadcaster_id = "150989534"
        moderator_id = "653847938"
        user_id = ctx.author.id
        duration = 600
        reason = "They wanna timeout themselves"

        headers = {
            "Client-Id": 'gp762nuuoqcoxypju8c569th9wz7q5',
            "Authorization": "Bearer 8qi84ffjuedzanri1vs74dhfu0rmd3",
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


        respond_list = ['想冷靜一下0..0', '覺得刀子很利，自ban了 guanwe1789 ', 'See u in 600 seconds!']

        if response.status_code == 200:
            await ctx.send(f" @{ctx.author.name} {random.choice(respond_list)}")
        else:
            print(response.text)
            await ctx.send(f" @{ctx.author.name} ban不了你QAQ")

    @commands.command(name='抽')
    async def vanishPOT(self, ctx):
        broadcaster_id = "150989534"
        moderator_id = "653847938"  
        user_id = ctx.author.id  

        # 定義禁言時間及其對應的權重
        timeout_options = [10,69, 487, 1212]  # 禁言時間（秒）
        weights = [0.5, 0.25, 0.15, 0.1]  # 對應的機率，加總需為 1

        # 隨機選擇禁言時間
        duration = random.choices(timeout_options, weights)[0]

        reason = "They wanna timeout themselves" 

        headers = {
            "Client-Id": 'gp762nuuoqcoxypju8c569th9wz7q5',
            "Authorization": "Bearer 8qi84ffjuedzanri1vs74dhfu0rmd3",
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

        if response.status_code == 200:  # Twitch API 成功回傳狀態
            if duration == 1212:
                await ctx.send(f"恭喜 @{ctx.author.name} 抽中大獎，禁言1212秒！")
            else:
                pass
        else:
            pass


    @commands.command(name='6OO')
    async def vanish2(self, ctx):
        broadcaster_id = "150989534"
        moderator_id = "653847938"
        user_id = ctx.author.id
        duration = 600
        reason = "They wanna timeout themselves"

        headers = {
            "Client-Id": 'gp762nuuoqcoxypju8c569th9wz7q5',
            "Authorization": "Bearer 8qi84ffjuedzanri1vs74dhfu0rmd3",
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


        if response.status_code == 200:
            await ctx.send(f" @{ctx.author.name} 以為打OO就不會被ban SUBprise SUBprise ")


    @commands.command(name='600 ')
    async def vanish3(self, ctx):
        broadcaster_id = "150989534"
        moderator_id = "653847938"
        user_id = ctx.author.id
        duration = 600
        reason = "They wanna timeout themselves"

        headers = {
            "Client-Id": 'gp762nuuoqcoxypju8c569th9wz7q5',
            "Authorization": "Bearer 8qi84ffjuedzanri1vs74dhfu0rmd3",
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


        if response.status_code == 200:
            await ctx.send(f" @{ctx.author.name} 以為加了空格就不會被ban SUBprise SUBprise ")


    @commands.command(name='6᱐᱐')
    async def vanish4(self, ctx):
        broadcaster_id = "150989534"
        moderator_id = "653847938"
        user_id = ctx.author.id
        duration = 600
        reason = "They wanna timeout themselves"

        headers = {
            "Client-Id": 'gp762nuuoqcoxypju8c569th9wz7q5',
            "Authorization": "Bearer 8qi84ffjuedzanri1vs74dhfu0rmd3",
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


        if response.status_code == 200:
            await ctx.send(f" @{ctx.author.name} 以為換字體就不會被ban SUBprise SUBprise ")

    @commands.command(name='CSO')
    async def commercial(self, ctx: commands.Context):
        await ctx.send(f' @{ctx.author.name} ❄️超多精彩活動都在冬季行事曆：https://pse.is/6t6tur 快點下載註冊登入吧🔥 guanwe1Mao6 ')

    @commands.command()
    async def please(self, ctx: commands.Context):
        await ctx.send(f' @{ctx.author.name} 懇求的臉 🥺🥺🥺🥺🥺')

    @commands.command(name='分數')
    async def points(self, ctx: commands.Context):
        point = rank()
        winrate= "{:.1f}".format(float((point[3]/(point[3]+point[4]))*100))
        output = str(f'@{ctx.author.name} 韓服即時分數 :\nsølips#ism:{point[0]} {point[1]} {point[2]}分, 當前賽季勝率:{winrate}%')
        await ctx.send(output)

    @commands.command(name='r')
    async def rpoints(self, ctx: commands.Context):
        point = rank()
        winrate= "{:.1f}".format(float((point[3]/(point[3]+point[4]))*100))
        output = str(f'@{ctx.author.name} 韓服即時分數 :\nsølips#ism:{point[0]} {point[1]} {point[2]}分, 當前賽季勝率:{winrate}%')
        await ctx.send(output)

    @commands.command(name='rk')
    async def rrpoints(self, ctx: commands.Context):
        point = rank()
        winrate= "{:.1f}".format(float((point[3]/(point[3]+point[4]))*100))
        output = str(f'@{ctx.author.name} 韓服即時分數 :\nsølips#ism:{point[0]} {point[1]} {point[2]}分, 當前賽季勝率:{winrate}%')
        await ctx.send(output)

    @commands.command(name='RK')
    async def rrrpoints(self, ctx: commands.Context):
        point = rank()
        winrate= "{:.1f}".format(float((point[3]/(point[3]+point[4]))*100))
        output = str(f'@{ctx.author.name} 韓服即時分數 :\nsølips#ism:{point[0]} {point[1]} {point[2]}分, 當前賽季勝率:{winrate}%')
        await ctx.send(output)       

    @commands.command(name='牌位')
    async def rpointss(self, ctx: commands.Context):
        point = rank()
        winrate= "{:.1f}".format(float((point[3]/(point[3]+point[4]))*100))
        output = str(f'@{ctx.author.name} 韓服即時分數 :\nsølips#ism:{point[0]} {point[1]} {point[2]}分, 當前賽季勝率:{winrate}%')
        await ctx.send(output)

    @commands.command(name='rank')
    async def rpointsss(self, ctx: commands.Context):
        point = rank()
        winrate= "{:.1f}".format(float((point[3]/(point[3]+point[4]))*100))
        output = str(f'@{ctx.author.name} 韓服即時分數 :\nsølips#ism:{point[0]} {point[1]} {point[2]}分, 當前賽季勝率:{winrate}%')
        await ctx.send(output)

    @commands.command(name='排位')
    async def rpointssss(self, ctx: commands.Context):
        point = rank()
        winrate= "{:.1f}".format(float((point[3]/(point[3]+point[4]))*100))
        output = str(f'@{ctx.author.name} 韓服即時分數 :\nsølips#ism:{point[0]} {point[1]} {point[2]}分, 當前賽季勝率:{winrate}%')
        await ctx.send(output)

    @commands.command(name='R')
    async def Rpointss(self, ctx: commands.Context):
        point = rank()
        winrate= "{:.1f}".format(float((point[3]/(point[3]+point[4]))*100))
        output = str(f'@{ctx.author.name} 韓服即時分數 :\nsølips#ism:{point[0]} {point[1]} {point[2]}分, 當前賽季勝率:{winrate}%')
        await ctx.send(output)

    @commands.command(name='歌單')
    async def playlist(self, ctx: commands.Context):
        await ctx.send(f' @{ctx.author.name} guanwe1Maomao https://www.youtube.com/playlist?list=PLi6wzs-FmmftsTQ6YW2jmES01JhLj07WA')

    @commands.command(name='songlist')
    async def playlist2(self, ctx: commands.Context):
        await ctx.send(f' @{ctx.author.name} guanwe1Maomao https://www.youtube.com/playlist?list=PLi6wzs-FmmftsTQ6YW2jmES01JhLj07WA')

    @commands.command(name='骰子')
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
            await ctx.send(f'🎲 骰子丟出...結果為：{output}！')

    @commands.command(name='冠貓')
    async def meow(self, ctx: commands.Context):

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

        url = 'https://api.twitch.tv/helix/chat/chatters'
        headers = {
            'Authorization': 'Bearer 8qi84ffjuedzanri1vs74dhfu0rmd3',
            'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'
        }
        params = {
            'broadcaster_id': '150989534',
            'moderator_id': '653847938'
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200 and check_if_live("guanweiboy") == 0:
            data = response.json()
            total = data.get('total', 0)
        else:
            print('Failed to retrieve data:', response.status_code, response.text)

        await ctx.send(f' @{ctx.author.name} 包含你，有{total}隻死忠冠貓在聊天室喵 guanwe1Mao6')

    #運勢指令冷卻資料庫

    def init_db():
        conn = sqlite3.connect("fortune.db")  # 建立或連接資料庫
        cursor = conn.cursor()
        # 建立表格（如果不存在）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS command_usage (
            user_id TEXT NOT NULL,
            command_name TEXT NOT NULL,
            last_executed TIMESTAMP NOT NULL,
            PRIMARY KEY (user_id, command_name)
        )
        """)
        conn.commit()
        conn.close()
    
    init_db()  # 初始化資料庫
    
    
    @commands.command(name='運勢')
    async def fortune(self, ctx: commands.Context):
        cooldown = 12  # 冷卻時間（秒）
        remaining_time = self.check_and_update_cooldown('運勢', cooldown)
        if remaining_time:
            return
        
        fort = ['大吉','中吉','小吉','末吉','凶']
        big = ['天時地利人和，萬事皆能順心如意','無論前進還是停下，都能感受到充滿力量的支持','陽光普照，所有事物都在朝著好的方向發展','內外皆和諧，任何挑戰都能輕鬆迎刃而解','運勢鼎盛，一切都能迎來圓滿的結果']
        mid = ['平穩中帶有上升的氣息，耐心耕耘必有回報','雖然不驚艷，但整體局勢令人感到安心愉快','穩中求進，環境雖未達最佳，但仍有光明可循','雲淡風輕，偶有微風助力，適合穩步前進','運勢逐漸好轉，保持節奏即可迎接美好的變化']
        small = ['時有小福降臨，但仍需腳踏實地，持續努力','局勢略顯波動，但整體方向仍是良好的','偶有阻礙，但每個挑戰都帶來新的可能性','運氣尚可，不宜急功近利，穩健是最佳策略','稍縱即逝的小幸運出現，留心細節便能抓住機會']
        tiny = ['運勢偏弱，但保持冷靜與謹慎仍能穩步向前','現階段需要耐心等待，時機尚未完全成熟','環境略有阻礙，但只要適應節奏即可逐漸改善','表面看似平靜，實則潛藏波折，需時刻注意動態','進展緩慢，但細心經營仍有希望看到成果']
        bad = ['風雨交加，需多加防範，避免冒然行動','低潮時期，保持內心的穩定是最重要的','步履維艱，當下宜以謹慎和耐心為先','暗藏危機，需避免過度樂觀，切勿心存僥倖','外部環境不穩，適宜縮減行動，靜待時局明朗']    
        color = ['紅','亮紅','橘紅','橙','陽光黃','黃綠','森林綠','藍','天藍','海洋藍','紫','薰衣草紫','水藍','黑','白','小倪黃','一件黑','好嫩好白','蒂芬妮綠','棕','草綠','連世橙','愛馬仕橘']
        cat = ['guanwe1Mao6','guanwe1Mao1','guanwe1Mao2','guanwe1Nerd','guanwe1Gugu','guanwe1Shy','guanwe1Mao','guanwe1GOOD']
        goodto = ['打LOL','告白','翹課','自助旅行','檢舉世誠','檢舉羅傑','抖內','買樂透','買刮刮樂','抖影片','用歐付寶說話','嘲笑逼寶','玩撲克','在女實況主YT影片留言','訂閱冠緯','跟團旅行','投資','靜','讀書','讀paper']
        notto = ['打LOL','告白','看實況','呼吸','生存','去樓頂放風','低頭看手機','交易股票','交易虛擬貨幣','賭博下注','偷滑主','帶辣條去上班','在fb分享網紅影片','訂閱世誠','爬山','玩水','標記']
    # 檢查是否可以執行指令
        def can_execute_command(user_id, command_name):
            conn = sqlite3.connect("commands.db")
            cursor = conn.cursor()
            
            # 查詢用戶的指令執行時間
            cursor.execute("""
            SELECT last_executed FROM command_usage
            WHERE user_id = ? AND command_name = ?
            """, (user_id, command_name))
            result = cursor.fetchone()
            
            current_time = datetime.now()
            
            if result:
                last_executed = datetime.fromisoformat(result[0])  # 取得上次執行時間
                # 檢查是否已超過一天
                if current_time - last_executed < timedelta(days=0.5):
                    conn.close()
                    return False  # 不允許執行
            
            # 更新或插入執行時間
            cursor.execute("""
            INSERT OR REPLACE INTO command_usage (user_id, command_name, last_executed)
            VALUES (?, ?, ?)
            """, (user_id, command_name, current_time.isoformat()))
            conn.commit()
            conn.close()
            return True  # 允許執行
        
        user_id = ctx.author.name
        command_name = "運勢"
        
        fcat = random.choice(cat)
        fcolor = random.choice(color)
        result_fortune = random.choice(fort)
        fgoodto = random.choice(goodto)
        fnotto = random.choice(notto)
        
        if result_fortune == '大吉':
            name = '大吉'
            result = random.choice(big)
            if can_execute_command(user_id, command_name):
                await ctx.send(f'@{ctx.author.name} guanwe1888 您的今日運勢為：{name} | {result}, 宜：{fgoodto} | 幸運色：{fcolor} | 幸運貓： {fcat}')
            else:
                print('cooldown')
        elif result_fortune == '中吉':
            name = '中吉'
            result = random.choice(mid)
            if can_execute_command(user_id, command_name):
                await ctx.send(f'@{ctx.author.name} guanwe1888 您的今日運勢為：{name} | {result}, 宜：{fgoodto} | 幸運色：{fcolor} | 幸運貓： {fcat}')
            else:
                print('cooldown')
        elif result_fortune == '小吉':
            name = '小吉'
            result = random.choice(small)
            if can_execute_command(user_id, command_name):
                await ctx.send(f'@{ctx.author.name} guanwe1888 您的今日運勢為：{name} | {result}, 宜：{fgoodto} | 幸運色：{fcolor} | 幸運貓： {fcat}')
            else:
                print('cooldown')
        elif result_fortune == '末吉':
            name = '末吉'
            result = random.choice(tiny)
            if can_execute_command(user_id, command_name):
                await ctx.send(f'@{ctx.author.name} guanwe1888 您的今日運勢為：{name} | {result}, 不宜：{fnotto} | 幸運色：{fcolor} | 幸運貓： {fcat}')
            else:
                print("cooldown")
        elif result_fortune == '凶':
            name = '凶'
            result = random.choice(bad)
            if can_execute_command(user_id, command_name):
                await ctx.send(f'@{ctx.author.name} guanwe1888 您的今日運勢為：{name} | {result}, 不宜：{fnotto} | 幸運色：{fcolor} | 幸運貓： {fcat}')
            else:
                print('cooldown')

    @commands.command(name='玩什麼')
    async def play(self, ctx: commands.Context):
        cooldown = 15  # 冷卻時間（秒）
        remaining_time = self.check_and_update_cooldown('玩什麼', cooldown)

        if remaining_time:
            return

        games = [
            "英雄聯盟", "LOL", "League of Legends", "steam只逛不買", "哩跟歐甫咧捐", "韓服英雄聯盟",
            "台服英雄聯盟", "陸服英雄聯盟", "日服英雄聯盟", "poker", "戶外台", "魔物獵人", "跑跑",
            "Apex", "陪玩只看不點", "楓之谷", "瀏覽Live頻道"
        ]
        cgame = random.choice(games)
        output = str(f'@{ctx.author.name} {cgame} guanwe1Bangbang')
        await ctx.send(output)

    @commands.command(name='吃什麼')
    async def eat(self, ctx: commands.Context):
        cooldown = 15  # 冷卻時間（秒）
        remaining_time = self.check_and_update_cooldown('吃什麼', cooldown)

        if remaining_time:
            return

        foods = [
            "牛肉麵", "水餃", "飯糰", "炒飯", "炒麵", "乾麵", "湯麵", "湯餃", "滷肉飯", "雞肉飯", 
            "雞魯飯", "肉羹麵", "魚酥羹麵", "辣炒年糕", "部隊鍋", "手捲", "大醬湯", "韓式起司拉麵", 
            "拉麵", "壽喜燒", "丼飯", "壽司", "火鍋", "燒烤", "海底撈", "義大利麵", "法式料理", 
            "三明治", "便利商店", "地瓜球", "排骨湯", "麥當勞", "肯德基", "漢堡王", "熱炒", 
            "雞排", "麵包", "鍋燒意麵", "烤肉飯", "水果", "沙拉", "餅乾", "自助餐", "披薩"
        ]
        cfood = random.choice(foods)
        output = str(f'@{ctx.author.name} {cfood} guanwe1Bangbang')
        await ctx.send(output)

    @commands.command(name='冠貓塔')
    async def tower(self, ctx: commands.Context): 
        cooldown = 90  # 冷卻時間（秒）
        remaining_time = self.check_and_update_cooldown('冠貓塔', cooldown)

        if remaining_time:
            return
        await ctx.send('⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ guanwe1Mao6 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ guanwe1Mao6 guanwe1Mao6 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ guanwe1Mao6 guanwe1Mao6 guanwe1Mao6 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ guanwe1Mao6 guanwe1Mao6 guanwe1Mao6 guanwe1Mao6 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ guanwe1Mao6 guanwe1Mao6 guanwe1Mao6 guanwe1Mao6 guanwe1Mao6')


    @commands.command(name='這場有誰')
    async def player(self, ctx: commands.Context):
        cooldown = 45  # 冷卻時間（秒）
        remaining_time = self.check_and_update_cooldown('這場有誰', cooldown)

        if remaining_time:
            return

        #await ctx.send('資料爬取中，請稍候')

        # 設定瀏覽器選項（可選）
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 無頭模式（不顯示瀏覽器）
        chrome_options.add_argument("--disable-gpu")  # 停用 GPU（適用於特定環境）

        # 設定 ChromeDriver 路徑
        service = Service("C:/chromedriver.exe")  # 替換為你的 chromedriver 路徑

        # 啟動 WebDriver
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 爬取網站完整 HTML 程式碼
        url = "https://www.deeplol.gg/summoner/kr/sølips-ism/ingame"  # 將此替換為目標網站 URL

        try:
            driver.get(url)

            # 等待頁面載入完成（可選，適用於動態內容）
            driver.implicitly_wait(10)  # 最多等待 10 秒

            # 模擬滾動頁面，等待所有內容加載
            # 可以根據網站的具體結構進行滾動，這裡設置滾動到底部，並重複直到加載完成
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                # 滾動到底部
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)  # 等待頁面加載新的內容
                new_height = driver.execute_script("return document.body.scrollHeight")

                # 如果滾動到底部且頁面高度不再變化，則停止滾動
                if new_height == last_height:
                    break
                last_height = new_height

            # 獲取完整的 HTML 原始碼
            html_content = driver.page_source
            print("成功取得完整網頁原始碼！")

            # 儲存 HTML 到檔案
            with open("ingame.html", "w", encoding="utf-8") as file:
                file.write(html_content)

        finally:
            # 關閉瀏覽器
            driver.quit()


        file_path = "ingame.html"
        search_word = "influ-name"

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        pro = []
        streamer = []
        blue_team = []
        red_team = []

        # 搜索所有 "藍" 和 "紅" 的位置
        blue_positions = [pos for pos in range(len(content)) if content.startswith("藍", pos)]
        red_positions = [pos for pos in range(len(content)) if content.startswith("紅", pos)]

        # 搜索所有匹配的位置
        matches = [pos for pos in range(len(content)) if content.startswith(search_word, pos)]

        # 根據位置進行分類
        for match in matches:
            # 在整個上下文中找 ">" 和 "<" 的位置
            start2 = content.find(">", match)
            end2 = content.find("<", start2)

            if start2 != -1 and end2 != -1 and start2 < end2:
                result = content[start2 + 1:end2]

                # 確定該位置的隊伍
                nearest_blue = max([pos for pos in blue_positions if pos < match], default=-1)
                nearest_red = max([pos for pos in red_positions if pos < match], default=-1)

                if nearest_blue > nearest_red:
                    blue_team.append(result)  # 屬於藍方
                elif nearest_red > nearest_blue:
                    red_team.append(result)  # 屬於紅方

                # 額外分類到 streamer 或 pro
                if 'strm' in content[match:]:
                    streamer.append(result)
                elif 'pro' in content[match:]:
                    pro.append(result)

            
        output = " | ".join(blue_team) 
        output2 = " | ".join(red_team) 
        await ctx.send(f'@{ctx.author.name} 藍方：{output} , 紅方：{output2}')  

    from typing import Optional

    @commands.command(name='level')
    async def level(self, ctx: commands.Context):
        cooldown = 12  # 冷卻時間（秒）
        remaining_time = self.check_and_update_cooldown('等級', cooldown)

        if remaining_time:
            return

        import sqlite3

        def get_user_data(user_id=None, user_name=None):
            """获取指定用户的 score、count 和 total"""
            with sqlite3.connect('D:/userslevel.db') as conn:
                cursor = conn.cursor()
                
                # 根据 user_id 或 user_name 查询用户数据
                if user_id:
                    cursor.execute('SELECT score, count, total FROM users WHERE user_id = ?', (user_id,))
                elif user_name:
                    cursor.execute('SELECT score, count, total FROM users WHERE user_name = ?', (user_name,))
                else:
                    return None, None, None
                
                result = cursor.fetchone()
                if result:
                    return result  # 返回 score, count, total
                else:
                    return None, None, None

        def get_user_rank(user_id=None, excluded_ids=None):
            """计算用户的 total 排名，可以排除特定用户"""
            with sqlite3.connect('D:/userslevel.db') as conn:
                cursor = conn.cursor()
                
                if excluded_ids:
                    query = '''
                        SELECT user_id, total 
                        FROM users 
                        WHERE user_id NOT IN ({}) 
                        ORDER BY total DESC
                    '''.format(','.join(['?'] * len(excluded_ids)))
                    cursor.execute(query, excluded_ids)
                else:
                    cursor.execute('SELECT user_id, total FROM users ORDER BY total DESC')

                all_users = cursor.fetchall()

                for rank, (u_id, total) in enumerate(all_users, start=1):
                    if user_id and u_id == user_id:
                        return rank, total
                return None, None

        def get_user_pr_rank(user_id):
            """计算用户的 PR 排名"""
            query = '''
                WITH user_stats AS (
                    SELECT 
                        total,
                        (SELECT COUNT(*) FROM users WHERE total > u.total) * 100.0 / 
                        (SELECT COUNT(*) FROM users) AS pr_percentage
                    FROM users u
                    WHERE user_id = ?
                )
                SELECT pr_percentage 
                FROM user_stats
            '''
            with sqlite3.connect('D:/userslevel.db') as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                if result:
                    return round(result[0], 3)
                return None

        def classify_by_percentage(percentage):
            """根据百分比分类段位"""
            if percentage <= 1:
                return '大師冠貓'
            elif percentage <= 10:
                return '鑽石冠貓'
            elif percentage <= 20:
                return '白金冠貓'
            elif percentage <= 35:
                return '黃金冠貓'
            elif percentage <= 50:
                return '白銀冠貓'
            elif percentage <= 60:
                return '青銅冠貓'
            else:
                return '簡單貓'


        user_id = ctx.author.id

        score, count, total = get_user_data(user_id=user_id)
        rank, total = get_user_rank(user_id=user_id, excluded_ids=['19264788', '653847938'])
        pr = get_user_pr_rank(user_id=user_id)

        
        if score is not None and count is not None:
            if rank <= 20:
                await ctx.send(f"@{ctx.author.name} guanwe1Gan 總積分--{total} 階級--菁英冠貓 #{rank} ({pr}%). 聊天數:{count} | 共觀看:{score * 0.25} hr")
            else:
                await ctx.send(f"@{ctx.author.name} guanwe1Gan 總積分--{total} 階級--{classify_by_percentage(pr)} #{rank} ({pr}%). 聊天數:{count} | 共觀看:{score * 0.25} hr")

    @commands.command(name='levelfor')
    async def levelfor(self, ctx: commands.Context, user_name: Optional[str] = None):
        cooldown = 10  # 冷卻時間（秒）
        remaining_time = self.check_and_update_cooldown('等級', cooldown)

        if remaining_time:
            return

        import sqlite3

        def get_user_data(user_id=None, user_name=None):
            """获取指定用户的 score、count 和 total"""
            with sqlite3.connect('D:/userslevel.db') as conn:
                cursor = conn.cursor()
                
                # 根据 user_id 或 user_name 查询用户数据
                if user_id:
                    cursor.execute('SELECT score, count, total FROM users WHERE user_id = ?', (user_id,))
                elif user_name:
                    cursor.execute('SELECT score, count, total FROM users WHERE user_name = ?', (user_name,))
                else:
                    return None, None, None
                
                result = cursor.fetchone()
                if result:
                    return result  # 返回 score, count, total
                else:
                    return None, None, None

        def get_user_rank(user_id=None, excluded_ids=None):
            """计算用户的 total 排名，可以排除特定用户"""
            with sqlite3.connect('D:/userslevel.db') as conn:
                cursor = conn.cursor()
                
                if excluded_ids:
                    query = '''
                        SELECT user_id, total 
                        FROM users 
                        WHERE user_id NOT IN ({}) 
                        ORDER BY total DESC
                    '''.format(','.join(['?'] * len(excluded_ids)))
                    cursor.execute(query, excluded_ids)
                else:
                    cursor.execute('SELECT user_id, total FROM users ORDER BY total DESC')

                all_users = cursor.fetchall()

                for rank, (u_id, total) in enumerate(all_users, start=1):
                    if user_id and u_id == user_id:
                        return rank, total
                return None, None

        def get_user_pr_rank(user_id):
            """计算用户的 PR 排名"""
            query = '''
                WITH user_stats AS (
                    SELECT 
                        total,
                        (SELECT COUNT(*) FROM users WHERE total > u.total) * 100.0 / 
                        (SELECT COUNT(*) FROM users) AS pr_percentage
                    FROM users u
                    WHERE user_id = ?
                )
                SELECT pr_percentage 
                FROM user_stats
            '''
            with sqlite3.connect('D:/userslevel.db') as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                if result:
                    return round(result[0], 3)
                return None

        def classify_by_percentage(percentage):
            """根据百分比分类段位"""
            if percentage <= 1:
                return '大師冠貓'
            elif percentage <= 10:
                return '鑽石冠貓'
            elif percentage <= 20:
                return '白金冠貓'
            elif percentage <= 35:
                return '黃金冠貓'
            elif percentage <= 50:
                return '白銀冠貓'
            elif percentage <= 60:
                return '青銅冠貓'
            else:
                return '簡單貓'

        # 如果提供了 user_name，则查询该用户的信息
        if user_name:
            with sqlite3.connect('D:/userslevel.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM users WHERE user_name = ?', (user_name,))
                user_id = cursor.fetchone()
                if user_id:
                    user_id = user_id[0]
                else:
                    return
        else:
            # 默認查詢當前用戶
            user_id = ctx.author.id

        score, count, total = get_user_data(user_id=user_id)
        rank, total = get_user_rank(user_id=user_id, excluded_ids=['19264788', '653847938'])
        pr = get_user_pr_rank(user_id=user_id)

        
        if score is not None and count is not None:
            if user_name:  # 查询其他用户时
                if rank <= 20:
                    await ctx.send(f"@{ctx.author.name} {user_name} 的數據: 總積分--{total} 階級--菁英冠貓 #{rank} ({pr}%). 聊天數:{count} | 共觀看:{score * 0.25} hr")
                else:
                    await ctx.send(f"@{ctx.author.name} {user_name} 的數據: 總積分--{total} 階級--{classify_by_percentage(pr)} #{rank} ({pr}%). 聊天數:{count} | 共觀看:{score * 0.25} hr")
            else:  # 查询自己时
                if rank <= 20:
                    await ctx.send(f"@{ctx.author.name} guanwe1Gan 總積分--{total} 階級--菁英冠貓 #{rank} ({pr}%). 聊天數:{count} | 共觀看:{score * 0.25} hr")
                else:
                    await ctx.send(f"@{ctx.author.name} guanwe1Gan 總積分--{total} 階級--{classify_by_percentage(pr)} #{rank} ({pr}%). 聊天數:{count} | 共觀看:{score * 0.25} hr")
        else:
            await ctx.send(f"@{ctx.author.name} 查無此用戶，請嘗試使用顯示ID(非純英數ID)")

    @commands.command(name='top10')
    async def top10(self, ctx: commands.Context):
        cooldown = 15  # 冷卻時間（秒）
        remaining_time = self.check_and_update_cooldown('top10', cooldown)

        if remaining_time:
            return
        
        rank_labels = ["1st", "2nd", "3rd"] + [f"{i}th" for i in range(4, 11)]  # 定義排名格式
        formatted_top_users = []
        skip_users = {"Nightbot","阿倫同學"}
        
        try:
            # 連接資料庫
            conn = sqlite3.connect("D:/userslevel.db")
            cursor = conn.cursor()
            
            # 查詢前十名用戶（根據你的需求排序，這裡假設以 total 降序排序）
            query = "SELECT user_name FROM users ORDER BY total DESC LIMIT 12"
            cursor.execute(query)
            results = cursor.fetchall()
            
            # 遍歷結果，跳過 "Nightbot"，只記錄前十名
            count = 0
            for user_name, in results:
                if user_name in skip_users:
                    continue  
                
                formatted_top_users.append(f"{rank_labels[count]}: {user_name}")
                count += 1
                
                if count == 10:  # 只記錄前十名
                    break
            
            conn.close()
        except Exception as e:
            print(f"資料庫操作失敗: {e}")
    
        await ctx.send(f'@{ctx.author.name} guanwe1Nerd 魯蛇排行---{" ".join(formatted_top_users)}')

bot = Bot()
bot.run()

