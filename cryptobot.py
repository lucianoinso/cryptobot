#!/usr/bin/python3
import os
import math
from time import sleep
from datetime import datetime
from helpers import truncate
from binance.client import Client
from telegram_bot import send_msg
from constants import BNC_API_KEY as API_KEY
from constants import BNC_API_SECRET as API_SECRET


"""
    Weights:
    Client()                    :  1
    client.get_exchange_info()  : 10    (exchangeInfo)
    client.order_market_sell()  :  2    (order)
    client.order_market_buy()   :  2    (order)
    client.get_asset_balance()  : 10    (account) (2x)
    client.get_symbol_info()    : 10
    client.get_symbol_ticker()  :  1

    start: 1 + 10 + 10 = 21
    while loop: 10*2 + 1 = 21
"""

RUN_MODE = "TEST"         # RUN_MODE : ["TEST", "OPERATE"]
TIME_INTERVAL = 1         # In seconds, amount of time between runs
BUY_PRICE = 0.3006          # USDT
SELL_PRICE = 0.34         # USDT
SYMBOL = "DOGEUSDT"
ASSET = "DOGE"
ORDER_REQUEST_WEIGHT = 2  # Depends on the Binance website

""" Configuration and Initialization """
project_path = "/home/loot/Projects/cryptobot/"
API_KEY = API_KEY
API_SECRET = API_SECRET


def dump_crypto_price(crypto_dict):
    with open(project_path + 'crypto_prices.txt', 'a') as f:
        date_now = datetime.today().strftime('%m-%d %H:%M:%S')
        f.write(f"{date_now} - {crypto_dict[price]}\n")


def print_info(crypto_dict, usdt_dict):
    # pasar usdt_dict['balance'] a una variable (cantidad de usdt a usar) que se setea
    # al comienzo y se guarda sino despues de comprar no vamos a tener ese valor
    # inicial disponible. Aunque al hacerse 0 parece que no influye en el calculo.

    usdt_fee = usdt_dict['balance'] * 0.001
    crypto_fee = crypto_dict['balance'] * 0.001

    usdt_amount_with_fee = usdt_dict['balance'] - usdt_fee
    crypto_amount_with_fee = crypto_dict['balance'] - crypto_fee

    crypto_bought = usdt_amount_with_fee / BUY_PRICE
    total_crypto = crypto_bought + crypto_dict['balance']

    usdt_gain = (total_crypto - total_crypto * 0.001) * SELL_PRICE
    usdt_benefits = usdt_gain - (usdt_amount_with_fee + crypto_dict['balance'] * BUY_PRICE)
    print()
    print("Transaction information\n=======================\n")
    print(f"USDT balance: {usdt_dict['balance']}")
    print(f"USDT fee: {usdt_fee}")
    print(f"USDT balance with fee: {usdt_amount_with_fee}")
    print()
    print(f"Symbol: {crypto_dict['symbol']}")
    print(f"{crypto_dict['currency']} balance: {crypto_dict['balance']}")
    print(f"{crypto_dict['currency']} fee: {crypto_fee}")
    print(f"{crypto_dict['currency']} balance with fee: {crypto_amount_with_fee}")
    print()
    print(f"{crypto_dict['currency']} price: {crypto_dict['price']}")
    print(f"Buy price: {BUY_PRICE}")
    print(f"Sell price: {SELL_PRICE}")
    print(f"Total amount of {crypto_dict['currency']}: {total_crypto}")
    print(f"Calculated benefits: {usdt_benefits}")
    # print(f"{crypto_dict['currency']} max quantity: {crypto_dict['maxQty']}")
    # print(f"{crypto_dict['currency']} min quantity: {crypto_dict['minQty']}")

    # Next one doesn't change much with time, more useful with limit maybe?
    # print(f"{crypto_dict['currency']} max price: {crypto_dict['maxPrice']}")
    # print(f"{crypto_dict['currency']} min price: {crypto_dict['minPrice']}")
    # TODO maybe: min y max del dia
    print("\n")
    print("[CTRL+C] to interrupt")


