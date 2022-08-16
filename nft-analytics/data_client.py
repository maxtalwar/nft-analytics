import json, contracts, table_manager, sys, CLI
from collections import OrderedDict
from data_models import Ask, Bid, Trade
from web3 import Web3
import endpoints as data
import streamlit as st
import matplotlib.pyplot as plt
from operator import itemgetter

# parse nft id from a longer string
def parse_nft_id(tokensetID: str) -> str:
    split = tokensetID.split(":", 2)

    return split[2]


# returns a project name from a contract address
def name_from_contract(contract: str) -> str:
    contract_to_name = {v: k for k, v in contracts.contract_data.items()}

    return contract_to_name[contract]


# fills the marketplace orders dict with the keys for the appropriate NFT prices
def fill_dict(start: int, end: int) -> dict:
    dictionary = {}
    for i in range(start, end + 1):
        dictionary[i] = 0

    return dictionary


# gets command line arguments
def get_configs():
    return CLI.get_configs()


# inserts data into table
def insert_data(detailed_data: list, type: str) -> None:
    for detailed_piece_of_data in detailed_data:
        if detailed_piece_of_data.marketplace == "X2Y2":
            try:
                table_manager.insert_order(detailed_piece_of_data, type)
            except:
                sys.exit("writing data failed -- try resetting database file")


# creates a bar chart of ask distributions across marketplaces
def marketplace_distribution_bar_chart(marketplace_listings: dict) -> None:
    project = name_from_contract(contract)
    marketplaces = list(marketplace_listings.keys())
    listings = list(marketplace_listings.values())

    figure = plt.figure(figsize=(10, 5))

    plt.bar(marketplaces, listings)
    plt.ylabel("# of Listings")
    plt.title(f"# of Listings for {project} Across Marketplaces")

    st.pyplot(figure)


# creates a bar chart of ask distributions across prices on a single marketplace
def price_distribution_bar_chart(listings_by_price: dict, marketplace: str) -> None:
    project = name_from_contract(contract)
    prices = list(listings_by_price.keys())
    listings = list(listings_by_price.values())

    figure = plt.figure(figsize=(10, 5))

    plt.bar(prices, listings)
    plt.xlabel("Listing Price")
    plt.ylabel("# of Listings")
    plt.title(f"# of {project} Listings across prices on {marketplace}")

    st.pyplot(figure)


# converts ask JSON data to ask objects
def parse_asks(
    orders: list,
    ask_count: dict,
    marketplace_asks: json,
    detailed_asks: list,
    min_price: int,
    max_price: int,
) -> None:
    for ask in orders:
        try:
            marketplace = ask["source"]["name"]
        except:
            marketplace = CLI.convert_marketplace_name(ask["kind"])

        project_name = ask["metadata"]["data"]["collectionName"]
        nft_id = parse_nft_id(ask["tokenSetId"])
        currency = "ETH"
        price = ask["price"]
        created_at = ask["createdAt"]
        expires_on = ask["expiration"]
        maker = ask["maker"]

        value = int(round(price, 0))

        if marketplace in target_marketplaces:
            ask_count[marketplace] += 1
            if (
                (marketplace + ask["tokenSetId"]) not in token_ids
                and price <= max_price
            ):  # only look at asks on the given marketplace that haven't been added yet below the max price
                if (
                    value in marketplace_asks[marketplace].keys()
                ):  # if the rounded value of the ask is already a key in the dict, increment it. Otherwise create a new key
                    marketplace_asks[marketplace][value] += 1
                else:
                    marketplace_asks[marketplace][value] = 1

                order = Ask(
                    project_name,
                    nft_id,
                    currency,
                    price,
                    marketplace,
                    created_at,
                    expires_on,
                    maker,
                    "ETH",
                )
                detailed_asks.append(order)

                token_ids.append((marketplace + ask["tokenSetId"]))


