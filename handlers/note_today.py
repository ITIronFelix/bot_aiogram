from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from create_bot import bot
from aiogram.dispatcher.filters import Text

async def note_today_show(id):
    path = 'user_profiles/' + str(id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    time = cur.execute(f'SELECT * FROM note_today ORDER BY time ASC').fetchall()
    lst = [*(x for t in time for x in t)]
    i = 0
    list = []
    if len(lst):
        while i < len(lst):
            list.append(lst[i] + " " + lst[i + 1] + " " + lst[i+2])
            i += 3
        base.close()
        await bot.send_message(id, 'Ваши задачи сегодня:' + "\n\n" + "\n".join(list))
    else:
        await bot.send_message(id, 'Список пуст')


async def list_buttons_note(callback):
    path = 'user_profiles/' + str(callback.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    time = cur.execute('SELECT time, description, status FROM note_today ORDER BY time ASC').fetchall()
    lst = [*(x for t in time for x in t)]
    base.close()
    keyboard_time = InlineKeyboardMarkup()
    i = 0
    while i < len(lst):
        keyboard_time.add(InlineKeyboardButton(text=f'{lst[i]} {lst[i+1]} {lst[i+2]}', callback_data=f'{lst[i]}'))
        i += 3
    await callback.message.answer('Выберите значение', reply_markup=keyboard_time)


class FSM_note_today_add(StatesGroup):
    addtime = State()
    status_note_today = State()
    adddiscription = State()

class FSM_note_today_change(StatesGroup):
    change_choose = State()
    change_row = State()
    change_value = State()

class FSM_today_status_change(StatesGroup):
    start = State()
    finish = State()
class FSM_note_today_delete(StatesGroup):
    delete_row = State()

class FSM_note_today_sms(StatesGroup):
    sms_start = State()
    sms_change_today = State()



async def note_today(message : types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text = "Добавить запись", callback_data='add_today')
    button2 = InlineKeyboardButton(text= 'Изменить', callback_data='change_today')
    button3 = InlineKeyboardButton(text= 'Удалить', callback_data='delete_today')
    button4 = InlineKeyboardButton(text = 'Показать', callback_data='button_show_today')
    keyboard.add(button4, button1, button2, button3)
    await message.reply('Что вы хотите сделать?', reply_markup = keyboard)


async def listener_today(callback :  types.CallbackQuery):
    if callback.data =='button_show_today':
        await note_today_show(callback.from_user.id)
    elif callback.data == 'add_today':
        await FSM_note_today_add.addtime.set()
        await callback.message.answer('Введите время')
    elif callback.data == 'change_today':
        path = 'user_profiles/' + str(callback.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        time = cur.execute('SELECT time, description FROM note_today ORDER BY time ASC').fetchall()
        lst = [*(x for t in time for x in t)]
        base.close()
        if len(lst):
            await FSM_note_today_change.change_choose.set()
            keyboard_change = InlineKeyboardMarkup()
            button_change1 = InlineKeyboardButton(text = "Время", callback_data= 'time_change_today')
            button_change2 = InlineKeyboardButton(text="Описание", callback_data='description_change_today')
            button_change3 = InlineKeyboardButton(text="Статус", callback_data='status_change_today')
            keyboard_change.add(button_change1, button_change2, button_change3)
            await callback.message.answer('Вы хотите поменять время, описание или статус?', reply_markup= keyboard_change)
        else:
            await callback.message.answer('Ваш список дел на сегодня пуст')
    elif callback.data == 'delete_today':
        path = 'user_profiles/' + str(callback.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        time = cur.execute('SELECT time, description, status FROM note_today ORDER BY time ASC').fetchall()
        lst = [*(x for t in time for x in t)]
        base.close()
        if len(lst):
            keyboard_time = InlineKeyboardMarkup()
            i = 0
            while i < len(lst):
                keyboard_time.add(InlineKeyboardButton(text=f'{lst[i]} {lst[i + 1]} {lst[i+2]}', callback_data=f'{lst[i]}'))
                i += 3
            await callback.message.answer('Выберите значение', reply_markup=keyboard_time)
            await FSM_note_today_delete.delete_row.set()
        else:
            await callback.message.answer('Ваш список дел на завтра пуст')

async def add_time_today(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
    await FSM_note_today_add.next()
    await message.reply('Введите описание')

async def status_note_today(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    keyboard_status_today_y_n = InlineKeyboardMarkup()
    button_status_today_y = InlineKeyboardButton(text="Да", callback_data='sms_today_y')
    button_status_today_n = InlineKeyboardButton(text="Нет", callback_data='sms_today_n')
    keyboard_status_today_y_n.add(button_status_today_y, button_status_today_n)
    await bot.send_message(message.chat.id, 'Установить оповещение', reply_markup=keyboard_status_today_y_n)
    await FSM_note_today_add.next()

async def add_discription_today(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'sms_today_y':
        async with state.proxy() as data:
            path = 'user_profiles/' + str(callback.from_user.id) + '.db'
            base = sqlite3.connect(path)
            cur = base.cursor()
            cur.execute('INSERT INTO note_today VALUES(?, ?, ?)',
                            (data['time'], data['description'], "🕔"))
            base.commit()
            base.close()
        await state.finish()
        await note_today_show(callback.from_user.id)
    elif callback.data == 'sms_today_n':
        async with state.proxy() as data:
            path = 'user_profiles/' + str(callback.from_user.id) + '.db'
            base = sqlite3.connect(path)
            cur = base.cursor()
            cur.execute('INSERT INTO note_today VALUES(?, ?, ?)',
                                (data['time'], data['description'], '❌'))
            base.commit()
            base.close()
        await state.finish()
        await note_today_show(callback.from_user.id)
    else:
        await callback.message.answer('Жми кнопки :)')
        return

async def listener_change_today(callback : types.CallbackQuery, state: FSMContext):
    if callback.data == 'time_change_today':
        async with state.proxy() as data:
            data['choose'] = 'time'
        await list_buttons_note(callback)
        await FSM_note_today_change.next()
    elif callback.data == 'description_change_today':
        async with state.proxy() as data:
            data['choose'] = 'description'
        await list_buttons_note(callback)
        await FSM_note_today_change.next()
    elif callback.data == 'status_change_today':
        async with state.proxy() as data:
            data['choose'] = 'status'
        await state.finish()
        await list_buttons_note(callback)
        await FSM_today_status_change.start.set()



async def change_row_today(callback : types.CallbackQuery, state: FSMContext):
    # path = 'user_profiles/' + str(callback.from_user.id) + '.db'
    # base = sqlite3.connect(path)
    # cur = base.cursor()
    # time = cur.execute('SELECT time FROM note_today').fetchall()
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
            await FSM_note_today_change.next()


async def change_value_today(message : types.Message, state : FSMContext):
    async with state.proxy() as data:
        data['new_value'] = message.text
    async with state.proxy() as data:
        path = 'user_profiles/' + str(message.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        cur.execute(f"UPDATE note_today SET {data['choose']} == ? WHERE time == ?", (data['new_value'], data['old_value']))
        base.commit()
        base.close()
    await state.finish()
    await bot.send_message(message.chat.id, 'Данные обновлены')
    await note_today_show(message.from_user.id)

async def change_status_listener(callback : types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["old_value"] = callback.data
    keyboard_change = InlineKeyboardMarkup()
    button_change1 = InlineKeyboardButton(text='✅', callback_data='✅')
    button_change2 = InlineKeyboardButton(text='🕔', callback_data='🕔')
    button_change3 = InlineKeyboardButton(text='❌', callback_data='❌')
    keyboard_change.add(button_change1, button_change2, button_change3)
    await callback.message.answer('Выберете статус?', reply_markup=keyboard_change)
    await FSM_today_status_change.next()

async def change_status_finisher(callback : types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["new_value"] = callback.data
        path = 'user_profiles/' + str(callback.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        cur.execute(f"UPDATE note_today SET status == ? WHERE time == ?",
                    (data['new_value'], data['old_value']))
        base.commit()
        base.close()
    await state.finish()
    await callback.message.answer('Данные обновлены')
    await note_today_show(callback.from_user.id)


async def row_delete_today(callback : types.CallbackQuery, state: FSMContext):
    path = 'user_profiles/' + str(callback.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    time = cur.execute('SELECT time FROM note_today').fetchall()
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
            cur.execute(f"DELETE from note_today WHERE time == ?", (data['row'],))
            base.commit()
            base.close()
        await state.finish()
        await callback.message.answer('Запись удалена')
        await note_today_show(callback.from_user.id)





async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено")

def register_handlers_note_today(dp : Dispatcher):
    dp.register_message_handler(note_today, commands=['note_today'])
    dp.register_callback_query_handler(listener_today, lambda call: call.data == 'add_today' or call.data == "change_today" or call.data == "delete_today" or call.data == "button_show_today")

    dp.register_message_handler(add_time_today, state=FSM_note_today_add.addtime)
    dp.register_message_handler(status_note_today, state=FSM_note_today_add.status_note_today)
    dp.register_callback_query_handler(add_discription_today, state=FSM_note_today_add.adddiscription)

    dp.register_callback_query_handler(listener_change_today, state=FSM_note_today_change.change_choose)
    dp.register_callback_query_handler(change_row_today, state=FSM_note_today_change.change_row)
    dp.register_message_handler(change_value_today, state=FSM_note_today_change.change_value)

    dp.register_callback_query_handler(change_status_listener, state=FSM_today_status_change.start)
    dp.register_callback_query_handler(change_status_finisher, state=FSM_today_status_change.finish)

    dp.register_callback_query_handler(row_delete_today, state=FSM_note_today_delete.delete_row)

    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")