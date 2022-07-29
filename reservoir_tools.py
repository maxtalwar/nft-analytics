import requests, json
from collections import OrderedDict

def get_open_asks(contract):
    url = f"https://api.reservoir.tools/orders/asks/v2?contracts={contract}&includePrivate=true&limit=999"

    headers = {
        "Accept": "*/*",
        "x-api-key": "demo-api-key"
    }

    response = json.loads(requests.get(url, headers=headers).text)["orders"]

    return response

marketplace_asks = {}
contract = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
total = 0

asks = get_open_asks(contract)

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