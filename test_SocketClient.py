import socket, pickle, SocketServer, asyncio, os
from werkzeug import Response
from dotenv import load_dotenv

PATH = os.path.dirname(os.path.abspath(__file__))
load_dotenv(f'{PATH}/TOKEN_BOT.env')
TOKEN = os.getenv('TOKEN')
TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN_KEY = os.getenv('TWITTER_ACCESS_TOKEN_KEY')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
TWITCH_CLIENTID = os.getenv('TWITCH_ID')
TWITCH_SECRET = os.getenv('TWITCH_SECRET')
TWITCH_CALLBACK = os.getenv('CALLBACK')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
SEED = os.getenv('KEY')


class ProcessData:
    def __init__(self, Message=None):
        self.Message = Message

Dic = {
   "total": 12,
   "data": [
       {
           "topic": "https://api.twitch.tv/helix/streams?user_id=123",
           "callback": "http://example.com/your_callback",
           "expires_at": "2018-07-30T20:00:00Z"
       },
       {
           "topic": "https://api.twitch.tv/helix/streams?user_id=345",
           "callback": "http://example.com/your_callback",
           "expires_at": "2018-07-30T20:03:00Z"
       }
   ],
   "pagination": {
       "cursor": "eyJiIjpudWxsLCJhIjp7IkN1cnNvciI6IkFYc2laU0k2TVN3aWFTSTZNWDAifX0"
   }
}

Server = SocketServer.Handler(TWITCH_CLIENTID, TWITCH_SECRET, "https://whitekeks.tk/")

async def t():
    Users = await Server.GETRequest(
        url="https://api.twitch.tv/helix/users",
        params=[["login","whitekeks"],["login","c4ndygg"]],
        headers={
			'Authorization': await Server.getToken(),
			'Client-Id': Server.CLIENTID
		}
    )
    print(Users)

loop = asyncio.get_event_loop()
loop.run_until_complete(t())