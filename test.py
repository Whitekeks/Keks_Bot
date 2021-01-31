import asyncio, aiohttp

async def POSTRequest(url: str, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=data) as resp:
                return resp.status

data = b"{'data': [{'game_id': '', 'game_name': '', 'id': '40942377596', 'language': 'en', 'started_at': '2021-01-31T17:22:13Z', 'tag_ids': None, 'thumbnail_url': 'https://static-cdn.jtvnw.net/previews-ttv/live_user_whitekeks-{width}x{height}.jpg', 'title': 'Titel', 'type': 'live', 'user_id': '410772114', 'user_login': 'whitekeks', 'user_name': 'Whitekeks', 'viewer_count': 0}]}"
empty = b"{'data': []}"
loop = asyncio.get_event_loop()
status = loop.run_until_complete(POSTRequest("https://www.whitekeks.tk/410772114", empty))
print(status)