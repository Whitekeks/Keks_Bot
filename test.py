import asyncio, aiohttp

async def POSTRequest(url: str, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=data) as resp:
                return resp.status

data = b"{'data': [{'game_id': '511224', 'game_name': 'Apex Legends', 'id': '40965739612', 'language': 'de', 'started_at': '2021-02-02T18:35:52Z', 'tag_ids': None, 'thumbnail_url': 'https://static-cdn.jtvnw.net/previews-ttv/live_user_c4ndygg-{width}x{height}.jpg', 'title': 'Season 8 LETS GOOOOO #TeamSalsa #Eddy #music #OpenEndGaming [Ger | Eng]', 'type': 'live', 'user_id': '246901251', 'user_login': 'c4ndygg', 'user_name': 'c4ndygg', 'viewer_count': 0}]}"
empty = b"{'data': []}"
loop = asyncio.get_event_loop()
status = loop.run_until_complete(POSTRequest("https://www.whitekeks.tk/246901251", data))
print(status)