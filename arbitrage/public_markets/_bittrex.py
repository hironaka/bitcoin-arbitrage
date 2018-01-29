import urllib.request
import urllib.error
import urllib.parse
import json
import sys
import time
from collections import defaultdict
from arbitrage.public_markets.market import Market
from arbitrage import config
import hmac
import hashlib

DEFAULT_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "*/*",
    "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"
}

class Bittrex(Market):
    def __init__(self, currency, code):
        super().__init__(currency)
        self.code = code
        self.update_rate = config.refresh_rate

    def update_depth(self):
        url = 'https://bittrex.com/api/v1.1/public/getorderbook?type=both&market=' + self.code
        depth = self.json_get(url)
        if not depth['success']:
            print(self.code + ' fail: ' + depth['message'])
            return
        self.depth = self.format_depth(depth["result"])

    def update_balances(self):
        url = 'https://bittrex.com/api/v1.1/account/getbalances?'
        balances = self.json_get_auth(url)
        if not balances['success']:
            print(self.code + ' fail: ' + balances['message'])
            return
        available_balances = {}
        for balance in balances['result']:
            available_balances[balance['Currency']] = balance['Available']
        print("balances:" + str(available_balances))
        return available_balances

    def json_get(self, url, headers=DEFAULT_HEADERS):
        req = urllib.request.Request(url, None, headers=headers)
        res = urllib.request.urlopen(req)
        return json.loads(res.read().decode('utf8'))

    def sort_and_format(self, l, reverse):
        r = []
        for i in l:
            r.append({'price': float(i['Rate']), 'amount': float(i['Quantity'])})
        r.sort(key=lambda x: float(x['price']), reverse=reverse)
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['buy'], True)
        asks = self.sort_and_format(depth['sell'], False)
        return {'asks': asks, 'bids': bids}
