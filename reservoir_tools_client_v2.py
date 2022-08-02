import requests, json
from collections import OrderedDict
import contracts
from data_models import Ask, Bid, Trade
import table_manager, math, os
import argparse

# gets an API key from the reservoir.tools API
def get_api_key() -> json:
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
def get_floor_price() -> json:
    url = f"https://api.reservoir.tools/collection/v3?id={contract}&includeTopBid=false"

    headers = {
        "Accept": "*/*",
        "x-api-key": key
    }

    response = json.loads(requests.get(url, headers=headers).text)

    return int(math.floor(response["collection"]["floorAsk"]["price"]))

# gets open bids on a specific project
def get_open_bids(contract: str, key: str, continuation=None) -> json:
    url = f"https://api.reservoir.tools/orders/bids/v2?contracts={contract}&limit=100"

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
        os._exit()

    return {
        "bids": response["orders"],
        "continuation": response["continuation"]
    }

# gets open asks on a specific project from the reservoir API
def get_open_asks(contract: str, key: str, continuation=None) -> json:
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
        os._exit()

    return {
        "orders": response["orders"], 
        "continuation": response["continuation"]
    }

# parse nft id from a longer string
def parse_nft_id(tokensetID: str) -> str:
    split = tokensetID.split(":", 2)

    return split[2]

# returns the former marketplace orders + new ones parsed
def parse_asks(orders: list) -> None:
    for ask in orders:
        try:
            marketplace = ask["source"]["name"]
        except:
            marketplace = convert_marketplace_name(ask["kind"])

        project_name = ask['metadata']['data']['collectionName']
        nft_id = parse_nft_id(ask["tokenSetId"])
        currency = "ETH"
        price = ask["price"]
        created_at = ask["createdAt"]
        expires_on = ask["expiration"]
        maker = ask["maker"]

        value = int(round(price, 0))

        if marketplace == target_marketplace and ask["tokenSetId"] not in token_ids and value >= min_price and value <= max_price: # only look at asks on the given marketplace that haven't been added yet below the max price
            
            if value in marketplace_asks.keys(): # if the rounded value of the ask is already a key in the dict, increment it. Otherwise create a new key
                marketplace_asks[value] += 1
            else:
                marketplace_asks[value] = 1

            order = Ask(project_name, nft_id, currency, price, marketplace, created_at, expires_on, maker)
            detailed_asks.append(order)
            
            token_ids.append(ask["tokenSetId"])

def parse_bids(bids: list) -> dict:
    for bid in bids:
        try:
            marketplace = bid["source"]["name"]
        except:
            marketplace = convert_marketplace_name(bid["kind"])
        
        project_name = bid['metadata']['data']['collectionName']
        currency = "ETH"
        price = bid["price"]
        created_at = bid["createdAt"]
        maker = bid["maker"]
        bid_type = bid["rawData"]["kind"]

        if marketplace == target_marketplace and bid["tokenSetId"] not in token_ids:
            if bid_type == "single-token":
                nft_id = parse_nft_id(bid["tokenSetId"])

            bid = Bid(project_name, nft_id, currency, price, created_at, maker, bid_type)
            detailed_bids.append(bid)

            token_ids.append(bid["tokenSetID"])

# converts various ways of spelling marketplaces into the names accepted by the reservoir.tools API
def convert_marketplace_name(input: str) -> str:
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
def get_input_name() -> str:
    name = input("Exchange name (opensea, looksrare, x2y2): ")

    try:
        return convert_marketplace_name(name)
    except:
        print("invalid exchange name entered")
        return get_input_name()

# gets project contract address from project name
def get_contract_address(verbose = True) -> str:
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
def fill_dict(start: int, end: int) -> dict:
    dictionary = {}
    for i in range(start, end+1):
        dictionary[i] = 0

    return dictionary

def get_data_type() -> str:

    parser = argparse.ArgumentParser()
    parser.add_argument('-data_type', dest='data_type', type=str, help='data type to get data about')
    args = parser.parse_args()

    if args.data_type != None:
        choice = args.data_type
    else:
        choice = input("bid, ask, or trade data: ")

    conversions = {
        "Bids":"bids",
        "Bid":"bids",
        "bid":"bids",
        "bids":"bids",
        "b":"bids",
        "Asks":"asks",
        "Ask":"asks",
        "asks":"asks",
        "ask":"asks",
        "a":"asks"
    }

    try:
        return conversions[choice]
    except:
        print("invalid data type")
        return get_data_type()

# instance variables
contract = get_contract_address()
target_marketplace = get_input_name()
key = get_api_key()
token_ids = []
data_type = get_data_type()
continuation = None
total = 0

print("fetching data... \n")

# pull and organize ask data
if data_type == "asks":
    min_price = get_floor_price()
    max_price = min_price*3
    marketplace_asks = fill_dict(min_price, max_price)
    detailed_asks = []

    # continually fetches the next page of asks and updates the marketplace orders with the next asks
    for i in range(15):
        asks = get_open_asks(contract, key, continuation)
        orders = asks["orders"]
        continuation = asks["continuation"]

        parse_asks(orders)

    marketplace_asks = dict(OrderedDict(sorted(marketplace_asks.items()))) # sort the orderbook by price

    # print out the data in an easily copiable format so that it can be pasted into excel, google sheets, etc

    print(f"Asks at each round ETH value from {min_price} to {max_price}:")

    for value in marketplace_asks.keys():
        print(str(value) + ":" + str(marketplace_asks[value]))
        total += marketplace_asks[value]

    if total == len(detailed_asks):
        print("\n")
        for detailed_ask in detailed_asks:
            table_manager.insert_order(detailed_ask, "ask")

# pull and organize bid data
if data_type == "bids":
    detailed_bids = []

    for i in range(15):
        bid_data = get_open_bids(contract, key, continuation)
        print(bid_data)
        print("\n")
        bids = bid_data["bids"]
        continuation = bid_data["continuation"]

        parse_bids(bids)

    print("\n")

    for detailed_bid in detailed_bids:
        table_manager.insert_order(detailed_bid, "bid")