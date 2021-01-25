from twitchAPI.twitch import Twitch
from twitchAPI.webhook import TwitchWebHook
import os, asyncio
from dotenv import load_dotenv
from time import sleep

PATH = os.path.dirname(os.path.abspath(__file__))
load_dotenv(f'{PATH}/TOKEN_BOT.env')
TOKEN = os.getenv('TOKEN')
TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN_KEY = os.getenv('TWITTER_ACCESS_TOKEN_KEY')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
TWITCH_ID = os.getenv('TWITCH_ID')
TWITCH_SECRET = os.getenv('TWITCH_SECRET')
SEED = os.getenv('KEY')

twitch = Twitch(TWITCH_ID, TWITCH_SECRET)
twitch.authenticate_app([])
user_info = twitch.get_users(logins=['Whitekeks'])
user_id = user_info['data'][0]['id']

hook = TwitchWebHook('https://167.86.119.250', TWITCH_ID, 443)
hook.authenticate(twitch)
hook.start()

def callback_stream_changed(uuid, data):
    print('Callback for UUID ' + str(uuid))
    print(data)

print('subscribing to hook:')
success, uuid = hook.subscribe_stream_changed(user_id, callback_stream_changed)
print(success)
if not succes:
    hook.stop()