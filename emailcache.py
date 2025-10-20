import json
import sqlite3
import time
from wsgiref import headers

DB_NAME = "C:\\Users\\wumar\\Desktop\\Personal Codes\\SimpleMCPServer\\data\\email_cache.db"

def init_cache():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (id TEXT PRIMARY KEY, sender TEXT, subject TEXT, body TEXT, time INT)''')
    c.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, last_refreshed TIMESTAMP)")
    conn.commit()
    conn.close()

def add_to_cache(messages):
    init_cache()
    conn = sqlite3.connect(DB_NAME)
    for message in messages:
        conn.execute("INSERT OR IGNORE INTO emails VALUES (?, ?, ?, ?, ?)", (message[0],message[1],message[2],message[3],message[4]))
    conn.commit()
    conn.execute("REPLACE INTO meta VALUES (?, ?)", ("last_refreshed", int(time.time())))
    conn.close()

def get_last_refreshed():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT last_refreshed FROM meta WHERE key = 'last_refreshed'")
    last_refreshed = c.fetchone()
    conn.close()
    if last_refreshed:
        return last_refreshed[0]
    return -1

def get_all_emails():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM emails")
    emails = c.fetchall()
    conn.close()
    return emails
def prune_cache():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("DELETE FROM emails WHERE time < ?", (int(time.time()) - 86400,))
    conn.commit()
    conn.close()