# converts bid JSON data to bid objects
def parse_looksrare_bids(bids: list, detailed_bids: list) -> None:
    makers = []
    for bid in bids:
        marketplace = "LooksRare"
        project_name = name_from_contract(bid["collectionAddress"])
        currency = "ETH"
        price = str(float(bid["price"]) / (10**18))
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

            parsed_bid = Bid(
                project_name,
                nft_id,
                currency,
                price,
                marketplace,
                created_at,
                maker,
                bid_type,
                "ETH",
            )
            detailed_bids.append(parsed_bid)

            token_ids.append(bid["hash"])
            makers.append(maker)


# converts trade JSON data to a trade object
def parse_trades(trades: list, detailed_trades: list) -> None:
    for trade in trades:
        project_name = name_from_contract(
            Web3.toChecksumAddress(trade["token"]["contract"])
        )
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
            fee = usdPrice * fee_rate
        except:
            fee = 0

        if marketplace in target_marketplaces and trade["id"] not in token_ids:
            parsed_trade = Trade(
                project_name,
                id,
                currency,
                price,
                marketplace,
                trade_timestamp,
                buyer,
                seller,
                "ETH",
                tx_id,
                offer_type,
                fee,
            )
            detailed_trades.append(parsed_trade)

            token_ids.append(trade["id"])


# manage asks
def manage_asks(verbose: bool = True, key: str = data.get_reservoir_api_key(), bar_chart = True) -> list:
    min_price = data.get_floor_price(contract, key)
    max_price = min_price * 3
    marketplace_asks = {}
    detailed_asks = []
    continuation = None
    total = 0
    x2y2_total = 0

    for marketplace in target_marketplaces:
        marketplace_asks[marketplace] = fill_dict(min_price, max_price)

    # continually fetches the next page of asks and updates the marketplace orders with the next asks
    for i in range(15):
        asks = data.get_open_asks(contract, key, continuation)
        orders = asks["orders"]
        continuation = asks["continuation"]

        parse_asks(
            orders,
            ask_count,
            marketplace_asks=marketplace_asks,
            detailed_asks=detailed_asks,
            min_price=min_price,
            max_price=max_price,
        )

    marketplace_asks = dict(
        OrderedDict(sorted(marketplace_asks.items()))
    )  # sort the orderbook by price

    # print out the data in an easily copiable format so that it can be pasted into excel, google sheets, etc and store it in a .db file
    if verbose:
        print(f"Asks at each round ETH value from {min_price} to {max_price}:")

    for marketplace in marketplace_asks.keys():
        print(marketplace)
        for value in marketplace_asks[marketplace].keys():
            if verbose:
                print(str(value) + ":" + str(marketplace_asks[marketplace][value]))
            total += marketplace_asks[marketplace][value]

    if total == len(detailed_asks):
        if store_data:
            insert_data(detailed_asks, "ask")
        if bar_chart:
            for marketplace in marketplace_asks.keys():
                price_distribution_bar_chart(marketplace_asks[marketplace], marketplace)


    print(f"\n{ask_count}")

    return detailed_asks


# manage ask distribution
def manage_ask_distribution() -> dict:
    manage_asks(verbose=False)
    parsed_ask_count = {}

    for key in ask_count.keys():
        if key in target_marketplaces:
            parsed_ask_count[key] = ask_count[key]

    marketplace_distribution_bar_chart(parsed_ask_count)

    return parsed_ask_count


# manage bids
def manage_bids() -> list:
    detailed_bids = []
    continuation = None

    # single bids
    for i in range(15):
        single_bids = data.get_looksrare_bids(
            contract=contract, continuation=continuation
        )
        try:
            continuation = single_bids[-1]["hash"]
        except:
            continuation = None

        parse_looksrare_bids(single_bids, detailed_bids=detailed_bids)

    # collection bids
    for i in range(15):
        collection_bids = data.get_looksrare_bids(
            contract=contract, strategy="0x86F909F70813CdB1Bc733f4D97Dc6b03B8e7E8F3"
        )
        parse_looksrare_bids(collection_bids, detailed_bids=detailed_bids)

    if store_data:
        insert_data(detailed_bids, "bid")

    if verbose:
        for bid in detailed_bids:
            print(
                f"Marketplace: {bid.marketplace}\n Project: {bid.project_name}\n Currency: {bid.currency}\n Value: {bid.value}\n Created At: {bid.created_at}\n NFT ID: {bid.nft_id}\n Bid Type: {bid.bid_type}\n"
            )

    return detailed_bids


