from aiogram.utils import executor
from create_bot import dp


from handlers import client,admin,other,note_tomorrow,note_today
client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
note_tomorrow.register_handlers_note_tomorrow(dp)
note_today.register_handlers_note_today(dp)

from keyboards import keyboard_ed
keyboard_ed.register_handlers_keyboard_ed(dp)



executor.start_polling(dp, skip_updates=True)