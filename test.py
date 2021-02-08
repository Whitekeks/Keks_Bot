import asyncio, aiohttp, SocketServer, os
from dotenv import load_dotenv

async def POSTRequest(url: str, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=data) as resp:
                return resp.status

data = b"{'data': [{'game_id': '511224', 'game_name': 'Apex Legends', 'id': '40965739612', 'language': 'de', 'started_at': '2021-02-02T18:35:52Z', 'tag_ids': None, 'thumbnail_url': 'https://static-cdn.jtvnw.net/previews-ttv/live_user_c4ndygg-{width}x{height}.jpg', 'title': 'Season 8 LETS GOOOOO #TeamSalsa #Eddy #music #OpenEndGaming [Ger | Eng]', 'type': 'live', 'user_id': '246901251', 'user_login': 'c4ndygg', 'user_name': 'c4ndygg', 'viewer_count': 0}]}"
empty = b"{'data': []}"
loop = asyncio.get_event_loop()
status = loop.run_until_complete(POSTRequest("https://www.whitekeks.de/twitch/246901251", empty))
print(status)

# {'id': '898263526', 'user_id': '246901251', 'user_login': 'c4ndygg', 'user_name': 'c4ndygg', 'title': "Season 8 LET'S GOOOOO #TeamSalsa #Eddy #music #OpenEndGaming [Ger | Eng]", 'description': '', 'created_at': '2021-02-02T18:36:05Z', 'published_at': '2021-02-02T18:36:05Z', 'url': 'https://www.twitch.tv/videos/898263526', 'thumbnail_url': 'https://static-cdn.jtvnw.net/cf_vods/d2nvs31859zcd8/ef9971ba19bb50b945b1_c4ndygg_40965739612_1612290952//thumb/thumb0-%{width}x%{height}.jpg', 'viewable': 'public', 'view_count': 11, 'language': 'de', 'type': 'archive', 'duration': '3h35m50s'}

