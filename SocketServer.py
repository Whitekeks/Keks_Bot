import socket
import pickle
import aiohttp
import asyncio
from threading import Thread
from werkzeug import Response, Request
from time import sleep

alive = True

class Handler:

    def __init__(self, CLIENTID, SECRET, CALLBACK, DataHandler=print, HOST='localhost', PORT_REC=50007, PORT_SEND=50008):
        self.CLIENTID = CLIENTID
        self.SECRET = SECRET
        if CALLBACK[len(CALLBACK)-1]=="/":
            self.CALLBACK = CALLBACK + f"twitch/{UserID}"
        else:
            self.CALLBACK = CALLBACK + f"/twitch/{UserID}"
        self.HOST = HOST
        self.PORT_REC = PORT_REC
        self.PORT_SEND = PORT_SEND
        self.DataHandler = DataHandler
        self.HandlerThread = Thread(target=self.handler)
        self.active = False


    def handler(self):
        while alive:
            try:
                # Recieve Data as query
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind((self.HOST, self.PORT_REC))
                self.active = True
                s.listen()
                conn, addr = s.accept()
                data = conn.recv(4096)
                query = pickle.loads(data)  # query : Dict
                # query = response.args
                conn.close()
                s.close()

                # Check for stop_command:
                if query == "stop":
                    self.active = False
                    break

                # Deal with Data only when its relevant (only when passed through "data")
                if type(query) == dict:
                    Thread(target=self.DataHandler, args=(query,)).start()
                
                # Response in .wsgi because Response not depending on DataHandler and not needed, just uncommend if needed:

                # # create Response object
                # # a try block for every case (change for better format (todo))
                # try:
                #     # if 'hub.mode' exists it was an unsubscription or a subscription
                #     if query['hub.mode'] == 'denied':
                #         answer = Response(response='200: OK', status=200)

                #     # if it was not denied, than the hub.challenge token must be echoed
                #     if query['hub.challenge']:
                #         answer = Response(
                #             response=query['hub.challenge'], content_type='application/json')
                # except:
                #     # if it has not 'hub.mode', then just an ok-response is required
                #     answer = Response(response='200: OK', status=200)

                # # Send Response-objekt
                # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # s.connect((self.HOST, self.PORT_SEND))
                # data_string = pickle.dumps(answer)  # change depending on mode
                # s.send(data_string)
                # s.close()
            except:
                self.active = False
                sleep(1)


    def stop(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.HOST, self.PORT_REC))
        data_string = pickle.dumps("stop")
        s.send(data_string)
        while self.active:
            None
        print("Handler stopped")



    def start(self):
        self.HandlerThread.start()
        while not self.active:
            None
        print("Handler started")


    async def getToken(self):
        params = {
            'client_id': self.CLIENTID,
            'client_secret': self.SECRET,
            'grant_type':  'client_credentials'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url='https://id.twitch.tv/oauth2/token', params=params) as resp:
                answer = await resp.json()
                return f"Bearer {answer['access_token']}"


    async def GETRequest(self, url: str, params: dict, headers: dict):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, params=params, headers=headers) as resp:
                return await resp.json(content_type=None)


    async def POSTRequest(self, url: str, params: dict, headers: dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, params=params, headers=headers) as resp:
                return await resp.json(content_type=None)


    async def HookStream(self, loginName : str, mode : str):
        Token = await self.getToken()
        headers = {
            'Authorization': Token,
            'Client-Id': self.CLIENTID
        }

        # Get UserData
        UserData = await self.GETRequest(
            url='https://api.twitch.tv/helix/users',
            params={'login': loginName},
            headers=headers
        )

        try:
            UserID = UserData['data'][0]['id']
        except:
            return {'error' : 'User not found'}

        # Make subscription
        subscription = await self.POSTRequest(
            url='https://api.twitch.tv/helix/webhooks/hub',
            params={
                'hub.callback': self.CALLBACK,
                'hub.mode': mode,
                'hub.topic': f"https://api.twitch.tv/helix/streams?user_id={UserID}",
                'hub.lease_seconds': 86400,
                'hub.secret': f"{UserID}"
            },
            headers=headers
        )

        # send back verification for subscription, if None then successfully to Callback:
        return subscription


