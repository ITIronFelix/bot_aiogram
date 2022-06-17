from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.dispatcher.filters import Text


class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()

#Начало диалога
# @dp.message.handler(commands=["Загрузить"], state=None) #отправная точка
async def cm_start(message: types.Message):
    await FSMAdmin.photo.set()                        #делается запрос
    await  message.reply("Загрузи фото")

# @dp.message.handler(content_types=['photo'], state=FSMAdmin.photo)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:                         #память работает как словарь
        data['photo'] = message.photo[0].file_id            #берется не сам файл, а его id
    await FSMAdmin.next()                        #делается запрос дальше
    await  message.reply("Название")

# @dp.message.handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdmin.next()
    await message.reply("описание")

# @dp.message.handler(state=FSMAdmin.description)
async def load_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await FSMAdmin.next()
    await message.reply("цена")

# @dp.message.handler(state=FSMAdmin.price)
async def load_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    async with state.proxy() as data:
        await message.reply(str(data))                  #выдать в чат содержание словаря
    await state.finish()

#выход из состояний
# @dp.message_handler(state="*", commands='отмена')
# @dp.message_handler(Text(equals = 'отмена', ignore_case = True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Ok')


def register_handlers_admin(dp : Dispatcher):
    dp.register_message_handler(cm_start, commands=["priv"], state=None)
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin.photo)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_message_handler(load_description, state=FSMAdmin.description)
    dp.register_message_handler(load_price, state=FSMAdmin.price)
    dp.register_message_handler(cancel_handler, state="*", commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals = 'отмена', ignore_case = True), state='*')