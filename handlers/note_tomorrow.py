from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from create_bot import bot
from handlers.client import note_tomorrow_show
from aiogram.dispatcher.filters import Text

class FSM_note_tommorow_add(StatesGroup):
    addtime = State()
    adddiscription = State()

class FSM_note_tommorow_change(StatesGroup):
    change_choose = State()
    change_row = State()
    change_value = State()

class FSM_note_tommorow_delete(StatesGroup):
    delete_row = State()




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
        path = 'user_profiles/' + str(callback.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        time = cur.execute('SELECT time, description FROM note_tomorrow ORDER BY time ASC').fetchall()
        lst = [*(x for t in time for x in t)]
        base.close()
        if len(lst):
            await FSM_note_tommorow_change.change_choose.set()
            keyboard_change = InlineKeyboardMarkup()
            button_change1 = InlineKeyboardButton(text = "Время", callback_data= 'time_change')
            button_change2 = InlineKeyboardButton(text="Описание", callback_data='description_change')
            keyboard_change.add(button_change1, button_change2)
            await callback.message.answer('Вы хотите поменять время или описание?', reply_markup= keyboard_change)
        else:
            await callback.message.answer('Ваш список дел на завтра пуст')
    elif callback.data == 'delete':
        path = 'user_profiles/' + str(callback.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        time = cur.execute('SELECT time, description FROM note_tomorrow ORDER BY time ASC').fetchall()
        lst = [*(x for t in time for x in t)]
        base.close()
        if len(lst):
            keyboard_time = InlineKeyboardMarkup()
            i = 0
            while i < len(lst):
                keyboard_time.add(InlineKeyboardButton(text=f'{lst[i]} {lst[i + 1]}', callback_data=f'{lst[i]}'))
                i += 2
            await callback.message.answer('Выберите значение', reply_markup=keyboard_time)
            await FSM_note_tommorow_delete.delete_row.set()
        else:
            await callback.message.answer('Ваш список дел на завтра пуст')

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
    await note_tomorrow_show(message)

#block change
async def listener_change(callback : types.CallbackQuery, state: FSMContext):
    if callback.data == 'time_change':
        async with state.proxy() as data:
            data['choose'] = 'time'
    elif callback.data == 'description_change':
        async with state.proxy() as data:
            data['choose'] = 'description'
    await FSM_note_tommorow_change.next()
    path = 'user_profiles/' + str(callback.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    time = cur.execute('SELECT time, description FROM note_tomorrow ORDER BY time ASC').fetchall()
    lst = [*(x for t in time for x in t)]
    base.close()
    keyboard_time = InlineKeyboardMarkup()
    i = 0
    while i < len(lst):
        keyboard_time.add(InlineKeyboardButton(text=f'{lst[i]} {lst[i+1]}', callback_data=f'{lst[i]}'))
        i += 2
    await callback.message.answer('Выберите значение', reply_markup=keyboard_time)


async def change_row(callback : types.CallbackQuery, state: FSMContext):
    path = 'user_profiles/' + str(callback.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    time = cur.execute('SELECT time FROM note_tomorrow').fetchall()
    base.close()
    lst = [*(x for t in time for x in t)]
    if callback.data not in lst:
        await callback.message.answer("Жми кнопки :)")
        return
    else:
        async with state.proxy() as data:
            data['old_value'] = callback.data
        await callback.message.answer("Введите новые данные")
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
            base.close()
    await state.finish()
    await note_tomorrow_show(message)

async def row_delete(callback : types.CallbackQuery, state: FSMContext):
    path = 'user_profiles/' + str(callback.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    time = cur.execute('SELECT time FROM note_tomorrow').fetchall()
    base.close()
    lst = [*(x for t in time for x in t)]
    if callback.data not in lst:
        await callback.message.answer("Жми кнопки :)")
        return
    else:
        async with state.proxy() as data:
            data["row"] = callback.data
        async with state.proxy() as data:
            path = 'user_profiles/' + str(callback.from_user.id) + '.db'
            base = sqlite3.connect(path)
            cur = base.cursor()
            cur.execute(f"DELETE from note_tomorrow WHERE time == ?", (data['row'],))
            base.commit()
            base.close()
        await state.finish()
        await callback.message.answer('Запись удалена')

async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено")








def register_handlers_note_tomorrow(dp : Dispatcher):
    dp.register_message_handler(note_tomorrow, commands=['plans_change'])
    dp.register_callback_query_handler(listener, lambda call: call.data == 'add' or call.data == "change" or call.data == "delete")
    dp.register_message_handler(add_time, state=FSM_note_tommorow_add.addtime)
    dp.register_message_handler(add_discription, state=FSM_note_tommorow_add.adddiscription)
    dp.register_callback_query_handler(listener_change, state= FSM_note_tommorow_change.change_choose)
    dp.register_callback_query_handler(change_row, state = FSM_note_tommorow_change.change_row)
    dp.register_message_handler(change_value, state=FSM_note_tommorow_change.change_value)
    dp.register_callback_query_handler(row_delete, state=FSM_note_tommorow_delete.delete_row)
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")