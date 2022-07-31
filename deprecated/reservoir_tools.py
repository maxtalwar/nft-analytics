import requests, json
from collections import OrderedDict

def get_open_asks(contract):
    url = f"https://api.reservoir.tools/orders/asks/v2?contracts={contract}&includePrivate=true&limit=999"

    headers = {
        "Accept": "*/*",
        "x-api-key": "demo-api-key"
    }

<<<<<<< Updated upstream:reservoir_tools.py
    response = json.loads(requests.get(url, headers=headers).text)["orders"]
=======
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

def parse_asks(asks):
    total = 0
>>>>>>> Stashed changes:deprecated/reservoir_tools.py

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

    return total

<<<<<<< Updated upstream:reservoir_tools.py
=======
contract = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
continuation = None
key = get_api_key()
>>>>>>> Stashed changes:deprecated/reservoir_tools.py
marketplace_asks = {}
contract = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
total = 0

<<<<<<< Updated upstream:reservoir_tools.py
asks = get_open_asks(contract)

for ask in asks:
    name = ask["source"]["name"]
    rounded_value = round(ask["price"], 1)
=======
>>>>>>> Stashed changes:deprecated/reservoir_tools.py

for i in range(5):
    data = get_open_asks(contract, key, continuation)
    asks = data["orders"]
    continuation = data["continuation"]

    total += parse_asks(asks)

for marketplace in marketplace_asks:
    marketplace_asks[marketplace] = dict(OrderedDict(sorted(marketplace_asks[marketplace].items())))
    print(marketplace, marketplace_asks[marketplace])
    print("\n")


print(total)