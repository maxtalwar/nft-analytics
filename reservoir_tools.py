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
    print(response.text)

    return json.loads(response.text)["key"]

def get_open_asks(contract, key):
    url = f"https://api.reservoir.tools/orders/asks/v2?contracts={contract}&includePrivate=true&limit=1000"

    headers = {
        "Accept": "*/*",
        "x-api-key": key
    }

    response = json.loads(requests.get(url, headers=headers).text)["orders"]

    return response

contract = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
key = get_api_key()
marketplace_asks = {}
total = 0

asks = get_open_asks(contract, key)

for ask in asks:
    name = ask["source"]["name"]
    rounded_value = round(ask["price"], 1)

    if (name not in marketplace_asks.keys()):
        marketplace_asks[name] = {}
    if (rounded_value not in marketplace_asks[name].keys()):
        marketplace_asks[name][rounded_value] = 1
    else:
        marketplace_asks[name][rounded_value] += 1

    total += 1

for marketplace in marketplace_asks:
    marketplace_asks[marketplace] = dict(OrderedDict(sorted(marketplace_asks[marketplace].items())))
    print(marketplace, marketplace_asks[marketplace])
    print("\n")


print(total)