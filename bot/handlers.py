import io
import random

from aiogram import Bot, Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from apps.gpt import get_gpt_response
from apps.parse_functions import get_ntk_quantity
from apps.plot_functions import plotGraph
from apps.predictModels import predictModels
from apps.weather_api import weatherAPI
from bot.filters import NTKChatFilter, SuperAdmins
from config import cnfg

router = Router()


@router.message(Command('nick'), SuperAdmins(), NTKChatFilter())
async def admin(message: types.Message, bot: Bot):
    """Give nickname title to user in NTK chat"""
    bot_info = await bot.me()
    bot_chat_info = await bot.get_chat_member(
        chat_id=message.chat.id,
        user_id=bot_info.id
    )
    if isinstance(bot_chat_info, types.ChatMemberAdministrator):
        if bot_chat_info.can_promote_members:
            new_nick = message.text[6:].strip()
            if new_nick and message.reply_to_message:
                user_id = message.reply_to_message.from_user.id
                user_info = await bot.get_chat_member(
                    chat_id=message.chat.id,
                    user_id=user_id
                    )
                if not isinstance(user_info, types.ChatMemberAdministrator):
                    await message.chat.promote(
                        user_id=user_id, 
                        can_invite_users=True
                        )
                await message.chat.set_administrator_custom_title(
                    user_id=user_id,
                    custom_title=new_nick
                    )
            await message.delete()
            return

    await message.delete()


@router.message(Command('anon_enable'), SuperAdmins())
async def anon_enable(message: types.Message):
    """Enable anon functionality"""
    cnfg.ANON_ENABLED = True
    await message.answer("🤖<b>Анон включен</b>\n")
    await message.delete()


@router.message(Command('anon_disable'), SuperAdmins())
async def anon_disable(message: types.Message):
    """Disable anon functionality"""
    cnfg.ANON_ENABLED = False
    await message.answer("🤖<b>Анон выключен</b>\n")
    await message.delete()


@router.message(Command('anon'))
async def anon(message: types.Message, bot: Bot):
    """Send anon message"""
    if not cnfg.ANON_ENABLED:
        await message.reply("💤<b>Анончик сейчас спит</b>💤")
        await message.delete()
        return

    text_head = "<b>💌Анон плс:</b>\n\n"
    text = message.text[6:].strip()
    if message.chat.id == message.from_user.id and text:
        member = await bot.get_chat_member(
            chat_id=cnfg.ID_NTK_BIG_CHAT,
            user_id=message.from_user.id
            )
        if member.status in ['creator', 'administrator', 'member']:
            await bot.send_message(
                chat_id=cnfg.ID_NTK_BIG_CHAT,
                text=text_head + text,
                parse_mode='HTML'
                )
    else:
        await message.delete()


@router.message(Command('ntk'), NTKChatFilter())
async def ntk(message: types.Message):
    """Send ntk quantity"""
    q = await get_ntk_quantity()
    text = f"📚<b>В NTK сейчас людей:</b> {q}"
    text += '\nДохуя крч.' if q >= 700 else ''
    text += "\n\n📣<a href='t.me/ntk_info'><b>NTK info</b></a>"
    await message.answer(
        text=text,
        parse_mode='HTML',
    )
    await message.delete()


@router.message(Command('help'))
async def help(message: types.Message):
    """Send help message"""
    text = \
        "🤖<b>Хай, я создан для чата @chat_ntk!</b>\n\n" \
        "📋<b>Команды:</b>\n" \
        "/ntk - Показать кол-во людей в NTK\n" \
        "/graph - Показать график посещений NTK\n"
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text='📚NTK chat', url='https://t.me/chat_ntk'),
        types.InlineKeyboardButton(text='👨‍🎓Admin', url='t.me/vsem_azamat'),
        types.InlineKeyboardButton(text='🧑‍💻GitHub', url='github.com/vsem-azamat/ntk_bot/')
    )
    builder.adjust(1)
    await message.answer(
        text=text,
        reply_markup=builder.as_markup(),
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


@router.message(Command('graph'), NTKChatFilter())
async def send_stats(message: types.Message, bot: Bot):
    """Send graph with NTK visits prediction and weather forecast """
    fig_visits, _ = await plotGraph.daily_graph_with_predictions()

    buffer_visits = io.BytesIO()
    fig_visits.savefig(buffer_visits, format='png')
    buffer_visits.seek(0)

    await bot.send_photo(
        chat_id=message.chat.id,
        photo=types.BufferedInputFile(
            file=buffer_visits.read(),
            filename='visits.png',
        )
    )
    await message.delete()


@router.message(Command('weather'), SuperAdmins())
async def send_weather(message: types.Message, bot: Bot):
    """Send weather forecast"""
    fig_weather, _, _ = await weatherAPI.plot_daily_weather_forecast()

    buffer_weather = io.BytesIO()
    fig_weather.savefig(buffer_weather, format='png')
    buffer_weather.seek(0)

    await bot.send_photo(
        chat_id=message.chat.id,
        photo=types.BufferedInputFile(
            file=buffer_weather.read(),
            filename='weather.png',
        )
    )
    await message.delete()


@router.message(Command('learn'), SuperAdmins())
async def learn_models(msg: types.Message):
    """Learn models"""
    await predictModels.learn_models()
    await msg.answer('Models learned!')
    await msg.delete()


@router.message(Command('data'), SuperAdmins())
async def send_data(msg: types.Message, bot: Bot):
    """Send ntk_data.txt with NTK visits"""
    with open('ntk_data.txt', 'rb') as file:
        input_file = types.BufferedInputFile(
            file=file.read(),
            filename='ntk_data.txt'
        )
        await bot.send_document(msg.chat.id, input_file)


@router.message(NTKChatFilter())
async def gpt_bullying(message: types.Message):
    """Random GPT response"""
    text = message.text
    if text and random.random() < 0.025:
        response = await get_gpt_response(text)
        if response:
            await message.reply(str(response))
