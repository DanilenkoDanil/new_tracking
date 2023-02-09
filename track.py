import time

from binance.client import Client
import requests
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

pub = 'NpaXMioHavvDu27dSzCsTd7VXY2x3dsrf3CZ7e705CHiVDEMfsqetMywcTwSDR2B'
pri = 'rJmldKeCoYGAJ01nwqfG4JZDNjkJfadHUQzkt51hbyIXeIuAxG3pb6yEa2QHA4lW'
current_symbols = []
url = 'http://185.231.155.38'
bd_url = 'http://212.118.40.209'


def find_info(text: str):
    info = dict()
    info["source"] = text.split('#')[1].split('\n')[0]
    info["symbol"] = text.split('#')[2].split(' ')[0]
    info["type"] = text.split('#')[3].split('\n')[0]
    info["entry"] = float(text.split('Entry: ')[1].split('\n')[0])
    return info


def find_msg(client: TelegramClient, channel,  symbol: str):
    history = client(GetHistoryRequest(
        peer=channel,
        offset_id=0,
        offset_date=None, add_offset=0,
        limit=100, max_id=0, min_id=0,
        hash=0))
    messages = list(history.messages)
    for message in messages:
        if f"#{symbol.upper()}" in message.message:
            return find_info(message.message)


def convert_to_dict(symbols: list):
    result_dict = {}
    for i in symbols:

        if i['symbol'] in result_dict.keys() and float(i['stopPrice']) > float(result_dict[i['symbol']]['stopPrice']):
            result_dict[i['symbol']] = i
        elif i['symbol'] not in result_dict.keys():
            result_dict[i['symbol']] = i
    return result_dict


def main():
    client_bin = Client(pub, pri)
    last_order_id = ''
    client = TelegramClient(
        "session_for_read",
        3566267,
        "77c8ec3ad6b760c7d247ef4159721524",
    )
    client.start()
    for i in client.iter_dialogs():
        if '1001624443589' in str(i.id):
            channel = i

    while True:
        time.sleep(30)
        global current_symbols
        try:
            order = client_bin.futures_get_all_orders()[-1]
        except requests.exceptions.ReadTimeout:
            continue
        if last_order_id != order['orderId']:
            last_order_id = order['orderId']
            if order['status'] == 'FILLED' and 'STOP' in order['origType']:
                order = client_bin.get_ticker(symbol=order['symbol'])
            else:
                print('next 1')
                time.sleep(2)
                continue
        else:
            print('next 2')
            time.sleep(2)
            continue
        print(current_symbols)
        try:
            info = find_msg(client, channel, order['symbol'])
        except Exception as e:
            print(e)
            continue
        if info['type'] == 'LONG':
            print('Long')
            print('up!!!!')
            percent = round(float(order['lastPrice'])/float(info["entry"]) * 100 - 100, 2)
            text_for_msg = f"{order['symbol']}, процент {percent}"
            print('test')
            requests.get(f'{bd_url}/api/send-signal-result/?name={info["symbol"]}&type=LONG&price={order["lastPrice"]}&source={info["source"]}&price_change={percent}')
            requests.get(f'{url}/api/send-target/?message={text_for_msg}'
                         f'&id={order["symbol"]}'
                         f'&name={order["symbol"]}'
                         f'&current={float(order["lastPrice"])}'
                         f'&old={float(info["entry"])}'
                         f'&percent={percent}'
                         f'&type=long'
            )
        else:
            print('up!!!!')
            percent = 1 - round(float(order['lastPrice'])/float(info["entry"]) * 100 + 100, 2)
            text_for_msg = f"{order['symbol']}, процент {percent}"
            print('test')
            requests.get(f'{bd_url}/api/send-signal-result/?name={info["symbol"]}&type=SHORT&price={order["lastPrice"]}&source={info["source"]}&price_change={percent}')
            requests.get(f'{url}/api/send-target/?message={text_for_msg}'
                         f'&id={order["symbol"]}'
                         f'&name={order["symbol"]}'
                         f'&current={float(order["lastPrice"])}'
                         f'&old={float(info["entry"])}'
                         f'&percent={percent}'
                         f'&type=short'
                         )

# http://212.118.40.209/api/send-signal-result/?name=TESTMONEY&type=SHORT&price=1331&source=Yer&price_change=12
if __name__ == "__main__":
    main()
