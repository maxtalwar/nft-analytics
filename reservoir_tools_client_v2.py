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

# returns the former marketplace orders + new ones parsed
def parse_asks(orders):
    for ask in orders:
        try:
            name = ask["source"]["name"]
        except:
            name = convert_marketplace_name(ask["kind"])

        price = ask["price"]

        if name == marketplace_name and ask["tokenSetId"] not in token_ids and price < max_price: # only look at asks on the given marketplace that haven't been added yet below the max price
            value = int(round(price, 0))

            if value in marketplace_orders.keys(): # if the rounded value of the ask is already a key in the dict, increment it. Otherwise create a new key
                marketplace_orders[value] += 1
            else:
                marketplace_orders[value] = 1
            
            token_ids.append(ask["tokenSetId"])

    return marketplace_orders

# converts various ways of spelling marketplaces into the names accepted by the reservoir.tools API
def convert_marketplace_name(input):
    OS = "OpenSea"
    LR = "LooksRare"
    X2 = "X2Y2"

    conversions = {
        "Opensea": OS,
        "opensea": OS,
        "Looksrare": LR,
        "looksrare": LR,
        "looks-rare": LR,
        "x2y2": X2
    }

    return conversions[input]

# gets user input in compliance w/ reservoir.tools accepted marketplace names
def get_input_name():
    name = input("Exchange name (opensea, looksrare, x2y2): ")

    try:
        return convert_marketplace_name(name)
    except:
        print("invalid exchange name entered")
        return get_input_name()

def get_contract_address():
    contracts = {
        "Cryptopunks": "0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB",
        "Moonbirds": "0x23581767a106ae21c074b2276D25e5C3e136a68b",
        "Otherdeed": "0x34d85c9CDeB23FA97cb08333b511ac86E1C4E258",
        "Goblintown": "0xbCe3781ae7Ca1a5e050Bd9C4c77369867eBc307e",
        "BAYC": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
        "MAYC": "0x60E4d786628Fea6478F785A6d7e704777c86a7c6",
        "CloneX": "0x49cF6f5d44E70224e2E23fDcdd2C053F30aDA28B",
        "Meebits": "0x7Bd29408f11D2bFC23c34f18275bBf23bB716Bc7",
        "Doodles": "0x8a90CAb2b38dba80c64b7734e58Ee1dB38B8992e",
        "Azuki": "0xED5AF388653567Af2F388E6224dC7C4b3241C544",
        "Veefriends": "0xa3AEe8BcE55BEeA1951EF834b99f3Ac60d1ABeeB"
    }

    print("Contracts")
    for contract in contracts.keys():
        print(contract + ": " + contracts[contract])

    project_name = input("Project Name: ")

    return contracts[project_name]

def fill_dict(start, end):
    dictionary = {}
    for i in range(start, end+1):
        dictionary[i] = 0

    return dictionary

# instance variables
contract = get_contract_address()
marketplace_name = get_input_name()
key = get_api_key()
failed = 0
min_price = 18
max_price = 50
marketplace_orders = fill_dict(min_price, max_price)
token_ids = []
continuation = None

print("fetching data...")

# continually fetches the next page of asks and updates the marketplace orders with the next asks
for i in range(20):
    asks = get_open_asks(contract, key, continuation)
    orders = asks["orders"]
    continuation = asks["continuation"]

    marketplace_orders = parse_asks(orders)

marketplace_orders = dict(OrderedDict(sorted(marketplace_orders.items()))) # sort the orderbook by price

# print out the data in an easily copiable format so that it can be pasted into excel, google sheets, etc

print("\n")

for value in marketplace_orders.keys():
    print(str(marketplace_orders[value]))