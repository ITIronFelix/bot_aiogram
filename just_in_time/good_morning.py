from create_bot import bot
import datetime
import sqlite3


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
    dtn = datetime.datetime.now()
    time = dtn.strftime("%H:%M")

    path = 'user_profiles/847088740.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    data = cur.execute('SELECT * FROM note_today WHERE time == ? ORDER BY time ASC', (time,)).fetchall()
    base.close()
    if len(data):
        lst = [*(x for t in data for x in t)]
        i = 0
        sms = []
        while i < len(lst):
            sms.append(lst[i] + " " + lst[i + 1] + " " + lst[i + 2])
            i += 3
        await bot.send_message(847088740, sms)

