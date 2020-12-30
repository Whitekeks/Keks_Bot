import sqlite3
from mysql import connector
import unicodedata
import os

def s(dirtyString):
	cleanString = None
	if dirtyString:
		cleanString = dirtyString.translate({ord(i): None for i in ["'", '"', ";", ",", "(", ")", "{", "}", "[", "]"]})
	return cleanString

PATH = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(database=f"{PATH}/End_Bot.db")
cursor = conn.cursor()
myconn = connector.connect(
	host="localhost",
	user="Whitekeks",
	password="Ludado80",
	database='Open_End'
)
mycursor = myconn.cursor()

#create database
mycursor.execute('CREATE TABLE IF NOT EXISTS guilds (_id BIGINT, _name TEXT, _prefix TEXT, _news BIGINT, _creation_time TEXT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
mycursor.execute('CREATE TABLE IF NOT EXISTS members (_id BIGINT, _name TEXT, _nick TEXT, _guild BIGINT, _regist BIGINT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
mycursor.execute('CREATE TABLE IF NOT EXISTS twitter (_rank BIGINT, _id BIGINT, _created_at TEXT, _send BOOL, _retweet BOOL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
mycursor.execute('CREATE TABLE IF NOT EXISTS bot (_key DOUBLE, _creation_time TEXT, _guild BIGINT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;')
myconn.commit()

#copy Open_End.db
#guilds
for row in cursor.execute('SELECT * FROM guilds'):
	mycursor.execute(f'INSERT INTO guilds VALUES ({row[0]},"{s(row[1])}","{s(row[2])}",{row[3]},"{s(row[4])}")')
conn.commit()
#members
for row in cursor.execute('SELECT * FROM members'):
	mycursor.execute(f'INSERT INTO members VALUES ({row[0]},"{s(row[1])}","{s(row[2])}",{row[3]},{row[4]})')
conn.commit()
#twitter
for row in cursor.execute('SELECT * FROM twitter'):
	mycursor.execute(f'INSERT INTO twitter VALUES ({row[0]},{row[1]},"{s(row[2])}",{row[3]},{row[4]})')
conn.commit()
#bot
for row in cursor.execute('SELECT * FROM bot'):
	mycursor.execute(f'INSERT INTO bot VALUES ({row[0]},"{s(row[1])}",{row[2]})')
conn.commit()
myconn.commit()

# cursor.execute('UPDATE guilds SET creation_time="Tue Oct 27 19:55:00 +0000 2020" WHERE name="DEBUG_SERVER"')
# cursor.execute('UPDATE twitter SET send=0')

# print("members:")
# for j in cursor.execute('SELECT id, name FROM members WHERE regist!=0'):
# 	print(j)
# print("guilds:")
# for i in cursor.execute('SELECT * FROM guilds'):
# 	print(i)
# print("bot:")
# for i in cursor.execute('SELECT * FROM bot'):
# 	print(i)
# print("twitter:")
# cursor.execute('SELECT * FROM twitter')
# List = cursor.fetchall()
# print(List)
# for i in List:
# 	print(i)

print("members:")
mycursor.execute('SELECT * FROM members WHERE _regist<>0')
List = mycursor.fetchall()
for i in List:
	print(i)

print("guilds:")
mycursor.execute('SELECT * FROM guilds')
List = mycursor.fetchall()
for i in List:
	print(i)

print("bot:")
mycursor.execute('SELECT * FROM bot')
List = mycursor.fetchall()
for i in List:
	print(i)

print("twitter:")
mycursor.execute('SELECT * FROM twitter')
List = mycursor.fetchall()
for i in List:
	print(i)

conn.close()
myconn.close()
