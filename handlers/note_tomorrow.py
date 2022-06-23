from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from create_bot import bot
from aiogram.dispatcher.filters import Text

class FSM_note_tommorow_add(StatesGroup):
    addtime = State()
    status_note_tomorrow = State()
    adddiscription = State()

class FSM_note_tommorow_change(StatesGroup):
    change_choose = State()
    change_row = State()
    change_value = State()

class FSM_note_tommorow_delete(StatesGroup):
    delete_row = State()


class FSM_note_tomorrow_sms(StatesGroup):
    sms_start = State()
    sms_change_tomorrow = State()

async def note_tomorrow_show_m(id):
    path = 'user_profiles/' + str(id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    time = cur.execute('SELECT * FROM note_tomorrow ORDER BY time ASC').fetchall()
    lst = [*(x for t in time for x in t)]
    if len(lst):
        i = 0
        list = []
        while i < len(lst):
            list.append(lst[i] + " " + lst[i + 1] + " " + lst[i+2])
            i += 3
        base.close()
        await bot.send_message(id, 'Ваши планы на завтра:' + "\n\n" + "\n".join(list))
    else:
        await bot.send_message(id, 'У вас нет планов на завтра')

async def note_tomorrow_show_c(callback : types.CallbackQuery):
    path = 'user_profiles/' + str(callback.from_user.id) + '.db'
    base = sqlite3.connect(path)
    cur = base.cursor()
    time = cur.execute('SELECT * FROM note_tomorrow ORDER BY time ASC').fetchall()
    lst = [*(x for t in time for x in t)]
    if len(lst):
        i = 0
        list = []
        while i < len(lst):
            list.append(lst[i] + " " + lst[i + 1] + " " + lst[i+2])
            i += 3
        base.close()
        await callback.message.answer('Ваши планы на завтра:' + "\n\n" + "\n".join(list))
    else:
        await callback.message.answer( 'У вас нет планов на завтра')




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
async def add_time_tomorrow(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
    await FSM_note_tommorow_add.next()
    await message.reply('Введите описание')

async def status_note_tomorrow(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    keyboard_status_tomorrow_y_n = InlineKeyboardMarkup()
    button_status_tomorrow_y = InlineKeyboardButton(text="Да", callback_data='sms_tomorrow_y')
    button_status_tomorrow_n = InlineKeyboardButton(text="Нет", callback_data='sms_tomorrow_n')
    keyboard_status_tomorrow_y_n.add(button_status_tomorrow_y, button_status_tomorrow_n)
    await bot.send_message(message.chat.id, 'Установить оповещение', reply_markup=keyboard_status_tomorrow_y_n)
    await FSM_note_tommorow_add.next()

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
        await note_tomorrow_show_m(callback.from_user.id)
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
        await note_tomorrow_show_c(callback)
    else:
        await callback.message.answer('Жми кнопки :)')
        return

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
    await note_tomorrow_show_m(message)

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
        await note_tomorrow_show_c(callback)

async def sms_start_tomorrow(message : types.Message):
    keyboard_sms = InlineKeyboardMarkup()
    button_sms1 = InlineKeyboardButton(text = 'По всем', callback_data= 'sms_all_tomorrow')
    button_sms2 = InlineKeyboardButton(text = 'По одному', callback_data= 'sms_one_tomorrow')
    keyboard_sms.add(button_sms1, button_sms2)
    await bot.send_message(message.chat.id, 'Вы хотите изменить статус оповещения по всем задачам или по одной конкретной?', reply_markup= keyboard_sms)
    await FSM_note_tomorrow_sms.sms_start.set()

async def sms_choose_tomorrow(callback : types.CallbackQuery, state : FSMContext):
    async with state.proxy() as data:
        data['choose'] = callback.data
    if callback.data == 'sms_all_tomorrow':
        keyboard_sms_change_all = InlineKeyboardMarkup()
        button_sms_change_all1 = InlineKeyboardButton(text='Включить уведомления', callback_data='sms_all_on_tomorrow')
        button_sms_change_all2 = InlineKeyboardButton(text='Выключить уведомления', callback_data='sms_all_off_tomorrow')
        keyboard_sms_change_all.add(button_sms_change_all1, button_sms_change_all2)
        await callback.message.answer('Включить или выключить уведомления?', reply_markup=keyboard_sms_change_all)
    elif callback.data == 'sms_one_tomorrow':
        path = 'user_profiles/' + str(callback.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        time = cur.execute('SELECT time, description, status FROM note_tomorrow ORDER BY time ASC').fetchall()
        lst = [*(x for t in time for x in t)]
        base.close()
        keyboard_time = InlineKeyboardMarkup()
        i = 0
        while i < len(lst):
            keyboard_time.add(
                InlineKeyboardButton(text=f'{lst[i]} {lst[i + 1]} {lst[i + 2]}', callback_data=f'{lst[i]}'))
            i += 3
        await callback.message.answer('Выберите запись', reply_markup=keyboard_time)
    await FSM_note_tomorrow_sms.next()


async def sms_change_tomorrow(callback : types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['old_value'] = callback.data
    if callback.data == 'sms_all_on_tomorrow':
        path = 'user_profiles/' + str(callback.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        cur.execute(f"UPDATE note_tomorrow SET status == ? WHERE status == ?",
                    ("🕔", '❌'))
        base.commit()
        base.close()
        await callback.message.answer('Уведомления включены')
    elif callback.data == 'sms_all_off_tomorrow':
        path = 'user_profiles/' + str(callback.from_user.id) + '.db'
        base = sqlite3.connect(path)
        cur = base.cursor()
        cur.execute(f"UPDATE note_tomorrow SET status == ? WHERE status == ?",
                    ('❌', "🕔"))
        base.commit()
        base.close()
        await callback.message.answer('Уведомления отключены')
    else:
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
                path = 'user_profiles/' + str(callback.from_user.id) + '.db'
                base = sqlite3.connect(path)
                cur = base.cursor()
                r = cur.execute(f'SELECT status FROM note_tomorrow WHERE time == ?', (data['old_value'],)).fetchone()
                if r[0] == '❌' or r[0] == '✅':
                    cur.execute(f"UPDATE note_tomorrow SET status == ? WHERE time == ?",
                                ("🕔", data['old_value']))
                else:
                    cur.execute(f"UPDATE note_tomorrow SET status == ? WHERE time == ?",
                                ('❌', data['old_value']))
                base.commit()
                base.close()
                await callback.message.answer('Статус изменен')
    await state.finish()
    await note_tomorrow_show_c(callback)



async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено")








def register_handlers_note_tomorrow(dp : Dispatcher):
    dp.register_message_handler(note_tomorrow_show_m, commands=['plans'])
    dp.register_message_handler(note_tomorrow, commands=['plans_change'])
    dp.register_callback_query_handler(listener, lambda call: call.data == 'add' or call.data == "change" or call.data == "delete")

    dp.register_message_handler(add_time_tomorrow, state=FSM_note_tommorow_add.addtime)
    dp.register_message_handler(status_note_tomorrow, state=FSM_note_tommorow_add.status_note_tomorrow)
    dp.register_callback_query_handler(add_discription_tomorrow, state=FSM_note_tommorow_add.adddiscription)

    dp.register_callback_query_handler(listener_change, state= FSM_note_tommorow_change.change_choose)
    dp.register_callback_query_handler(change_row, state = FSM_note_tommorow_change.change_row)
    dp.register_message_handler(change_value, state=FSM_note_tommorow_change.change_value)

    dp.register_callback_query_handler(row_delete, state=FSM_note_tommorow_delete.delete_row)

    dp.register_message_handler(sms_start_tomorrow, commands='sms_tomorrow')
    dp.register_callback_query_handler(sms_choose_tomorrow, state=FSM_note_tomorrow_sms.sms_start)
    dp.register_callback_query_handler(sms_change_tomorrow, state=FSM_note_tomorrow_sms.sms_change_tomorrow)

    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
