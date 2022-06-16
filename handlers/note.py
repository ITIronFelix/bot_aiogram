from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from create_bot import dp, bot


class FSM_note_tommorow_add(StatesGroup):
    addtime = State()
    adddiscription = State()



async def note_tomorrow(message : types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text = "Добавить запись", callback_data='add')
    button2 = InlineKeyboardButton(text= 'Изменить', callback_data='change')
    button3 = InlineKeyboardButton(text= 'Удалить', callback_data='delete')
    keyboard.add(button1, button2, button3)
    await message.reply('Что вы хотите сделать?', reply_markup = keyboard)



# choose
# @dp.callback_query_handler(text = 'add')
async def listener(callback :  types.CallbackQuery):
    if callback.data == 'add':
        await FSM_note_tommorow_add.addtime.set()
        await callback.message.answer('Введите время')
    elif callback.data == 'change':
        await callback.message.answer('change')
    elif callback.data == 'delete':
        await  callback.message.answer('delete')

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




def register_handlers_note(dp : Dispatcher):
    dp.register_message_handler(note_tomorrow, commands=['note'])
    dp.register_callback_query_handler(listener)
    dp.register_message_handler(add_time, state=FSM_note_tommorow_add.addtime)
    dp.register_message_handler(add_discription, state=FSM_note_tommorow_add.adddiscription)
#     # dp.register_message_handler(change_note, state=FSM_note_tommorow.cnange)