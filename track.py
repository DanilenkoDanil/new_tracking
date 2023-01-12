import time

from binance.client import Client
from try_db import User
from try_db import get_active_target
import requests

pub = 'NpaXMioHavvDu27dSzCsTd7VXY2x3dsrf3CZ7e705CHiVDEMfsqetMywcTwSDR2B'
pri = 'rJmldKeCoYGAJ01nwqfG4JZDNjkJfadHUQzkt51hbyIXeIuAxG3pb6yEa2QHA4lW'
current_symbols = []
url = 'http://185.231.155.38'


def convert_to_dict(symbols: list):
    result_dict = {}
    for i in symbols:

        if i['symbol'] in result_dict.keys() and float(i['stopPrice']) > float(result_dict[i['symbol']]['stopPrice']):
            result_dict[i['symbol']] = i
        elif i['symbol'] not in result_dict.keys():
            result_dict[i['symbol']] = i
    return result_dict


def main():
    db = User('db.db')
    client_bin = Client(pub, pri)
    last_order_id = ''

    while True:
        global current_symbols
        order = client_bin.futures_get_all_orders()[-1]
        if last_order_id != order['orderId']:
            last_order_id = order['orderId']
            if order['status'] != 'CANCELED' and order['status'] != 'EXPIRED':
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

        symbol_info = db.get_symbol(order['symbol'])
        target = get_active_target([symbol_info[0], symbol_info[1], symbol_info[2]])
        if target == 0:
            db.delete_symbol(order['symbol'])
            continue

        if time.time() - float(symbol_info[3]) > 60*60*24*10:
            db.delete_symbol(order['symbol'])
            continue
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print(symbol_info[5])
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        if symbol_info[5] == 'LONG':
            print('Long')
            print('up!!!!')
            percent = round(float(order['lastPrice'])/float(symbol_info[4]) * 100 - 100, 2)
            text_for_msg = f"{order['symbol']} - выполнен таргет {target[0]}, процент {percent}"
            print('test')
            requests.get(f'{url}/api/send-target/?message={text_for_msg}'
                         f'&id={order["symbol"]}'
                         f'&name={order["symbol"]}'
                         f'&current={float(order["lastPrice"])}'
                         f'&old={float(symbol_info[4])}'
                         f'&percent={percent}'
                         f'&type=long'
            )
            db.close_target(order['symbol'], target[0])
        else:
            print('up!!!!')
            percent = 1 - round(float(order['lastPrice'])/float(symbol_info[4]) * 100 + 100, 2)
            text_for_msg = f"{order['symbol']} - выполнен таргет {target[0]}, процент {percent}"
            print('test')
            requests.get(f'{url}/api/send-target/?message={text_for_msg}'
                         f'&id={order["symbol"]}'
                         f'&name={order["symbol"]}'
                         f'&current={float(order["lastPrice"])}'
                         f'&old={float(symbol_info[4])}'
                         f'&percent={percent}'
                         f'&type=short'
                         )
            db.close_target(order["symbol"], target[0])


if __name__ == "__main__":
    main()
