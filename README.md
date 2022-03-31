# Cryptobot
Bot for cryptocurrency trading using the Binance platform and API, includes a Telegram bot that messages you when an Order is placed, initial release.

## Usage
By setting `BUY_PRICE` and `SELL_PRICE` constants at `cryptobot.py` the bot continuously buys at the first price and sells at the second one.

### Usage scenario example:
Suppose you think "**ExampleCoin**" is gonna fluctuate from 40000$ to 45000$ for some days, and you have 500$ in USDT on your account for investing, by setting `BUY_PRICE = 40500` and `SELL_PRICE = 44500`, every time the price goes lower than 40500$ the bot will execute a buying action using all your USDT balance (to be modified later) and then when it goes up to 44500$ the bot will sell.

So, after the first buying, at 40500$, you'd have: (500\/40500) BTC = 0.012345679 BTC.

And then, after the first selling, when "**ExampleCoin**" reaches 44500$, you'd have: (0.012345679 * 44500)$ = 549.38 $

Resulting in an overall benefit of (549.38 - 500) = 49.38$.

## Things to fix/add/make better
- Add functionality/refactor to allow to make several orders with the corresponding profit calculation.
- Switch from http API calls to sockets usage (they're way more efficient).


## Disclaimer
This code is at a really early stage (and has a lot of room for growth), it was thought for personal use, I share it for educational purposes, I take no responsability for the problems the misuse or missunderstanding of this code can bring you, use at your own risk, or maybe use as inspiration to build your own :).
