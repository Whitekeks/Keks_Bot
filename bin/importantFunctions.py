import time

STDPREFIX = "/"

class CustomError(Exception):
	pass

def s(dirtyString):
	cleanString = None
	if dirtyString:
		cleanString = dirtyString.translate({ord(i): None for i in [";", '"', "'", "\\"]})
	return cleanString

def sleep(Interval, Condition=True):
	time_1 = time.time()
	while time.time()-time_1 < Interval and Condition:
		None

async def send_private(member, message=None, embed=None):
	DM = await member.create_dm()
	return await DM.send(content=message, embed=embed)