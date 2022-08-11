import json, contracts, argparse, table_manager, sys
from collections import OrderedDict
from data_models import Ask, Bid, Trade
from web3 import Web3
import endpoints as data
import streamlit as st
import matplotlib.pyplot as plt

# parse nft id from a longer string
def parse_nft_id(tokensetID: str) -> str:
    split = tokensetID.split(":", 2)

    return split[2]

# converts various ways of spelling marketplaces into the names accepted by the reservoir.tools API
def convert_marketplace_name(marketplace: str = None) -> str:
    OS = "OpenSea"
    LR = "LooksRare"
    X2 = "X2Y2"

    if marketplace == None:
        marketplace = input("Exchange name (opensea, looksrare, x2y2): ")

    conversions = {
        "Opensea": OS,
        "opensea": OS,
        "seaport": OS,
        "Looksrare": LR,
        "looksrare": LR,
        "looks-rare": LR,
        "x2y2": X2
    }

    try:
        return conversions[marketplace]
    except:
        print("invalid marketplace name")
        print(marketplace)
        return convert_marketplace_name()

# process marketplace names
def process_marketplace_names(marketplaces: list) -> list:
    if len(marketplaces) != 0:
        for i in range(len(marketplaces)):
            marketplaces[i] = convert_marketplace_name(marketplaces[i])

        adding_more = (input("add another marketplace? [Y/n]: ") == "Y")
    else:
        adding_more = True
    
    while adding_more:
        marketplaces.append(convert_marketplace_name())
        adding_more = (input("add another marketplace? [Y/n]: ") == "Y")

    return marketplaces

# gets user input in compliance w/ reservoir.tools accepted marketplace names
def get_input_names() -> str:
    marketplaces = []

    process_marketplace_names(marketplaces)

    return marketplaces

# returns a project name from a contract address
def name_from_contract(contract: str) -> str:
    contract_to_name = {v: k for k, v in contracts.contract_data.items()}

    return contract_to_name[contract]

# gets project contract address from project name
def get_contract_address(verbose: bool = True, collection: str = None) -> str:
    contract_data = contracts.contract_data

    if verbose:
        print("Contracts")
        for contract in contract_data.keys():
            print(contract + ": " + contract_data[contract])

    if collection == None:
        collection = input("Project Name: ")

    try:
        return contract_data[collection]
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
def get_data_type(choice: str = None) -> str:
    if choice == None:
        choice = input("ask, ask distribution, bid, or trade data: ")

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
        "t":"trades",
        "ask_distribution":"ask_distribution",
        "ask-distribution":"ask_distribution",
        "ask distribution": "ask_distribution"
    }

    try:
        return conversions[choice]
    except:
        print("invalid data type")
        return get_data_type(arguments = False)

def get_configs():
    parser = argparse.ArgumentParser("Provide information about the data you want to query")
    parser.add_argument('--collection', dest='collection', type=str, help='[Cryptopunks, Moonbirds, Otherdeed, Goblintown, BAYC, MAYC, CloneX, Meebits, Doodles, Azuki, Veefriends]')
    parser.add_argument('--data_type', dest='data_type', type=str, help='asks, bids, trades, and ask distribution')
    parser.add_argument('--marketplaces', dest='marketplaces', type=str, nargs="+", help='marketplace[s] to process data for. Opensea, Looksrare, and X2Y2 supported. ')
    parser.add_argument('--store_data', dest='store_data', type=bool, help='Choose whether to store data on .db file. (True, False)')
    parser.add_argument('--verbose', dest='verbose', type=bool, help='Choose whether scraped data is displayed on CLI (True, False)')
    args = parser.parse_args()

    args.contract_address = get_contract_address(verbose = False, collection = args.collection)
    args.data_type = get_data_type(args.data_type)
    args.marketplace = process_marketplace_names(args.marketplaces)

    data_management_configs = get_data_preferences(store_data = args.store_data, verbose = args.verbose, data_type = args.data_type)
    args.store_data = data_management_configs["storage_preferences"]
    args.verbose = data_management_configs["verbose"]

    return args

# inserts data into table
def insert_data(detailed_data: list, type: str) -> None:
    for detailed_piece_of_data in detailed_data:
        try:
            table_manager.insert_order(detailed_piece_of_data, type)
        except:
            sys.exit("writing data failed -- try resetting database file")

# creates a bar chart
def bar_chart(marketplace_listings: dict) -> None:
    project = name_from_contract(contract)
    marketplaces = list(marketplace_listings.keys())
    listings = list(marketplace_listings.values())

    figure = plt.figure(figsize = (10, 5))

    plt.bar(marketplaces, listings)
    plt.xlabel("Marketplace")
    plt.ylabel("# of Listings")
    plt.title(f"# of Listings for {project} Across Marketplaces")

    st.pyplot(figure)

