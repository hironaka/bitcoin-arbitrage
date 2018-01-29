from arbitrage.public_markets._bittrex import Bittrex

class BittrexUSD(Bittrex):
    def __init__(self):
        super().__init__("USD", "USDT-BTC")
