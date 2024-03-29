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
        help="options: [ask price distribution, ask marketplace distribution, ask marketplace concentration, arbitrage, bids, trades]",
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
        choice = input(
            "Data Type: (ask price distribution, ask marketplace distribution, ask marketplace concentration, arbitrage, bid, or trade data): "
        )

    # ask price distribution, ask marketplace distribution, ask marketplace concentration, arbitrage, bids, trades
    price_distribution = "ask_price_distribution"
    marketplace_distribution = "ask_marketplace_distribution"
    marketplace_concentration = "ask_marketplace_concentration"
    arb = "arbitrage"
    bids = "bids"
    trades = "trades"

    conversions = {
        "Asks": price_distribution,
        "Ask": price_distribution,
        "asks": price_distribution,
        "ask": price_distribution,
        "ask price distribution": price_distribution,
        "ask_distribution": marketplace_distribution,
        "ask-distribution": marketplace_distribution,
        "ask distribution": marketplace_distribution,
        "ask distributions": marketplace_distribution,
        "ask marketplace distribution": marketplace_distribution,
        "ask_concentration": marketplace_concentration,
        "Ask_Concentration": marketplace_concentration,
        "ask concentration": marketplace_concentration,
        "Ask Concentration": marketplace_concentration,
        "ask marketplace concentration": marketplace_concentration,
        "liquidity_concentration": marketplace_concentration,
        "Liquidity_Concentration": marketplace_concentration,
        "liquidity concentration": marketplace_concentration,
        "Liquidity Concentration": marketplace_concentration,
        "Arbitrage": arb,
        "arbitrage": arb,
        "arbitrage opportunities": arb,
        "Arbitrage opportunities": arb,
        "Bids": bids,
        "Bid": bids,
        "bid": bids,
        "bids": bids,
        "Trades": trades,
        "Trade": trades,
        "trade": trades,
        "trades": trades,
    }

    try:
        return conversions[choice]
    except:
        print("invalid data type")
        return get_data_type(arguments=False)


# process marketplace names
def process_marketplace_names(marketplaces: list = [], data_type: list = None) -> list:
    if data_type == "arbitrage" or data_type == "ask_marketplace_concentration":
        return ["OpenSea", "LooksRare", "X2Y2"]

    if marketplaces == None:
        input_marketplaces = input("Marketplace Names (opensea, looksrare, x2y2): ")
        marketplaces = list(input_marketplaces.split(" "))

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


# converts various ways of spelling marketplaces into the names accepted by the reservoir.tools API
def convert_marketplace_name(marketplace: str = None) -> str:
    OS = "OpenSea"
    LR = "LooksRare"
    X2 = "X2Y2"

    if marketplace == None:
        marketplace = input("Marketplace Name (opensea, looksrare, x2y2): ")

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
        return convert_marketplace_name()


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


# gets storage and output preferences
def get_data_preferences(
    store_data: bool = None, verbose: bool = None, data_type: bool = None
) -> json:
    if (
        data_type == "ask_marketplace_distribution"
        or data_type == "ask_marketplace_concentration"
        or data_type == "arbitrage"
    ):
        verbose = False
    if data_type == "arbitrage":
        store_data = False
    else:
        if store_data == None:
            store_data = input("Store data in .db file? [Y/n]: ") == "Y"
        if not store_data and data_type in ["bids", "trades"]:
            verbose = True
        if verbose == None:
            verbose = input("Output data to CLI? [Y/n]: ") == "Y"

    return {"storage_preferences": store_data, "verbose": verbose}
