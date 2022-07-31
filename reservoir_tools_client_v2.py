import requests, json
from collections import OrderedDict

def get_api_key():
    url = "https://api.reservoir.tools/api-keys"

    payload = "appName=Marketplace_Indexer&email=proton0x%40photonmail.com&website=https%3A%2F%2Fgithub.com%2F0xphoton%2FNFT-Marketplaces"
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "x-api-key": "demo-api-key"
    }

    response = requests.post(url, data=payload, headers=headers)

    return json.loads(response.text)["key"]

def get_open_asks(contract, key, continuation=None):
    url = f"https://api.reservoir.tools/orders/asks/v2?contracts={contract}&includePrivate=false&limit=100"

    if continuation != None:
        url += f"&continuation={continuation}"

    headers = {
        "Accept": "*/*",
        "x-api-key": key
    }

    response = json.loads(requests.get(url, headers=headers).text)

    return {
        "orders": response["orders"], 
        "continuation": response["continuation"]
    }

def parse_asks(orders):
    for ask in orders:
        if ask["source"]["name"] == marketplace_name and ask["tokenSetId"] not in token_ids: # only look at asks on the given marketplace that haven't been added yet

            value = round(ask["price"], 1)

            if value in marketplace_orders.keys(): # if the rounded value of the ask is already a key in the dict, increment it. Otherwise create a new key
                marketplace_orders[value] += 1
            else:
                marketplace_orders[value] = 1
            
            token_ids.append(ask["tokenSetId"])

    return marketplace_orders


contract = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
marketplace_name = "OpenSea"
key = get_api_key()
marketplace_orders = {}
token_ids = []
continuation = None

print("fetching data from API...")

for i in range(5):
    asks = get_open_asks(contract, key, continuation)
    orders = asks["orders"]
    continuation = asks["continuation"]

    marketplace_orders = parse_asks(orders)

marketplace_orders = dict(OrderedDict(sorted(marketplace_orders.items()))) # sort the dict of orders

print(marketplace_orders)
print(len(marketplace_orders.keys()))