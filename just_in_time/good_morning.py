from create_bot import bot
import datetime
import sqlite3
import os.path
from os import path

async def hello():
    dtn = datetime.datetime.now()
    date = dtn.strftime("%d.%m.%Y")

    path = 'user_profiles/847088740.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    time = cur.execute('SELECT * FROM note_today ORDER BY time ASC').fetchall()
    lst = [*(x for t in time for x in t)]
    i = 0
    list = []
    while i < len(lst):
        list.append(lst[i] + " " + lst[i + 1] + " " + lst[i + 2])
        i += 3

    base.close()
    mess = "Доброе утро! Сегодня " + date + "\n" +'Ваши задачи сегодня:' + "\n\n" + "\n".join(list)
    await bot.send_message(847088740, mess)

async def sing():
    for filename in os.listdir("user_profiles"):
        if path.splitext(filename)[1] == '.db':
            dtn = datetime.datetime.now()
            time = dtn.strftime("%H:%M")
            path1 = 'user_profiles/' + filename
            chat = path.splitext(filename)[0]
            base = sqlite3.connect(path1)
            cur = base.cursor()
            data = cur.execute('SELECT * FROM note_today WHERE time == ? AND status == ? ORDER BY time ASC', (time, '🕔')).fetchall()
            if len(data):
                cur.execute(f"UPDATE note_today SET status == ? WHERE time == ? AND status == ?", ('❌', time, '🕔'))
                base.commit()
                lst = [*(x for t in data for x in t)]
                i = 0
                sms = []
                while i < len(lst):
                    sms.append(lst[i] + " " + lst[i + 1] + " " + lst[i + 2])
                    i += 3
                await bot.send_message(chat, f'Напоминание! \n {sms[0]}')
            base.close()


async def note_swap():
    for filename in os.listdir("user_profiles"):
        if path.splitext(filename)[1] == '.db':
            path1 = 'user_profiles/' + filename
            base = sqlite3.connect(path1)
            cur = base.cursor()
            cur.execute('INSERT INTO note_tomorrow(time, description, status) SELECT time, description, status FROM note_today '
                        'WHERE status == ?', ('❌'))
            cur.execute('DELETE FROM note_today')
            cur.execute('INSERT INTO note_today(time, description, status) SELECT time, description, status FROM note_tomorrow')
            cur.execute('DELETE FROM note_tomorrow')
            base.commit()
            base.close()