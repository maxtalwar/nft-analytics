import requests, json
from collections import OrderedDict
import contracts
from data_models import Ask
import table_manager
import math

# gets an API key from the reservoir.tools API
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

# gets the floor price for a specific project
def get_floor_price():
    url = f"https://api.reservoir.tools/collection/v3?id={contract}&includeTopBid=false"

    headers = {
        "Accept": "*/*",
        "x-api-key": key
    }

    response = json.loads(requests.get(url, headers=headers).text)

    return int(math.floor(response["collection"]["floorAsk"]["price"]))
    

# gets open asks on a specific project from the reservoir API
def get_open_asks(contract, key, continuation=None):
    url = f"https://api.reservoir.tools/orders/asks/v2?contracts={contract}&includePrivate=false&limit=100"

    if continuation != None:
        url += f"&continuation={continuation}"

    headers = {
        "Accept": "*/*",
        "x-api-key": key
    }

    try:
        response = json.loads(requests.get(url, headers=headers).text)
    except:
        print("504 Error: Gateway timeout")

    return {
        "orders": response["orders"], 
        "continuation": response["continuation"]
    }

def parse_nft_id(tokensetID):
    split = tokensetID.split(":", 2)

    return split[2]

# returns the former marketplace orders + new ones parsed
def parse_asks(orders):
    for ask in orders:
        try:
            name = ask["source"]["name"]
        except:
            name = convert_marketplace_name(ask["kind"])

        project_name = ask['metadata']['data']['collectionName']
        nft_id = parse_nft_id(ask["tokenSetId"])
        currency = "ETH"
        price = ask["price"]
        marketplace = marketplace_name
        created_at = ask["createdAt"]
        expires_on = ask["expiration"]
        maker = ask["maker"]

        value = int(round(price, 0))

        if name == marketplace_name and ask["tokenSetId"] not in token_ids and value >= min_price and value <= max_price: # only look at asks on the given marketplace that haven't been added yet below the max price
            
            if value in marketplace_orders.keys(): # if the rounded value of the ask is already a key in the dict, increment it. Otherwise create a new key
                marketplace_orders[value] += 1
            else:
                marketplace_orders[value] = 1

            order = Ask(project_name, nft_id, currency, price, marketplace, created_at, expires_on, maker)
            detailed_asks.append(order)
            
            token_ids.append(ask["tokenSetId"])

    return {
        "price_ask_matchings": marketplace_orders,
        "asks": detailed_asks
    }

# converts various ways of spelling marketplaces into the names accepted by the reservoir.tools API
def convert_marketplace_name(input):
    OS = "OpenSea"
    LR = "LooksRare"
    X2 = "X2Y2"

    conversions = {
        "Opensea": OS,
        "opensea": OS,
        "seaport": OS,
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

# gets project contract address from project name
def get_contract_address(verbose = True):
    contract_data = contracts.contract_data

    if verbose:
        print("Contracts")
        for contract in contract_data.keys():
            print(contract + ": " + contract_data[contract])

    project_name = input("Project Name: ")

    try:
        return contract_data[project_name]
    except:
        print("invalid project name")
        return get_contract_address(verbose = False)

# fills the marketplace orders dict with the keys for the appropriate NFT prices
def fill_dict(start, end):
    dictionary = {}
    for i in range(start, end+1):
        dictionary[i] = 0

    return dictionary

# instance variables
contract = get_contract_address()
marketplace_name = get_input_name()
key = get_api_key()
min_price = get_floor_price()
max_price = min_price*3
total = 0
marketplace_orders = fill_dict(min_price, max_price)
detailed_asks = []
token_ids = []
continuation = None

print("fetching data... \n")

# continually fetches the next page of asks and updates the marketplace orders with the next asks
for i in range(15):
    asks = get_open_asks(contract, key, continuation)
    orders = asks["orders"]
    continuation = asks["continuation"]

    parsed_asks = parse_asks(orders)

    marketplace_orders = parsed_asks["price_ask_matchings"]
    detailed_asks = parsed_asks["asks"]

marketplace_orders = dict(OrderedDict(sorted(marketplace_orders.items()))) # sort the orderbook by price

# print out the data in an easily copiable format so that it can be pasted into excel, google sheets, etc

print(f"Asks at each round ETH value from {min_price} to {max_price}:")

for value in marketplace_orders.keys():
    print(str(value) + ":" + str(marketplace_orders[value]))
    total += marketplace_orders[value]

if total == len(detailed_asks):
    print("\n")
    for detailed_order in detailed_asks:
        table_manager.insert_orders(detailed_order)