def transact(transaction, buy_price, sell_price):
    client = transaction['client']
    crypto_dict = transaction['crypto_dict']
    usdt_dict = transaction['usdt_dict']

    usdt_amount_with_fee = usdt_dict['balance'] - usdt_dict['balance'] * 0.001
    crypto_amount_with_fee = crypto_dict['balance'] - crypto_dict['balance'] * 0.001

    crypto_buy_max_quantity = usdt_amount_with_fee / crypto_dict['price']
    crypto_quantity_decimal_places = math.ceil(-math.log10(crypto_dict['quantity_step_size']))

    crypto_buy_max_quantity_truncated = truncate(crypto_buy_max_quantity, crypto_quantity_decimal_places)
    crypto_sell_max_quantity_truncated = truncate(crypto_amount_with_fee, crypto_quantity_decimal_places)

    if crypto_dict['price'] <= buy_price and usdt_amount_with_fee > 1:
        response = client.order_market_buy(symbol=SYMBOL, quantity=crypto_buy_max_quantity_truncated)
        # response = "{'operation':'buy'}"
        msg = f"You bought {crypto_buy_max_quantity_truncated}\n {crypto_dict['currency']} price: {crypto_dict['price']}\n{response}"
        with open(project_path + 'transaction.txt', 'a') as f:
            f.write(msg + "\n\n")
        send_msg(msg)

    elif crypto_dict['price'] >= sell_price and crypto_amount_with_fee > 1:
        response = client.order_market_sell(symbol=SYMBOL, quantity=crypto_sell_max_quantity_truncated)
        # response = "{'operation':'sell'}"
        msg = f"You sold {crypto_sell_max_quantity_truncated}\n {crypto_dict['currency']} price: {crypto_dict['price']}\n{response}"
        with open(project_path + 'transaction.txt', 'a') as f:
            f.write(msg + "\n\n")
        send_msg(msg)
    # TODO: formatear bien los mensajes para el telegram y el log de transacciones


def main():
    while True:
        client = Client(API_KEY, API_SECRET)  # In case the connection fails it restarts from here.
        try:
            exchange_info = client.get_exchange_info()
            exchange_limits = exchange_info['rateLimits']
            request_weight_limit_per_min = exchange_limits[0]['limit']
            x_mbx_used_weight = client.response.headers['x-mbx-used-weight']

            # Estudiar si dejarlo afuera del while loop (con cuanta frecuencia cambia esta data?)
            # Creo que de ultima va a parar la ejecucion (maneja los decimales permitidos
            # para comprar/vender junto con otras cosas que no parecen cambiar mucho)
            crypto_filters = client.get_symbol_info(symbol=SYMBOL)['filters']

            # We don't care about this ones for now
            max_amount_orders_per_sec = exchange_limits[1]['limit']
            max_amount_orders_per_day = exchange_limits[2]['limit']

            # 21: sum of weight of the requests that always execute
            while(int(x_mbx_used_weight) + 21 <= request_weight_limit_per_min):
                usdt_balance = float(client.get_asset_balance(asset='USDT')['free'])
                usdt_dict = {
                    'balance': usdt_balance
                }

                crypto_dict = {
                    'currency': SYMBOL[:-4].title(),
                    'symbol': SYMBOL,
                    'minPrice': float(crypto_filters[0]['minPrice']),
                    'maxPrice': float(crypto_filters[0]['maxPrice']),
                    'price_tick_size': float(crypto_filters[0]['tickSize']),
                    'price': float(client.get_symbol_ticker(symbol=SYMBOL)['price']),
                    'minQty': float(crypto_filters[2]['minQty']),
                    'maxQty': float(crypto_filters[2]['maxQty']),
                    # At the momment 0.1 step size for quantity
                    'quantity_step_size': float(crypto_filters[2]['stepSize']),
                    'balance': float(client.get_asset_balance(asset=ASSET)['free'])
                }

                transaction = {'client': client, 'crypto_dict': crypto_dict, 'usdt_dict': usdt_dict}
                os.system('clear')

                x_mbx_used_weight = client.response.headers['x-mbx-used-weight']
                print(f"Running...\n")
                print(f"x-mbx-used-weight: {x_mbx_used_weight}")
                print(f"x-mbx-weight-limit-per-minute: {request_weight_limit_per_min}")
                print()

                print_info(crypto_dict, usdt_dict)

                if(int(x_mbx_used_weight) + ORDER_REQUEST_WEIGHT <= request_weight_limit_per_min):
                    transact(transaction, BUY_PRICE, SELL_PRICE)

                sleep(TIME_INTERVAL)
                # After the sleep it might have been reseted so we calculate it again
                x_mbx_used_weight = client.response.headers['x-mbx-used-weight']

        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            send_msg(f"Something went wrong:\n{e}\n Restarting...")
            print(e)
            sleep(90)
            continue
        


if __name__ == '__main__':
    main()
