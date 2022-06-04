# FOR SCRAPING
import requests
from bs4 import BeautifulSoup

# TELEGRAM BOT
import aiogram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Command, BoundFilter

# DOT ENV
import os
from dotenv import load_dotenv

# OTHER
import csv

# GET BOT TOKEN
load_dotenv()
BOT_TOKEN = str(os.getenv('BOT_TOKEN'))

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

admin = int(os.getenv('ADMIN'))  # admin telegram id


# FILTERS ------------------------
class AdminFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        member = await message.chat.get_member(message.from_user.id)
        return member.is_chat_admin() == admin or message.from_user.id == admin


class NtkGroup(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.id == -1001684546093

# class BotState(BoundFilter):
#     async def check(self, message: types.Message) -> bool:
#         return bot_state() == 1


def setup(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)


# FUNCTIONS ----------------------

def bot_state(change=None):
    # get state
    r = csv.reader(open('bot_state.csv'))
    state = list(r)
    if change is None:
        return int(state[0][0])

    # change and get state
    else:
        with open('eggs.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(str(change))
        return int(bot_state())


def get_ntk_quantity():
    url = 'https://www.techlib.cz/en/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    body = soup.find_all('div', class_='panel-body text-center lead')
    # for i in body:
    #     q = i.find('span').text
    return body[0].text.strip()


# BOT HANDLERS ---------------------
@dp.message_handler(Command("ntk", prefixes='!/'))
async def ntk(msg: types.Message):
    q = get_ntk_quantity()
    await msg.answer(f'В NTK сейчас людей: {q}')
    await msg.delete()


@dp.message_handler(Command('help', prefixes='!/'), NtkGroup())
async def ask_ntk(msg: types.Message):
    text = """
    Хай, моя задача в этой жизни показывать количество людей в НТК!

    GitHub:
    admin: t.me/vsem_azamat
    """
    await msg.answer(text)
    await msg.delete()

# @dp.message_handler(Command('ntk_state', prefixes='!/'), AdminFilter())
# async def state_bot(msg: types.Message):
#     state_dict = {'off': 0, 'on': 1}
#     try:
#         state_new = msg.text.lower().split()[1]
#         # CHANGE STATE OF BOT
#         print(state_new)
#         if state_new in state_dict:
#             state = bot_state(state_dict.get(state_new))
#             raise IndexError
#
#         # ERROR: UNCORRECT PARAMETER OF COMMAND
#         else:
#             await msg.answer("Неверна задана команда!\n\nПример:\n/ntk_state off\n/ntk_state on\n/ntk_state")
#
#     # GET STATE OF BOT
#     except IndexError:
#         state_text_dict = {0: 'выключен', 1: 'включен'}
#         state = bot_state()
#         print(state)
#         print(type(state))
#         await msg.answer(f'Бот сейчас {state_text_dict.get(state)}')
#     await msg.delete()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
