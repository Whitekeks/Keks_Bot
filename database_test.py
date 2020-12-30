# import sqlite3
from mysql import connector
import unicodedata
import os

# PATH = os.path.dirname(os.path.abspath(__file__))
# conn = sqlite3.connect(database=f"{PATH}/funniest/End_Bot.db")
# cursor = conn.cursor()
myconn = connector.connect(
	host="localhost",
	user="root",
	password="Ludado80",
	database='Open_End'
)
mycursor = myconn.cursor()


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
mycursor.execute('SELECT _id FROM members WHERE _regist<>0')
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

# conn.commit()

# conn.close()
myconn.close()