# search for arb opportunities
def find_arb_opportunities() -> list:
    asks = manage_asks(verbose=False)
    bids = manage_bids()
    order_book = {}
    tokens = []
    opportunities = []
    number_of_opportunities = 0

    for ask in asks:
        tokens.append(ask.nft_id)

    for token in tokens:
        order_book[token] = {"asks": [], "bids": []}

    for ask in asks:
        simple_ask = {
            "price": ask.value,
            "currency": ask.currency,
            "marketplace": ask.marketplace,
        }

        order_book[ask.nft_id]["asks"].append(simple_ask)

    for bid in bids:
        simple_bid = {
            "price": bid.value,
            "currency": bid.currency,
            "marketplace": bid.marketplace,
            "bid type": bid.bid_type,
        }

        if bid.bid_type == "single":
            try:
                order_book[bid.nft_id]["bids"].append(simple_bid)
            except:
                order_book[bid.nft_id] = {"asks": [], "bids": []}
        else:
            for token in order_book.keys():
                order_book[token]["bids"].append(simple_bid)

    for token in tokens:
        order_book[token]["asks"] = sorted(
            order_book[token]["asks"], key=itemgetter("price")
        )
        order_book[token]["bids"] = sorted(
            order_book[token]["bids"], key=itemgetter("price"), reverse=True
        )

    for token in tokens:
        for bid in order_book[token]["bids"]:
            for ask in order_book[token]["asks"]:
                if float(bid["price"]) > float(ask["price"]):
                    opportunities.append(
                        {
                            "bid": bid,
                            "ask": ask,
                        }
                    )

                    number_of_opportunities += 1

        try:
            max_bid = float(order_book[token]["bids"][0]["price"])
        except:
            max_bid = 0
        min_ask = float(order_book[token]["asks"][0]["price"])

        if max_bid > min_ask:
            print(f"token id: {token}")
            print(f"max bid: {max_bid}")
            print(f"min ask: {min_ask}")

        print(token)
        print("Asks: ")
        for ask in order_book[token]["asks"]:
            print(ask)
        print("Bids: ")
        for bid in order_book[token]["bids"]:
            print(bid)
        print(f"max bid: {max_bid}")
        print(f"min ask: {min_ask}")

        print("\n")

    print(
        f"Total opportunities across OpenSea, X2Y2, and LooksRare: {number_of_opportunities}"
    )

    return opportunities


# manage trades
def manage_trades(
    store_data: bool = True, key: str = data.get_reservoir_api_key()
) -> None:
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
            print(
                f"Marketplace: {trade.marketplace} \n Project: {trade.project_name} \n Currency: {trade.currency} \n Value: {trade.value} \n Created At: {trade.timestamp} \n"
            )


# instance variables
configs = get_configs()
contract = configs.contract_address
data_type = configs.data_type
target_marketplaces = configs.marketplaces
store_data = configs.store_data
verbose = configs.verbose
ask_count = {"OpenSea": 0, "LooksRare": 0, "X2Y2": 0, "atomic0": 0}
token_ids = []

print("fetching data...\n")

# pull and organize ask data
if data_type == "asks":
    manage_asks(verbose=verbose)

# pull and organize ask distribution data
if data_type == "ask_distribution":
    manage_ask_distribution()

# pull and organize bid data
if data_type == "bids":
    manage_bids()

# pull and organize trade data
if data_type == "trades":
    manage_trades()

# pull and organize ask + bid data to search for arb opportunities
if data_type == "arbitrage":
    find_arb_opportunities()
