from aiogram.utils import executor
from create_bot import dp
import asyncio
import aioschedule

from handlers import client,admin,other,note_tomorrow,note_today
client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
note_tomorrow.register_handlers_note_tomorrow(dp)
note_today.register_handlers_note_today(dp)



from keyboards import keyboard_ed
keyboard_ed.register_handlers_keyboard_ed(dp)



from just_in_time.good_morning import hello, sing, note_swap





async def scheduler():
    aioschedule.every().day.at("08:30").do(hello)
    aioschedule.every().day.at("00:24").do(note_swap)
    aioschedule.every().minute.do(sing)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    asyncio.create_task(scheduler())


# '🕔'   '✅'   '❌'




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)