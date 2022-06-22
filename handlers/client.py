from aiogram import types, Dispatcher
from create_bot import bot
import sqlite3
import os.path
import datetime
profile_baza = {
            "name": "",
            "sex": "",
            "age": 0,
            "bahcoin": 0,
            "sig_in_day": 0,
            "sig_yesterday" : 0,
            "sig_in_week": 0,
            "sig_in_mounth": 0,
            "total_sig": 0,
            "check_profile": 0,
            "check_sig": 0,
            'check_spin': 0,
            'note_tomorrow1': "Пусто",
            'note_tomorrow2': "Пусто",
            'note_tomorrow3': "Пусто",
            'note_tomorrow4': "Пусто",
            'note_tomorrow5': "Пусто"
    }
dtn = datetime.datetime.now()

async def new_base(message : types.Message):
    path = 'user_profiles/' + str(message.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    base.execute('CREATE TABLE IF NOT EXISTS {}(id int, first_name text, last_name text, sex text, age int, sig_in_day int, bahcoin int)'.format("profile"))
    cur.execute('INSERT INTO profile VALUES(?, ?, ?, ?, ?, ?, ?)',
                (message.from_user.id, message.from_user.first_name, message.from_user.last_name, "", 0, 0, 0))
    base.execute('CREATE TABLE IF NOT EXISTS {}(date, sig_today int, sig_yesterday int, sig_in_week int, sig_in_mounth int, total_sig int)'.format("statistics"))
    cur.execute('INSERT INTO statistics VALUES(?, ?, ?, ?, ?, ?)',
                (dtn.strftime("%d-%m-%Y"), 0, 0, 0, 0, 0))
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
    a = 0
    path = 'user_profiles/' + str(message.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    r = cur.execute(f'SELECT sig_in_week FROM statistics').fetchone()
    a = int(r[0])
    a += 1
    cur.execute(f"UPDATE statistics SET sig_in_week == ? WHERE date == ?", (a, dtn.strftime("%d-%m-%Y")))
    r = cur.execute(f'SELECT sig_in_mounth FROM statistics').fetchone()
    a = int(r[0])
    a += 1
    cur.execute(f"UPDATE statistics SET sig_in_mounth == ? WHERE date == ?", (a, dtn.strftime("%d-%m-%Y")))
    r = cur.execute(f'SELECT total_sig FROM statistics').fetchone()
    a = int(r[0])
    a += 1
    cur.execute(f"UPDATE statistics SET total_sig == ? WHERE date == ?", (a, dtn.strftime("%d-%m-%Y")))
    r = cur.execute(f'SELECT sig_today FROM statistics').fetchone()
    a = int(r[0])
    a += 1
    cur.execute(f"UPDATE statistics SET sig_today == ? WHERE date == ?", (a, dtn.strftime("%d-%m-%Y")))
    base.commit()
    await message.reply(f'Сигарета учтена, вы сегодня выкурили: {a}')
    base.close()

# @dp.message_handler(commands=["start"])
async def start(message: types.Message):
    path = 'user_profiles/' + str(message.from_user.id) + '.db'
    if os.path.isfile(path) == False:
        await new_base(message)
    await bot.send_message(message.from_user.id, 'mess')




# @bot.message_handler()
async def echo_send(message : types.Message):
    if message.text == '🚬':
        await change_profile_sig_plus_one(message)

async def test (message : types.Message):
    path = 'user_profiles/' + str(message.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    cur.execute('INSERT INTO note_tomorrow(time, description) SELECT time, description FROM note_today '
                'WHERE status == ?', ('❌'))
    cur.execute('DELETE FROM note_today')
    cur.execute('INSERT INTO note_today(time, description) SELECT time, description FROM note_tomorrow')
    cur.execute('UPDATE note_today SET status == ?', ('❌'))
    cur.execute('DELETE FROM note_tomorrow')
    base.commit()
    base.close()


def register_handlers_client(dp : Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(echo_send, text = '🚬')
    dp.register_message_handler(test, commands=['test'])
