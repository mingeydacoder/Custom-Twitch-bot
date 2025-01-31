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

        #發言計數器

        user_id = message.author.id
        user_name = message.author.name

        with sqlite3.connect('D:/userslevel.db') as conn:
            cursor = conn.cursor()

            # 检查用户是否已存在
            cursor.execute('SELECT id, count FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()

            def check_if_live2(username):
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
            
            if check_if_live2("guanweiboy") == 1:
                if result:
                    # 如果用户已存在，增加发言计数
                    new_count = result[1] + 1
                    cursor.execute('UPDATE users SET count = ? WHERE user_id = ?', (new_count, user_id))
                    conn.commit
                    #print(f"Updated user {user_id}: new message count = {new_count}.")
                else:
                    # 如果用户不存在，插入新记录并设置初始计数为 1
                    cursor.execute('INSERT INTO users (user_name, user_id, count) VALUES (?, ?, ?)', (user_name, user_id, 1))
                    conn.commit
                    #print(f"Added new user {user_id}: initial message count = 1.")
            else:
                pass



  
bot = Bot()
bot.run()

