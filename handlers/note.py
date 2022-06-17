from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from create_bot import bot


class FSM_note_tommorow_add(StatesGroup):
    addtime = State()
    adddiscription = State()

class FSM_note_tommorow_change(StatesGroup):
    change_choose = State()
    change_row = State()
    change_value = State()

async def note_tomorrow(message : types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text = "Добавить запись", callback_data='add')
    button2 = InlineKeyboardButton(text= 'Изменить', callback_data='change')
    button3 = InlineKeyboardButton(text= 'Удалить', callback_data='delete')
    keyboard.add(button1, button2, button3)
    await message.reply('Что вы хотите сделать?', reply_markup = keyboard)



# @dp.callback_query_handler(text = 'add')
async def listener(callback :  types.CallbackQuery):
    if callback.data == 'add':
        await FSM_note_tommorow_add.addtime.set()
        await callback.message.answer('Введите время')
    elif callback.data == 'change':
        await FSM_note_tommorow_change.change_choose.set()
        keyboard_change = InlineKeyboardMarkup()
        button_change1 = InlineKeyboardButton(text = "Время", callback_data= 'time_change')
        button_change2 = InlineKeyboardButton(text="Описание", callback_data='description_change')
        keyboard_change.add(button_change1, button_change2)
        await callback.message.answer('Вы хотите поменять время или описание?', reply_markup= keyboard_change)
    elif callback.data == 'delete':
        keyboard_delete = InlineKeyboardMarkup()
        button_delete1 = InlineKeyboardButton(text="knopka", callback_data='delete_query')
        keyboard_delete.add(button_delete1)
        await callback.message.answer('some text?', reply_markup=keyboard_delete)

#block add
async def add_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
    await FSM_note_tommorow_add.next()
    await message.reply('Введите описание')

async def add_discription(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    async with state.proxy() as data:
        await bot.send_message(message.chat.id, 'Данные добавлены')
        path = 'user_profiles/' + str(message.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        cur.execute('INSERT INTO note_tomorrow VALUES(?, ?)',
                    (data['time'], data['description']))
        base.commit()
        time = cur.execute('SELECT * FROM note_tomorrow ORDER BY time ASC').fetchall()
        lst = [*(x for t in time for x in t)]
        i = 0
        list = []
        while i < len(lst):
            list.append(lst[i] + " " + lst[i + 1])
            i += 2
        base.close()
    await state.finish()
    await bot.send_message(message.chat.id, "\n".join(list))

#block change
async def listener_change(callback : types.CallbackQuery, state: FSMContext):
    if callback.data == 'time_change':
        async with state.proxy() as data:
            data['choose'] = 'time'
    elif callback.data == 'description_change':
        async with state.proxy() as data:
            data['choose'] = 'description'
    await FSM_note_tommorow_change.next()
    await callback.message.answer('Введите время записи, которую хотите изменить')


async def change_row(message : types.Message, state: FSMContext):
    path = 'user_profiles/' + str(message.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    time = cur.execute('SELECT time FROM note_tomorrow').fetchall()
    base.close()
    lst = [*(x for t in time for x in t)]
    if message.text not in lst:
        await message.answer("Записи с таким времени, введите корректное время")
        return
    else:
        async with state.proxy() as data:
            data['old_value'] = message.text
        await bot.send_message(message.chat.id, "Введите новые данные")
        await FSM_note_tommorow_change.next()

async def change_value(message : types.Message, state : FSMContext):
    async with state.proxy() as data:
        data['new_value'] = message.text
    async with state.proxy() as data:
            await bot.send_message(message.chat.id, 'Данные обновлены')
            path = 'user_profiles/' + str(message.from_user.id) + '.db'
            base = sqlite3.connect(path)
            cur = base.cursor()
            cur.execute(f"UPDATE note_tomorrow SET {data['choose']} == ? WHERE time == ?", (data['new_value'], data['old_value']))
            base.commit()
            time = cur.execute('SELECT * FROM note_tomorrow ORDER BY time ASC').fetchall()
            lst = [*(x for t in time for x in t)]
            i = 0
            list = []
            while i < len(lst):
                list.append(lst[i] + " " + lst[i + 1])
                i += 2
            base.close()
    await state.finish()
    await bot.send_message(message.chat.id, "\n".join(list))

async def listener_delete(callback : types.CallbackQuery, state: FSMContext):
    await callback.message.answer('rab')








def register_handlers_note(dp : Dispatcher):
    dp.register_message_handler(note_tomorrow, commands=['note'])
    dp.register_callback_query_handler(listener, lambda call: call.data == 'add' or call.data == "change" or call.data == "delete")
    dp.register_message_handler(add_time, state=FSM_note_tommorow_add.addtime)
    dp.register_message_handler(add_discription, state=FSM_note_tommorow_add.adddiscription)
    dp.register_callback_query_handler(listener_change, state= FSM_note_tommorow_change.change_choose)
    dp.register_message_handler(change_row, state = FSM_note_tommorow_change.change_row)
    dp.register_message_handler(change_value, state=FSM_note_tommorow_change.change_value)
    dp.register_callback_query_handler(listener_delete, lambda call: call.data == 'delete_query')
