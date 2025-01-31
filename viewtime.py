# 2024/1/26 00:00 第一次更新

from twitchio.ext import commands
from dataclasses import dataclass
#import keep_alive
import json
import requests
import random
import time
import os
from collections import deque
import sqlite3
import json
import csv

def make_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return response.json()  # Return the JSON response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Print HTTP error
    except Exception as err:
        print(f"Other error occurred: {err}")  # Print any other error

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
        self.cooldown_period = 30  # Cooldown period in seconds
        self.recent_results = deque(maxlen=20)  # Use a deque with a maximum length of 20 to store the recent results

        def times(self):
            url = 'https://api.twitch.tv/helix/chat/chatters'
            headers = {
                'Authorization': 'Bearer 8qi84ffjuedzanri1vs74dhfu0rmd3',
                'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'

            }
            params = {
                'broadcaster_id': '150989534',
                'moderator_id': '653847938',
                'first' : 1000
            }

            all_chatters = []
            cursor = None

            while True:
                # 如果有分頁游標，加入到請求參數中
                if cursor:
                    params["after"] = cursor
                
                # 發送 API 請求
                response = requests.get(url, headers=headers, params=params)
                if response.status_code != 200:
                    print(f"Error: {response.status_code}, {response.json()}")
                    break
                
                data = response.json()
                chatters = data.get("data", [])
                all_chatters.extend(chatters)
                
                # 檢查是否有下一頁
                cursor = data.get("pagination", {}).get("cursor")
                if not cursor:
                    break

            return all_chatters

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

        def update_database_with_scores(self,db_path, response_data):
            """
            根据响应更新数据库中的数据。
            
            :param db_path: 数据库文件路径
            :param response_data: JSON 响应中的 data 列表
            """
            if check_if_live("guanweiboy") == 1:
                try:
                    # 连接数据库
                    self.conn = sqlite3.connect(db_path)
                    self.cursor = self.conn.cursor()
                    
                    # 创建表（如果不存在）
                    self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT UNIQUE NOT NULL,
                        user_name TEXT NOT NULL,
                        score INTEGER NOT NULL DEFAULT 0,
                        count INTEGER NOT NULL DEFAULT 0,
                        total REAL GENERATED ALWAYS AS ((score * 25) + (count * 1)) STORED                                    
                    )
                    ''') 
                    
                    # 处理响应数据
                    for user in response_data:
                        user_id = user['user_id']
                        user_name = user['user_name']
                        
                        # 检查是否存在该 user_id
                        self.cursor.execute('SELECT id, score FROM users WHERE user_id = ?', (user_id,))
                        result = self.cursor.fetchone()
                        
                        if result:
                            # 如果 user_id 已存在，增加分数并更新 user_name
                            new_score = result[1] + 1
                            self.cursor.execute('''
                                UPDATE users 
                                SET score = ?, user_name = ? 
                                WHERE user_id = ?
                            ''', (new_score, user_name, user_id))
                            # print(f"Updated user {user_id}: +1 point, new score = {new_score}, user_name updated to {user_name}.")
                        else:
                            # 如果 user_id 不存在，添加新记录
                            self.cursor.execute('INSERT INTO users (user_id, user_name, score) VALUES (?, ?, ?)', (user_id, user_name, 1))
                            #print(f"Added new user {user_id}: initial score = 1.")
                    
                    # 提交更改
                    self.conn.commit()
            
                except sqlite3.Error as e:
                    print(f"An error occurred: {e}")
                
                finally:
                    # 关闭连接
                    if self.conn:
                        self.conn.close()
            else: 
                pass           

        db_path = 'D:/userslevel.db'
        
        while True:
            print("Sending request...")
            response = times(self)
            update_database_with_scores(self,db_path, response)
            print("Database updated. Waiting for next request...")
            time.sleep(900)


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


bot = Bot()
bot.run()
