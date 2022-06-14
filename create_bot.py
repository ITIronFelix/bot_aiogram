from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from configure import token
from aiogram.contrib.fsm_storage.memory import MemoryStorage #машина состояний

storage=MemoryStorage()

bot = Bot(token)
dp = Dispatcher(bot, storage=storage)