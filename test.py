import time

from binance.client import Client

pub = 'NpaXMioHavvDu27dSzCsTd7VXY2x3dsrf3CZ7e705CHiVDEMfsqetMywcTwSDR2B'
pri = 'rJmldKeCoYGAJ01nwqfG4JZDNjkJfadHUQzkt51hbyIXeIuAxG3pb6yEa2QHA4lW'

last_order_id = ''
client_bin = Client(pub, pri)
# client_bin.futures_create_order(symbol='BTCUSDT',
#                                 side='SELL',
#                                 positionSide='BOTH',
#                                 type='STOP_MARKET',
#                                 closePosition='true',
#                                 timeInForce='GTC',
#                                 stopPrice=17280)
while True:
    order = client_bin.futures_get_all_orders()[-1]
    if last_order_id != order['orderId']:
        last_order_id = order['orderId']
        # if order['status'] != 'CANCELED' and order['status'] != 'EXPIRED':
        print(order['symbol'])
        print(client_bin.get_ticker(symbol=order['symbol']))
        print(order)
    time.sleep(2)
