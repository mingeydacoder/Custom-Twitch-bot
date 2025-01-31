import sqlite3
import requests
from dataclasses import dataclass
from twitchio.ext import commands

@dataclass
class MessageData:
    author: str
    content: str
    channel: str
    is_mod: bool

class Bot(commands.Bot):

    def __init__(self):
        # Initialize the Bot with access token, prefix, and channels to join
        super().__init__(token='8qi84ffjuedzanri1vs74dhfu0rmd3', prefix='!', initial_channels=['guanweiboy'])
        self.author_names = []
        self.last_announcement_time = 0
        self.cooldown_period = 90  # Cooldown period in seconds

        # Initialize database connection and cursor
        self.conn = sqlite3.connect('D:/userslevel.db')
        self.cursor = self.conn.cursor()

    async def event_ready(self):
        # Notify when the bot is ready
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Ignore messages sent by the bot itself
        if message.echo:
            return

        # Get user info from the message
        user_id = message.author.id
        user_name = message.author.name

        # Check if the user exists in the database
        self.cursor.execute('SELECT id, count FROM users WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()

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
                return 0

        # Check if the channel is live
        if check_if_live2("guanweiboy") == 1:
            if result:
                # If the user exists, increase the message count
                new_count = result[1] + 1
                self.cursor.execute('UPDATE users SET count = ? WHERE user_id = ?', (new_count, user_id))
                self.conn.commit()  # Commit changes to the database
            else:
                # If the user does not exist, insert a new record with an initial count of 1
                self.cursor.execute('INSERT INTO users (user_name, user_id, count) VALUES (?, ?, ?)', (user_name, user_id, 1))
                self.conn.commit()  # Commit changes to the database
        else:
            pass

    def close(self):
        # Close the database connection when the bot shuts down
        self.conn.close()

# Initialize and run the bot
bot = Bot()
bot.run()
