import os
import time

from pybit import usdt_perpetual

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('api_key')
secret = os.getenv('secret')


session = usdt_perpetual.HTTP(
        endpoint='https://api.bybit.com',
        api_key=api_key,
        api_secret=secret,
    )

ETHUSDT = 'ETHUSDT'
BTCUSDT = 'BTCUSDT'
LIMIT = 60          # кол-во свечей
INTERVAL = 1        # минутные свечи


def change(ticker):
    """Записываем изменения цены закрытия от свечи к свече.
    """
    change_ethbtc = []
    for i in range(1, len(ticker)):
        x = (ticker[i - 1] / ticker[i]) * 100 - 100
        change_ethbtc.append(x)

    return change_ethbtc


def get_ethbtc():
    """Получаем список изменений цены ETH к BTC
    """
    kline_eth = session.query_kline(    # получить свечи
        symbol=ETHUSDT,
        interval=INTERVAL,
        limit=100,
        from_time=int(time.time() - LIMIT * 60)
    )
    kline_eth = kline_eth['result']
    eth_prices = []
    for each in kline_eth:              # из каждой свечи
        close = each['close']           # берем данные о закрытии
        eth_prices.append(close)        # накапливаем в списке

    kline_btc = session.query_kline(    # получить свечи
        symbol=BTCUSDT,
        interval=INTERVAL,
        limit=100,
        from_time=int(time.time() - LIMIT * 60)
    )
    kline_btc = kline_btc['result']
    btc_prices = []
    for each in kline_btc:          # из каждой свечи
        close = each['close']       # берем данные о закрытии
        btc_prices.append(close)    # накапливаем в списке
    ethbtc_prices = [eth/btc for eth, btc in zip(eth_prices, btc_prices)]

    return change(ethbtc_prices)


def main():
    """Получаем изменение цены ETHUSDT с учётом изменения цены ETH к BTC,
    просто складываем значения, исходя из теории,
    что рост цены ETH к BTC усиливает собственный рост ETHUSDT,
    а снижение - ослабевает.
    """
    kline = session.query_kline(
        symbol=ETHUSDT,
        interval=INTERVAL,
        limit=100,
        from_time=int(time.time() - LIMIT * 60)
    )
    kline = kline['result']
    eth_prices = []
    for each in kline:
        close = each['close']
        eth_prices.append(close)
    change_ethusdt = change(eth_prices)
    change_ethbtc = get_ethbtc()
    return_data = [
        eth + btc for eth, btc in zip(change_ethusdt, change_ethbtc)
    ]
    gap = sum(return_data)
    if gap >= 1:
        print(f'Цена за час изменилась на {gap:.4f}%')
    time.sleep(5)
    main()


if __name__ == '__main__':
    main()
