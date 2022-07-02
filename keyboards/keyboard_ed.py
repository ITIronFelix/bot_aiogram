from aiogram import types, Dispatcher
from create_bot import bot
import sqlite3



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

async def keybord_sig_tasks_plans_change(message : types.Message):
    if await check(message, 'check_keyboard') == False:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard= True)
        button1 = types.KeyboardButton("🚬")
        button2 = types.KeyboardButton('/statistics_sig')
        button3 = types.KeyboardButton('/note_today')
        button4 = types.KeyboardButton('/note_tomorrow')
        keyboard.add(button1, button2, button3, button4)
        await bot.send_message(message.chat.id, "Клавиатура подключена", reply_markup= keyboard)
        await change_profile(message, 'checks', 'check_keyboard', "1")
    elif await check(message, 'check_keyboard') == True:
        await change_profile(message, 'checks', 'check_keyboard', "0")
        await bot.send_message(message.chat.id, 'Кнопка отключена', reply_markup=types.ReplyKeyboardRemove())

async def siga(message : types.Message):
    if await check(message, 'check_keyboard') == False:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        knopka = types.KeyboardButton("🚬")
        keyboard.add(knopka)
        await bot.send_message(message.chat.id, 'Нажми на кнопку, когда покуришь', reply_markup = keyboard)
        await change_profile(message, 'checks', 'check_keyboard', "1")
    elif await check(message, 'check_keyboard') == True:
        await change_profile(message, 'checks', 'check_keyboard', "0")
        await bot.send_message(message.chat.id, 'Кнопка отключена', reply_markup=types.ReplyKeyboardRemove())



def register_handlers_keyboard_ed(dp : Dispatcher):
    dp.register_message_handler(keybord_sig_tasks_plans_change, commands=["Keyboard"])
    dp.register_message_handler(siga, commands=['sig'])