import argparse, contracts, json

def get_configs():
    parser = argparse.ArgumentParser(
        "Provide information about the data you want to query"
    )
    parser.add_argument(
        "--collection",
        dest="collection",
        type=str,
        help="[Cryptopunks, Moonbirds, Otherdeed, Goblintown, BAYC, MAYC, CloneX, Meebits, Doodles, Azuki, Veefriends]",
    )
    parser.add_argument(
        "--data_type",
        dest="data_type",
        type=str,
        help="options: [asks, bids, trades, ask distribution, ask concentration, arbitrage]",
    )
    parser.add_argument(
        "--marketplaces",
        dest="marketplaces",
        type=str,
        nargs="+",
        help="marketplace[s] to process data for. Opensea, Looksrare, and X2Y2 supported. ",
    )
    parser.add_argument(
        "--store_data",
        dest="store_data",
        type=bool,
        help="Choose whether to store data on .db file. (True, False)",
    )
    parser.add_argument(
        "--verbose",
        dest="verbose",
        type=bool,
        help="Choose whether scraped data is displayed on CLI (True, False)",
    )
    args = parser.parse_args()

    args.contract_address = get_contract_address(
        verbose=False, collection=args.collection
    )
    args.data_type = get_data_type(args.data_type)
    args.marketplaces = process_marketplace_names(args.marketplaces, args.data_type)

    data_management_configs = get_data_preferences(
        store_data=args.store_data, verbose=args.verbose, data_type=args.data_type
    )
    args.store_data = data_management_configs["storage_preferences"]
    args.verbose = data_management_configs["verbose"]

    return args


# gets data type from command line arguments
def get_data_type(choice: str = None) -> str:
    if choice == None:
        choice = input("ask, ask distribution, ask concentration, bid, or trade data: ")

    conversions = {
        "Bids": "bids",
        "Bid": "bids",
        "bid": "bids",
        "bids": "bids",
        "b": "bids",
        "Asks": "asks",
        "Ask": "asks",
        "asks": "asks",
        "ask": "asks",
        "a": "asks",
        "Trades": "trades",
        "Trade": "trades",
        "trade": "trades",
        "trades": "trades",
        "t": "trades",
        "ask_distribution": "ask_distribution",
        "ask-distribution": "ask_distribution",
        "ask distribution": "ask_distribution",
        "ask distributions": "ask_distribution",
        "Arbitrage": "arbitrage",
        "arbitrage": "arbitrage",
        "arbitrage opportunities": "arbitrage",
        "Arbitrage opportunities": "arbitrage",
        "ask_concentration": "ask_concentration",
        "Ask_Concentration": "ask_concentration",
        "ask concentration": "ask_concentration",
        "Ask Concentration": "ask_concentration",
        "liquidity_concentration": "ask_concentration",
        "Liquidity_Concentration": "ask_concentration",
        "liquidity concentration": "ask_concentration",
        "Liquidity Concentration": "ask_concentration",
    }

    try:
        return conversions[choice]
    except:
        print("invalid data type")
        return get_data_type(arguments=False)


# process marketplace names
def process_marketplace_names(marketplaces: list = [], data_type: list = None) -> list:
    if marketplaces == None:
        marketplaces = []

    if data_type == "arbitrage" or data_type == "ask_concentration":
        return ["OpenSea", "LooksRare", "X2Y2"]

    if len(marketplaces) != 0:
        for i in range(len(marketplaces)):
            marketplaces[i] = convert_marketplace_name(marketplaces[i])

        adding_more = input("add another marketplace? [Y/n]: ") == "Y"
    else:
        adding_more = True

    while adding_more:
        marketplaces.append(convert_marketplace_name())
        adding_more = input("add another marketplace? [Y/n]: ") == "Y"

    return marketplaces

# gets project contract address from project name
def get_contract_address(verbose: bool = True, collection: str = None) -> str:
    contract_data = contracts.contract_data

    if verbose:
        print("Contracts")
        for contract in contract_data.keys():
            print(contract + ": " + contract_data[contract])

    if collection == None:
        collection = input(
            "Collection Name [Cryptopunks, Moonbirds, Otherdeed, Goblintown, BAYC, MAYC, CloneX, Meebits, Doodles, Azuki, Veefriends]: "
        )

    try:
        return contract_data[collection]
    except:
        print("invalid collection name")
        return get_contract_address(verbose=False)

# converts various ways of spelling marketplaces into the names accepted by the reservoir.tools API
def convert_marketplace_name(marketplace: str = None) -> str:
    OS = "OpenSea"
    LR = "LooksRare"
    X2 = "X2Y2"

    if marketplace == None:
        marketplace = input("Marketplace name (opensea, looksrare, x2y2): ")

    conversions = {
        "Opensea": OS,
        "opensea": OS,
        "seaport": OS,
        "Looksrare": LR,
        "looksrare": LR,
        "looks-rare": LR,
        "x2y2": X2,
    }

    try:
        return conversions[marketplace]
    except:
        print("invalid marketplace name")
        print(marketplace)
        return convert_marketplace_name()


# gets storage and output preferences
def get_data_preferences(
    store_data: bool = None, verbose: bool = None, data_type: bool = None
) -> json:
    if data_type == "ask_distribution":
        verbose = False
        store_data = True
    elif data_type == "arbitrage":
        verbose = False
        store_data = False
    elif data_type == "ask_concentration":
        store_data = False
    else:
        if store_data == None:
            store_data = input("Store data in .db file? [Y/n]: ") == "Y"
        if not store_data:
            verbose = True
        elif verbose == None:
            verbose = input("Output data to CLI? [Y/n]: ") == "Y"

    return {"storage_preferences": store_data, "verbose": verbose}