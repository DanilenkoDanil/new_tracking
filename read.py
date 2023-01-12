import configparser
import json
import asyncio

from telethon.sync import TelegramClient
from telethon import connection

# для корректного переноса времени сообщений в json
from datetime import date, datetime

# классы для работы с каналами
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

from try_db import User


def convert_to_dict(symbols: list):
    result_dict = {}
    for i in symbols:

        if i['symbol'] in result_dict.keys() and float(i['stopPrice']) > float(result_dict[i['symbol']]['stopPrice']):
            result_dict[i['symbol']] = i
        elif i['symbol'] not in result_dict.keys():
            result_dict[i['symbol']] = i
    return result_dict


old_message = []
db = User('db.db')


with open("setting.json", 'r', encoding='utf8') as out:
    setting = json.load(out)

    client = TelegramClient(
        setting['account']['session'],
        setting['account']['api_id'],
        setting['account']['api_hash']
    )

    client.start()


async def change_user_links_text(message: str, username: str) -> str:
    for item in message.split():
        if '@' in item:
            print('!!!!!!!!!!!!!!!!!!!!!!!')
            if not item[1].isdigit():
                message = message.replace(item, username)

    return message


def check_msg(text):
    if "LONG" in text:
        return True
    if "лонг" in text:
        return True
    if "Лонг" in text:
        return True
    if "Long" in text:
        return True
    if "Short" in text:
        return True
    if "SHORT" in text:
        return True
    if "Шорт" in text:
        return True
    if "шорт" in text:
        return True
    if '📈' in text:
        return True

    return False


async def dump_all_messages(channel):
    """Записывает json-файл с информацией о всех сообщениях канала/чата"""

    history = await client(GetHistoryRequest(
        peer=channel,
        offset_id=0,
        offset_date=None, add_offset=0,
        limit=2, max_id=0, min_id=0,
        hash=0))
    messages = list(history.messages)
    messages.reverse()
    for message in messages:
        if int(message.id) not in old_message:
            try:
                symbol = message.message.split('#')[2].split(' -')[0]
                entry = message.message.split('Entry: ')[1].split('\n')[0]
                take_profit = message.message.split('Take profit: ')[1].split('\n')[0].split(', ')
                print(symbol)
                print(entry)
                print(take_profit)
                if float(take_profit[0]) < float(take_profit[1]):
                    db.register(symbol, float(entry), float(take_profit[0]), float(take_profit[1]), float(take_profit[2]), 'LONG')
                else:
                    db.register(symbol, float(entry), float(take_profit[0]), float(take_profit[1]), float(take_profit[2]), 'SHORT')
                old_message.append(int(message.id))
            except Exception as e:
                print(e)


async def main():
    dialogs = await client.get_dialogs()

    for index, dialog in enumerate(dialogs):
        if index < 250:
            if str(dialog.id) == '-1001624443589':
                channel = dialog
                print('+')

    while True:
        try:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('Скан')
            await dump_all_messages(channel)
            await asyncio.sleep(30)
        except Exception as e:
            print(e)
            await asyncio.sleep(300)

with client:
    client.loop.run_until_complete(main())
