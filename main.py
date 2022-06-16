from aiogram.utils import executor
from create_bot import dp


from handlers import client,admin,other,note
client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
note.register_handlers_note(dp)

executor.start_polling(dp, skip_updates=True)