from aiogram.utils import executor
from create_bot import dp


from handlers import client,admin,other,note
client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
note.register_handlers_note(dp)

from keyboards import keyboard_ed
keyboard_ed.register_handlers_keyboard_ed(dp)



executor.start_polling(dp, skip_updates=True)