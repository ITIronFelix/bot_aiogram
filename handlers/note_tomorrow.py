from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from create_bot import bot
from aiogram.dispatcher.filters import Text

async def note_tomorrow_show(id):
    path = 'user_profiles/' + str(id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    time = cur.execute(f'SELECT * FROM note_tomorrow ORDER BY time ASC').fetchall()
    lst = [*(x for t in time for x in t)]
    i = 0
    list = []
    if len(lst):
        while i < len(lst):
            list.append(lst[i] + " " + lst[i + 1] + " " + lst[i+2])
            i += 3
        base.close()
        await bot.send_message(id, 'Ваши планы на завтра:' + "\n\n" + "\n".join(list))
    else:
        await bot.send_message(id, 'Список пуст')


async def list_buttons_note(callback):
    path = 'user_profiles/' + str(callback.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    time = cur.execute('SELECT time, description, status FROM note_tomorrow ORDER BY time ASC').fetchall()
    lst = [*(x for t in time for x in t)]
    base.close()
    keyboard_time = InlineKeyboardMarkup()
    i = 0
    while i < len(lst):
        keyboard_time.add(InlineKeyboardButton(text=f'{lst[i]} {lst[i+1]} {lst[i+2]}', callback_data=f'{lst[i]}'))
        i += 3
    await callback.message.answer('Выберите значение', reply_markup=keyboard_time)


class FSM_note_tomorrow_add(StatesGroup):
    addtime = State()
    status_note_tomorrow = State()
    adddiscription = State()

class FSM_note_tomorrow_change(StatesGroup):
    change_choose = State()
    change_row = State()
    change_value = State()

class FSM_tomorrow_status_change(StatesGroup):
    start = State()
    finish = State()
class FSM_note_tomorrow_delete(StatesGroup):
    delete_row = State()

class FSM_note_tomorrow_sms(StatesGroup):
    sms_start = State()
    sms_change_tomorrow = State()



async def note_tomorrow(message : types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text = "Добавить запись", callback_data='add_tomorrow')
    button2 = InlineKeyboardButton(text= 'Изменить', callback_data='change_tomorrow')
    button3 = InlineKeyboardButton(text= 'Удалить', callback_data='delete_tomorrow')
    button4 = InlineKeyboardButton(text = 'Показать', callback_data='button_show_tomorrow')
    keyboard.add(button4, button1, button2, button3)
    await message.reply('Что вы хотите сделать?', reply_markup = keyboard)


async def listener_tomorrow(callback :  types.CallbackQuery):
    if callback.data =='button_show_tomorrow':
        await note_tomorrow_show(callback.from_user.id)
    elif callback.data == 'add_tomorrow':
        await FSM_note_tomorrow_add.addtime.set()
        await callback.message.answer('Введите время')
    elif callback.data == 'change_tomorrow':
        path = 'user_profiles/' + str(callback.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        time = cur.execute('SELECT time, description FROM note_tomorrow ORDER BY time ASC').fetchall()
        lst = [*(x for t in time for x in t)]
        base.close()
        if len(lst):
            await FSM_note_tomorrow_change.change_choose.set()
            keyboard_change = InlineKeyboardMarkup()
            button_change1 = InlineKeyboardButton(text = "Время", callback_data= 'time_change_tomorrow')
            button_change2 = InlineKeyboardButton(text="Описание", callback_data='description_change_tomorrow')
            button_change3 = InlineKeyboardButton(text="Статус", callback_data='status_change_tomorrow')
            keyboard_change.add(button_change1, button_change2, button_change3)
            await callback.message.answer('Вы хотите поменять время, описание или статус?', reply_markup= keyboard_change)
        else:
            await callback.message.answer('Ваш список дел на сегодня пуст')
    elif callback.data == 'delete_tomorrow':
        path = 'user_profiles/' + str(callback.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        time = cur.execute('SELECT time, description, status FROM note_tomorrow ORDER BY time ASC').fetchall()
        lst = [*(x for t in time for x in t)]
        base.close()
        if len(lst):
            keyboard_time = InlineKeyboardMarkup()
            i = 0
            while i < len(lst):
                keyboard_time.add(InlineKeyboardButton(text=f'{lst[i]} {lst[i + 1]} {lst[i+2]}', callback_data=f'{lst[i]}'))
                i += 3
            await callback.message.answer('Выберите значение', reply_markup=keyboard_time)
            await FSM_note_tomorrow_delete.delete_row.set()
        else:
            await callback.message.answer('Ваш список дел на завтра пуст')

async def add_time_tomorrow(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
    await FSM_note_tomorrow_add.next()
    await message.reply('Введите описание')

async def status_note_tomorrow(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    keyboard_status_tomorrow_y_n = InlineKeyboardMarkup()
    button_status_tomorrow_y = InlineKeyboardButton(text="Да", callback_data='sms_tomorrow_y')
    button_status_tomorrow_n = InlineKeyboardButton(text="Нет", callback_data='sms_tomorrow_n')
    keyboard_status_tomorrow_y_n.add(button_status_tomorrow_y, button_status_tomorrow_n)
    await bot.send_message(message.chat.id, 'Установить оповещение', reply_markup=keyboard_status_tomorrow_y_n)
    await FSM_note_tomorrow_add.next()

async def add_discription_tomorrow(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'sms_tomorrow_y':
        async with state.proxy() as data:
            path = 'user_profiles/' + str(callback.from_user.id) + '.db'
            base = sqlite3.connect(path)
            cur = base.cursor()
            cur.execute('INSERT INTO note_tomorrow VALUES(?, ?, ?)',
                            (data['time'], data['description'], "🕔"))
            base.commit()
            base.close()
        await state.finish()
        await note_tomorrow_show(callback.from_user.id)
    elif callback.data == 'sms_tomorrow_n':
        async with state.proxy() as data:
            path = 'user_profiles/' + str(callback.from_user.id) + '.db'
            base = sqlite3.connect(path)
            cur = base.cursor()
            cur.execute('INSERT INTO note_tomorrow VALUES(?, ?, ?)',
                                (data['time'], data['description'], '❌'))
            base.commit()
            base.close()
        await state.finish()
        await note_tomorrow_show(callback.from_user.id)
    else:
        await callback.message.answer('Жми кнопки :)')
        return

async def listener_change_tomorrow(callback : types.CallbackQuery, state: FSMContext):
    if callback.data == 'time_change_tomorrow':
        async with state.proxy() as data:
            data['choose'] = 'time'
        await list_buttons_note(callback)
        await FSM_note_tomorrow_change.next()
    elif callback.data == 'description_change_tomorrow':
        async with state.proxy() as data:
            data['choose'] = 'description'
        await list_buttons_note(callback)
        await FSM_note_tomorrow_change.next()
    elif callback.data == 'status_change_tomorrow':
        async with state.proxy() as data:
            data['choose'] = 'status'
        await state.finish()
        await list_buttons_note(callback)
        await FSM_tomorrow_status_change.start.set()



async def change_row_tomorrow(callback : types.CallbackQuery, state: FSMContext):
    # path = 'user_profiles/' + str(callback.from_user.id) + '.db'
    # base = sqlite3.connect(path)
    # cur = base.cursor()
    # time = cur.execute('SELECT time FROM note_tomorrow').fetchall()
    # base.close()
    # lst = [*(x for t in time for x in t)]
    # if callback.data not in lst:
    #     await callback.message.answer("Жми кнопки :)")
    #     return
    # else:
    async with state.proxy() as data:
        if data['choose'] == 'time' or data['choose'] == 'description':
            data['old_value'] = callback.data
            await callback.message.answer("Введите новые данные")
            await FSM_note_tomorrow_change.next()


async def change_value_tomorrow(message : types.Message, state : FSMContext):
    async with state.proxy() as data:
        data['new_value'] = message.text
    async with state.proxy() as data:
        path = 'user_profiles/' + str(message.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        cur.execute(f"UPDATE note_tomorrow SET {data['choose']} == ? WHERE time == ?", (data['new_value'], data['old_value']))
        base.commit()
        base.close()
    await state.finish()
    await bot.send_message(message.chat.id, 'Данные обновлены')
    await note_tomorrow_show(message.from_user.id)

async def change_status_listener(callback : types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["old_value"] = callback.data
    keyboard_change = InlineKeyboardMarkup()
    button_change1 = InlineKeyboardButton(text='✅', callback_data='✅')
    button_change2 = InlineKeyboardButton(text='🕔', callback_data='🕔')
    button_change3 = InlineKeyboardButton(text='❌', callback_data='❌')
    keyboard_change.add(button_change1, button_change2, button_change3)
    await callback.message.answer('Выберете статус?', reply_markup=keyboard_change)
    await FSM_tomorrow_status_change.next()

async def change_status_finisher(callback : types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["new_value"] = callback.data
        path = 'user_profiles/' + str(callback.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        cur.execute(f"UPDATE note_tomorrow SET status == ? WHERE time == ?",
                    (data['new_value'], data['old_value']))
        base.commit()
        base.close()
    await state.finish()
    await callback.message.answer('Данные обновлены')
    await note_tomorrow_show(callback.from_user.id)


async def row_delete_tomorrow(callback : types.CallbackQuery, state: FSMContext):
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
        await note_tomorrow_show(callback.from_user.id)





async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено")

def register_handlers_note_tomorrow(dp : Dispatcher):
    dp.register_message_handler(note_tomorrow, commands=['note_tomorrow'])
    dp.register_callback_query_handler(listener_tomorrow, lambda call: call.data == 'add_tomorrow' or call.data == "change_tomorrow" or call.data == "delete_tomorrow" or call.data == "button_show_tomorrow")

    dp.register_message_handler(add_time_tomorrow, state=FSM_note_tomorrow_add.addtime)
    dp.register_message_handler(status_note_tomorrow, state=FSM_note_tomorrow_add.status_note_tomorrow)
    dp.register_callback_query_handler(add_discription_tomorrow, state=FSM_note_tomorrow_add.adddiscription)

    dp.register_callback_query_handler(listener_change_tomorrow, state=FSM_note_tomorrow_change.change_choose)
    dp.register_callback_query_handler(change_row_tomorrow, state=FSM_note_tomorrow_change.change_row)
    dp.register_message_handler(change_value_tomorrow, state=FSM_note_tomorrow_change.change_value)

    dp.register_callback_query_handler(change_status_listener, state=FSM_tomorrow_status_change.start)
    dp.register_callback_query_handler(change_status_finisher, state=FSM_tomorrow_status_change.finish)

    dp.register_callback_query_handler(row_delete_tomorrow, state=FSM_note_tomorrow_delete.delete_row)

    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")