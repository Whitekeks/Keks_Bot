import socket, pickle
from werkzeug import Response

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


HOST = 'localhost'
PORT_SEND = 50007
PORT_REC = 50008
for i in range(0,1):
    try:
        # Pickle the object and send it to the server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT_SEND))
        data_string = pickle.dumps(Dic)
        s.send(data_string)
        s.close()

        # Wait for response and send it to Twitch
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT_REC))
        s.listen()
        conn, addr = s.accept()
        data = conn.recv(4096)
        data_variable = pickle.loads(data)
        conn.close()
        s.close()

        print(data_variable.response)
    except:
        print(404)