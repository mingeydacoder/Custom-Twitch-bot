from twitchio.ext import commands
from dataclasses import dataclass
import requests
import subprocess
import json


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
        super().__init__(token='mloiry6jiupz7qrzfzwii5l1kzr46g', prefix='!', initial_channels=['lav3nd3rtree'])
        self.processes = []  # 存儲 3 個子進程
        self.scripts = ["C:/Users/allen/OneDrive/桌面/viewtime.py", "C:/Users/allen/OneDrive/桌面/twitchbot.py", "C:/Users/allen/OneDrive/桌面/chatcount.py"]  # 要執行的 Python 檔案


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
        
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)
        return message.author.name

    @commands.command(name='mode')
    async def toggle_mode(self, ctx: commands.Context):
        if self.processes:
            # 如果程式正在運行，就關閉所有子進程
            for process in self.processes:
                if process.poll() is None:  # 確保程式還在運行
                    process.terminate()  # 終止該程式
            self.processes.clear()  # 清空進程列表
            await ctx.send(f"@{ctx.author.name} 所有外部程式已關閉 guanwe1Cry")
        else:
            # 啟動 3 個不同的 Python 程式
            for script in self.scripts:
                process = subprocess.Popen(
                    ["python", script],  # 執行外部 Python 檔案
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                self.processes.append(process)  # 儲存進程
            await ctx.send(f"@{ctx.author.name} 已啟動 3 個外部程式 guanwe1Gan")

    @commands.command(name='status')
    async def check_status(self, ctx: commands.Context):
        """檢查目前運行中的程式數量"""
        running_count = sum(1 for p in self.processes if p.poll() is None)
        await ctx.send(f"@{ctx.author.name} 目前有 {running_count} 個程式在運行 guanwe1Bangbang")

bot = Bot()
bot.run()