# gets storage and output preferences
def get_data_preferences(store_data: bool = None, verbose: bool = None, data_type: bool = None) -> json:
    if data_type == "ask_distribution":
        verbose = False
        store_data = True
    else:
        if store_data == None:
            store_data = (input("Store data in .db file? [Y/n]: ") == "Y")
        if not store_data:
            verbose = True
        elif verbose == None:
            verbose = input("Output data to CLI? [Y/n]: ") == "Y"
        
    return {
        "storage_preferences": store_data,
        "verbose": verbose
    }

# converts ask JSON data to ask objects
def parse_asks(orders: list, ask_count: dict, marketplace_asks: json, detailed_asks: list, min_price: int, max_price: int) -> None:
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

        if marketplace in target_marketplaces:
            ask_count[marketplace] += 1
            if ask["tokenSetId"] not in token_ids and value >= min_price and value <= max_price: # only look at asks on the given marketplace that haven't been added yet below the max price
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
def parse_trades(trades: list, detailed_trades: list) -> None:
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

        if marketplace in target_marketplaces and trade["id"] not in token_ids:
            parsed_trade = Trade(project_name, id, currency, price, marketplace, trade_timestamp, buyer, seller, "ETH", tx_id, offer_type, fee)
            detailed_trades.append(parsed_trade)

            token_ids.append(trade["id"])

# manage asks
def manage_asks(verbose: bool = True, key: str = data.get_reservoir_api_key()) -> list:
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

        parse_asks(orders, ask_count, marketplace_asks = marketplace_asks, detailed_asks = detailed_asks, min_price = min_price, max_price = max_price)

    marketplace_asks = dict(OrderedDict(sorted(marketplace_asks.items()))) # sort the orderbook by price

    # print out the data in an easily copiable format so that it can be pasted into excel, google sheets, etc and store it in a .db file 
    if verbose:
        print(f"Asks at each round ETH value from {min_price} to {max_price}:")

    for value in marketplace_asks.keys():
        if verbose:
            print(str(value) + ":" + str(marketplace_asks[value]))
        total += marketplace_asks[value]

    if total == len(detailed_asks) and store_data:
        insert_data(detailed_asks, "ask")

    print(f"\n{ask_count}")

    return detailed_asks

# manage ask distribution
def manage_ask_distribution(create_bar_chart = True) -> dict:
    manage_asks(verbose = False)
    parsed_ask_count = {}

    for key in ask_count.keys():
        if key in target_marketplaces:
            parsed_ask_count[key] = ask_count[key]

    if create_bar_chart:
        bar_chart(parsed_ask_count)

    return parsed_ask_count

# manage bids
def manage_bids() -> None:
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

    if store_data:
        insert_data(detailed_bids, "bid")

    if verbose:
        for bid in detailed_bids:
            print(f"Marketplace: {bid.marketplace}\n Project: {bid.project_name}\n Currency: {bid.currency}\n Value: {bid.value}\n Created At: {bid.created_at}\n NFT ID: {bid.nft_id}\n Bid Type: {bid.bid_type}\n")

# manage trades
def manage_trades(store_data: bool = True, key: str = data.get_reservoir_api_key()) -> None:
    detailed_trades = []
    continuation = None

    for i in range(15):
        trade_data = data.get_trades(contract, key, continuation)
        trades = trade_data["trades"]
        continuation = trade_data["continuation"]

        parse_trades(trades, detailed_trades)

    if store_data:
        insert_data(detailed_trades, "trade")

    if verbose:
        for trade in detailed_trades:
            print(f"Marketplace: {trade.marketplace} \n Project: {trade.project_name} \n Currency: {trade.currency} \n Value: {trade.value} \n Created At: {trade.timestamp} \n")

# instance variables
configs = get_configs()
contract = configs.contract_address
data_type = configs.data_type
target_marketplaces = configs.marketplace
store_data = configs.store_data
verbose = configs.verbose
ask_count = {"OpenSea": 0, "LooksRare": 0, "X2Y2": 0, "atomic0": 0}
token_ids = []

print("fetching data...\n")

# pull and organize ask data
if data_type == "asks":
    manage_asks()

# pull and organize ask distribution data
if data_type == "ask_distribution":
    manage_ask_distribution()

# pull and organize bid data
if data_type == "bids":
    manage_bids()

# pull and organize trade data
if data_type == "trades":
    manage_trades()