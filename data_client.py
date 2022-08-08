import requests, json
from collections import OrderedDict
import contracts
from data_models import Ask, Bid, Trade
import table_manager, math, os
import argparse
from web3 import Web3
import endpoints as data

# parse nft id from a longer string
def parse_nft_id(tokensetID: str) -> str:
    split = tokensetID.split(":", 2)

    return split[2]

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

# returns a project name from a contract address
def name_from_contract(contract: str) -> str:
    contract_to_name = {v: k for k, v in contracts.contract_data.items()}

    return contract_to_name[contract]

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

# gets data type from command line arguments
def get_data_type() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_type', dest='data_type', type=str, help='data type to get data about')
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
        "a":"asks",
        "Trades":"trades",
        "Trade":"trades",
        "trade":"trades",
        "trades":"trades",
        "t":"trades"
    }

    try:
        return conversions[choice]
    except:
        print("invalid data type")
        return get_data_type()

# inserts data into table
def insert_data(detailed_data, type):
    for detailed_piece_of_data in detailed_data:
        try:
            table_manager.insert_order(detailed_piece_of_data, type)
        except:
            print("writing data failed -- try resetting database file")
            quit()

# converts ask JSON data to ask objects
def parse_asks(orders: list, marketplace_asks: json, detailed_asks: list, min_price: int, max_price: int) -> None:
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

            order = Ask(project_name, nft_id, currency, price, marketplace, created_at, expires_on, maker, "ETH")
            detailed_asks.append(order)
            
            token_ids.append(ask["tokenSetId"])

# converts bid JSON data to bid objects
def parse_looksrare_bids(bids: list, detailed_bids: list) -> None:
    makers = []
    for bid in bids:
        marketplace = "LooksRare"
        project_name = name_from_contract(bid["collectionAddress"])
        currency = "ETH"
        price = str(float(bid["price"])/(10**18))
        created_at = bid["startTime"]
        maker = bid["signer"]
        
        strategy = bid["strategy"]
        if strategy == "0x56244Bb70CbD3EA9Dc8007399F61dFC065190031":
            bid_type = "single"
        else:
            bid_type = "collection"

        if bid["hash"] not in token_ids:
            if bid_type == "single":
                nft_id = bid["tokenId"]
            else:
                nft_id = "N/A"

            parsed_bid = Bid(project_name, nft_id, currency, price, marketplace, created_at, maker, bid_type, "ETH")
            detailed_bids.append(parsed_bid)

            token_ids.append(bid["hash"])
            makers.append(maker)

# converts trade JSON data to a trade object
def parse_trades(trades: list) -> None:
    for trade in trades:
        project_name = name_from_contract(Web3.toChecksumAddress(trade["token"]["contract"]))
        id = trade["token"]["tokenId"]
        currency = "ETH"
        price = trade["price"]
        marketplace = trade["orderSource"]
        trade_timestamp = trade["timestamp"]
        buyer = trade["from"]
        seller = trade["to"]
        tx_id = trade["txHash"]
        offer_type = trade["orderSide"]
        
        fee_rate = 0
        if marketplace == "OpenSea":
            fee_rate = 0.025
        if marketplace == "LooksRare":
            fee_rate = 0.02
        if marketplace == "X2Y2":
            fee_rate = 0.005

        usdPrice = trade["usdPrice"]
        try:
            fee = usdPrice*fee_rate
        except:
            fee = 0

        if marketplace == target_marketplace and trade["id"] not in token_ids:
            parsed_trade = Trade(project_name, id, currency, price, marketplace, trade_timestamp, buyer, seller, "ETH", tx_id, offer_type, fee)
            detailed_trades.append(parsed_trade)

            token_ids.append(trade["id"])

def manage_asks():
    min_price = data.get_floor_price(contract, key)
    max_price = min_price*3
    marketplace_asks = fill_dict(min_price, max_price)
    detailed_asks = []
    continuation = None
    total = 0

    # continually fetches the next page of asks and updates the marketplace orders with the next asks
    for i in range(15):
        asks = data.get_open_asks(contract, key, continuation)
        orders = asks["orders"]
        continuation = asks["continuation"]

        parse_asks(orders, marketplace_asks = marketplace_asks, detailed_asks = detailed_asks, min_price = min_price, max_price = max_price)

    marketplace_asks = dict(OrderedDict(sorted(marketplace_asks.items()))) # sort the orderbook by price

    # print out the data in an easily copiable format so that it can be pasted into excel, google sheets, etc
    print(f"Asks at each round ETH value from {min_price} to {max_price}:")

    for value in marketplace_asks.keys():
        print(str(value) + ":" + str(marketplace_asks[value]))
        total += marketplace_asks[value]

    if total == len(detailed_asks):
        print("\n")
        insert_data(detailed_asks, "ask")

def manage_bids():
    detailed_bids = []
    continuation = None

    # single bids
    for i in range(15):
        single_bids = data.get_looksrare_bids(contract = contract, continuation = continuation)
        try:
            continuation = single_bids[-1]["hash"]
        except:
            continuation = None

        parse_looksrare_bids(single_bids, detailed_bids = detailed_bids)

    # collection bids
    for i in range(15):
        collection_bids = data.get_looksrare_bids(contract = contract, strategy = "0x86F909F70813CdB1Bc733f4D97Dc6b03B8e7E8F3")
        parse_looksrare_bids(collection_bids, detailed_bids = detailed_bids)

    insert_data(detailed_bids, "bid")

# instance variables
contract = get_contract_address()
target_marketplace = get_input_name()
key = data.get_reservoir_api_key()
data_type = get_data_type()
token_ids = []
continuation = None

print("fetching data... \n")

# pull and organize ask data
if data_type == "asks":
    manage_asks()

# pull and organize bid data
if data_type == "bids":
    manage_bids()

# pull and organize trade data
if data_type == "trades":
    detailed_trades = []

    for i in range(45):
        trade_data = data.get_trades(contract, key, continuation)
        trades = trade_data["trades"]
        continuation = trade_data["continuation"]

        parse_trades(trades)

    insert_data(detailed_trades, "trade")

print("data parsing complete")