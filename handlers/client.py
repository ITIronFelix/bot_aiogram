from aiogram import types, Dispatcher
from create_bot import bot
import sqlite3
import os.path
import datetime

dtn = datetime.datetime.now()



async def new_base(message : types.Message):
    path = 'user_profiles/' + str(message.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    base.execute('CREATE TABLE IF NOT EXISTS {}(id int, first_name text, last_name text, sex text, age int, sig_in_day int, bahcoin int)'.format("profile"))
    cur.execute('INSERT INTO profile VALUES(?, ?, ?, ?, ?, ?, ?)',
                (message.from_user.id, message.from_user.first_name, message.from_user.last_name, "", 0, 0, 0))
    base.execute('CREATE TABLE IF NOT EXISTS {}(date_full, date_day, date_mounth, date_year, sig_today int, total_sig int)'.format("statistics_sig"))
    cur.execute('INSERT INTO statistics_sig VALUES(?, ?, ?, ?, ?, ?)',
                (dtn.strftime("%d.%m.%Y"), dtn.strftime("%d"), dtn.strftime("%m"), dtn.strftime("%y"), 0, 0))
    base.execute('CREATE TABLE IF NOT EXISTS {}(check_profile int, check_keyboard int)'.format("checks"))
    cur.execute('INSERT INTO checks VALUES(?, ?)',
                (0, 0))
    base.execute('CREATE TABLE IF NOT EXISTS {}(time, description, status)'.format("note_tomorrow"))
    base.execute('CREATE TABLE IF NOT EXISTS {}(time, description, status)'.format("note_today"))
    base.commit()
    base.close()

async def check(message : types.Message, column):
    path = 'user_profiles/' + str(message.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    r = cur.execute(f'SELECT {column} FROM checks').fetchone()
    base.close()
    if r[0] == 1:
        return True
    else:
        return False

async def change_profile(message : types.Message, table, column, value):
    path = 'user_profiles/' + str(message.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    cur.execute(f"UPDATE {table} SET {column} == ?", (value))
    base.commit()
    base.close()

async def change_profile_sig_plus_one(message : types.Message):
    path = 'user_profiles/' + str(message.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    r = cur.execute('SELECT sig_today FROM statistics_sig WHERE date_full == ?', (dtn.strftime("%d.%m.%Y"),)).fetchall()
    lst = [*(x for t in r for x in t)]
    if len(lst) == False:
        r = cur.execute('SELECT total_sig FROM statistics_sig ORDER BY date_full DESC').fetchone()
        cur.execute('INSERT INTO statistics_sig VALUES(?, ?, ?, ?, ?, ?)',
                    (dtn.strftime("%d.%m.%Y"), dtn.strftime("%d"), dtn.strftime("%m"), dtn.strftime("%y"), 0, r[0]))
        base.commit()
    r = cur.execute('SELECT sig_today, total_sig FROM statistics_sig WHERE date_full == ?', (dtn.strftime("%d.%m.%Y"),)).fetchall()
    a = int(r[0][0])
    b = int(r[0][1])
    a += 1
    b += 1
    cur.execute(f"UPDATE statistics_sig SET sig_today == ? WHERE date_full == ?", (a, dtn.strftime("%d.%m.%Y")))
    cur.execute(f"UPDATE statistics_sig SET total_sig == ? WHERE date_full == ?", (b, dtn.strftime("%d.%m.%Y")))
    base.commit()
    await message.reply(f'Сигарета учтена, вы сегодня выкурили: {a}')
    base.close()

async def otmena_sig(message : types.Message):
    path = 'user_profiles/' + str(message.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    r = cur.execute('SELECT sig_today FROM statistics_sig WHERE date_full == ?', (dtn.strftime("%d.%m.%Y"),)).fetchall()
    lst = [*(x for t in r for x in t)]
    if len(lst) == False:
        r = cur.execute('SELECT total_sig FROM statistics_sig ORDER BY date_full DESC').fetchone()
        cur.execute('INSERT INTO statistics_sig VALUES(?, ?, ?, ?, ?, ?)',
                    (dtn.strftime("%d.%m.%Y"), dtn.strftime("%d"), dtn.strftime("%m"), dtn.strftime("%y"), 0, r[0]))
        base.commit()
    r = cur.execute('SELECT sig_today, total_sig FROM statistics_sig WHERE date_full == ?', (dtn.strftime("%d.%m.%Y"),)).fetchall()
    a = int(r[0][0])
    b = int(r[0][1])
    a -= 1
    b -= 1
    cur.execute(f"UPDATE statistics_sig SET sig_today == ? WHERE date_full == ?", (a, dtn.strftime("%d.%m.%Y")))
    cur.execute(f"UPDATE statistics_sig SET total_sig == ? WHERE date_full == ?", (b, dtn.strftime("%d.%m.%Y")))
    base.commit()
    await message.reply(f'Сигарета учтена, вы сегодня выкурили: {a}')
    base.close()


# @dp.message_handler(commands=["start"])
async def start(message: types.Message):
    path = 'user_profiles/' + str(message.from_user.id) + '.db'
    if os.path.isfile(path) == False:
        await new_base(message)
    with open('texts/start.txt', 'r', encoding= 'UTF-8') as file:
        mess = file.read()
    await bot.send_message(message.from_user.id, mess)

async def note_info(message : types.Message):
    with open('texts/start.txt', 'r', encoding= 'UTF-8') as file:
        mess = file.read()
    await bot.send_message(message.chat.id, mess)

async def otmena_sig(message : types.Message):
    path = 'user_profiles/' + str(message.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    r = cur.execute('SELECT sig_today FROM statistics_sig WHERE date_full == ?', (dtn.strftime("%d.%m.%Y"),)).fetchall()
    lst = [*(x for t in r for x in t)]
    if len(lst) == False:
        r = cur.execute('SELECT total_sig FROM statistics_sig ORDER BY date_full DESC').fetchone()
        cur.execute('INSERT INTO statistics_sig VALUES(?, ?, ?, ?, ?, ?)',
                    (dtn.strftime("%d.%m.%Y"), dtn.strftime("%d"), dtn.strftime("%m"), dtn.strftime("%y"), 0, r[0]))
        base.commit()
    r = cur.execute('SELECT sig_today, total_sig FROM statistics_sig WHERE date_full == ?', (dtn.strftime("%d.%m.%Y"),)).fetchall()
    a = int(r[0][0])
    b = int(r[0][1])
    a -= 1
    b -= 1
    cur.execute(f"UPDATE statistics_sig SET sig_today == ? WHERE date_full == ?", (a, dtn.strftime("%d.%m.%Y")))
    cur.execute(f"UPDATE statistics_sig SET total_sig == ? WHERE date_full == ?", (b, dtn.strftime("%d.%m.%Y")))
    base.commit()
    await message.reply(f'Сигарета вычтена, вы сегодня выкурили: {a}')
    base.close()

async def show_statistics_sig(message: types.Message):
    sig_mounth = 0
    sig_week = 0
    path = 'user_profiles/' + str(message.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    today = cur.execute('SELECT sig_today FROM statistics_sig WHERE date_full == ?', (dtn.strftime("%d.%m.%Y"),)).fetchone()
    total_sig = cur.execute('SELECT total_sig FROM statistics_sig ORDER BY date_full DESC').fetchone()
    data = cur.execute('SELECT sig_today FROM statistics_sig WHERE date_mounth == ?', (dtn.strftime("%m"),)).fetchall()
    lst = [*(x for t in data for x in t)]
    for item in lst:
        sig_mounth += int(item)
    data = cur.execute('SELECT sig_today FROM statistics_sig ORDER BY sig_today ASC').fetchmany(7)
    lst = [*(x for t in data for x in t)]
    for item in lst:
        sig_week += int(item)
    mess = f"Ваша статистика выкуренных сигарет:\n" \
           f"Сигарет за сегодня: {today[0]}\n" \
           f"Сигарет за последние 7 дней: {sig_week}\n" \
           f"Сигарет за этот месяц: {sig_mounth}\n" \
           f"Cигарет всего: {total_sig[0]}"
    await bot.send_message(message.chat.id, mess)


async def echo_send(message : types.Message):
    if message.text == '🚬':
        await change_profile_sig_plus_one(message)



async def test(message : types.Message):
    await bot.send_message(message.chat.id, message.from_user.id)


def register_handlers_client(dp : Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(note_info, commands=['note_info'])
    dp.register_message_handler(show_statistics_sig, commands=['statistics_sig'])
    dp.register_message_handler(otmena_sig, commands=['otmena_sig'])
    dp.register_message_handler(echo_send, text = '🚬')
    dp.register_message_handler(test, commands=['test'])
