import twitter
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import pytz

PATH = os.path.dirname(os.path.abspath(__file__))
load_dotenv(f'{PATH}/TOKEN.env')
TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN_KEY = os.getenv('TWITTER_ACCESS_TOKEN_KEY')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

twitter_api = twitter.Api(consumer_key=TWITTER_CONSUMER_KEY,
				consumer_secret=TWITTER_CONSUMER_SECRET,
				access_token_key=TWITTER_ACCESS_TOKEN_KEY,
				access_token_secret=TWITTER_ACCESS_TOKEN_SECRET)

# USERS = ['@OpenEndGaming', '@foxnews', '@moooris', '@alohaarleen', '@waynemansfield', 
# '@davemalby', '@radioblogger', '@barefoot_exec', '@mike_wesely', '@ggw_bach', '@rockingjude', 
# '@chrisbrogan', '@djc8080', '@nytimes', '@guykawasaki', '@wossy', '@tyrese4real','@alyssa_milano', 
# '@officialtila', '@schofe', '@agent_m', '@estelledarlings', '@time', '@craigteich', '@judyrey', '@jeanettejoy']

# USERS = ['@foxnews']

# def main():
# 	# twitter_api.GetStreamFilter will return a generator that yields one status
# 	# message (i.e., Tweet) at a time as a JSON dictionary.
# 	for line in twitter_api.GetStreamFilter(track=USERS):
# 		# if line['id']==1325758184225583105:
# 		print(f"{line['user']['name']} writes at {line['created_at']}: {line['text']}")
# 		print('\n')

# if __name__ == '__main__':
#     main()

statuses = twitter_api.GetUserTimeline(screen_name='@OpenEndGaming', count=20)
s = statuses[0]
print(s.retweeted_status)
s = statuses[1]
print(s.retweeted_status)
# now = datetime.now()
# timezone = pytz.timezone("Europe/Berlin")
# now = timezone.localize(now)
# then = datetime.strptime(s.created_at, '%a %b %d %X %z %Y')
# print(now)
# print(then)
# print(now>then)
# print(twitter_api.GetStatusOembed(s.id))