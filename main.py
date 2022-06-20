from aiogram.utils import executor
from create_bot import dp, bot
import asyncio
import aioschedule
import time


from handlers import client,admin,other,note_tomorrow,note_today
client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
note_tomorrow.register_handlers_note_tomorrow(dp)
note_today.register_handlers_note_today(dp)


from keyboards import keyboard_ed
keyboard_ed.register_handlers_keyboard_ed(dp)



from just_in_time.good_morning import hello





async def scheduler():
    aioschedule.every().day.at("22:31").do(hello)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    # executor.start_polling(dp, skip_updates=True)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)