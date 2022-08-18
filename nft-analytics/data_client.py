import json, contracts, table_manager, sys, CLI
from re import S
from collections import OrderedDict
from data_models import Ask, Bid, Trade
from web3 import Web3
import endpoints as data
import streamlit as st
import matplotlib.pyplot as plt
from operator import itemgetter

class NftClient:
    def __init__(self, configs, api_key):
        self.contract = configs.contract_address
        self.data_type = configs.data_type
        self.target_marketplaces = configs.marketplaces
        self.store_data = configs.store_data
        self.verbose = configs.verbose
        self.api_key = api_key


    # returns a project name from a contract address
    def name_from_contract(self, contract: str) -> str:
        contract_to_name = {v: k for k, v in contracts.contract_data.items()}

        return contract_to_name[contract]


    # inserts data into table
    def insert_data(self, detailed_data: list, type: str) -> None:
        for detailed_piece_of_data in detailed_data:
            try:
                table_manager.insert_order(detailed_piece_of_data, type)
            except:
                sys.exit("writing data failed -- try resetting database file")


    # generates a streamlit bar chart
    def generate_bar_chart(
        self, data: dict, x_axis_title: str, y_axis_title: str, title: str
    ) -> None:
        x_axis = list(data.keys())
        y_axis = list(data.values())

        figure = plt.figure(figsize=(10, 5))

        plt.bar(x_axis, y_axis)

        plt.xlabel(x_axis_title)
        plt.ylabel(y_axis_title)
        plt.title(title)

        st.pyplot(figure)


    # converts ask JSON data to ask objects
    def parse_asks(
        self,
        orders: list,
        ask_count: dict,
        marketplace_asks: json,
        detailed_asks: list,
        max_price: int,
        token_ids: list,
        target_marketplaces: list,
    ) -> dict:
        for ask in orders:
            try:
                marketplace = ask["source"]["name"]
            except:
                marketplace = CLI.convert_marketplace_name(ask["kind"])

            project_name = ask["metadata"]["data"]["collectionName"]
            nft_id = ask["tokenSetId"].split(":", 2)[2]
            currency = "ETH"
            price = ask["price"]
            created_at = ask["createdAt"]
            expires_on = ask["expiration"]
            maker = ask["maker"]

            value = int(round(price, 0))

            if marketplace in target_marketplaces:
                ask_count[marketplace] += 1
                if (
                    marketplace + ask["tokenSetId"]
                ) not in token_ids and price <= max_price:  # only look at asks on the given marketplace that haven't been added yet below the max price
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

        return {
            "ask_count": ask_count,
            "marketplace_asks": marketplace_asks,
            "detailed_asks": detailed_asks,
            "token_ids": token_ids,
        }


    # converts bid JSON data to bid objects
    def parse_looksrare_bids(self, bids: list, detailed_bids: list, token_ids: list) -> dict:
        makers = []
        for bid in bids:
            marketplace = "LooksRare"
            project_name = self.name_from_contract(bid["collectionAddress"])
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

        return {
            "detailed_bids": detailed_bids,
            "makers": makers,
            "token_ids": token_ids,
        }


    # converts trade JSON data to a trade object
    def parse_trades(
        self, trades: list, detailed_trades: list, token_ids: list, target_marketplaces: list
    ) -> dict:
        for trade in trades:
            project_name = self.name_from_contract(
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

        return {
            "detailed_trades": detailed_trades,
            "token_ids": token_ids,
        }


    # manage asks
    def manage_asks(
        self, 
        contract: str,
        target_marketplaces: list,
        store_data: bool = False,
        key: str = data.get_reservoir_api_key(),
        max_price: int = 1000,
    ) -> dict:
        marketplace_asks = {"OpenSea": {}, "LooksRare": {}, "X2Y2": {}}
        ask_count = {"OpenSea": 0, "LooksRare": 0, "X2Y2": 0, "atomic0": 0}
        detailed_asks = []
        token_ids = []
        continuation = None

        # continually fetches the next page of asks and updates the marketplace orders with the next asks
        for i in range(15):
            asks = data.get_open_asks(contract, key, continuation)
            orders = asks["orders"]
            continuation = asks["continuation"]

            parsed_asks = self.parse_asks(
                orders,
                ask_count,
                marketplace_asks=marketplace_asks,
                detailed_asks=detailed_asks,
                max_price=max_price,
                token_ids=token_ids,
                target_marketplaces=target_marketplaces,
            )

            ask_count = parsed_asks["ask_count"]
            marketplace_asks = parsed_asks["marketplace_asks"]
            detailed_asks = parsed_asks["detailed_asks"]
            token_ids = parsed_asks["token_ids"]

        if store_data:
            self.insert_data(detailed_asks, "asks")

        return {
            "ask_count": ask_count,
            "marketplace_asks": marketplace_asks,
            "detailed_asks": detailed_asks,
        }


    # gets and plots ask price distribution
    def ask_price_distribution(
        self,
        bar_chart: bool = True,
    ) -> None:
        project = self.name_from_contract(self.contract)
        min_price = data.get_floor_price(self.contract)
        max_price = min_price * 3

        asks = self.manage_asks(
            contract=self.contract,
            max_price=max_price,
            store_data=self.store_data,
            target_marketplaces=self.target_marketplaces,
        )
        marketplace_asks = asks["marketplace_asks"]

        # print out the data in an easily copiable format so that it can be pasted into excel, google sheets, etc and store it in a .db file
        if self.verbose:
            print(f"Asks at each round ETH value from {min_price} to {max_price}:")

            for marketplace in marketplace_asks.keys():
                marketplace_asks[marketplace] = dict(
                    OrderedDict(sorted(marketplace_asks[marketplace].items()))
                )  # sort the orderbook by price

                print(f"\n{marketplace}")
                for value in marketplace_asks[marketplace].keys():
                    print(str(value) + ":" + str(marketplace_asks[marketplace][value]))

        if bar_chart:
            for marketplace in marketplace_asks.keys():
                # marketplace_distribution_bar_chart(marketplace_asks[marketplace])
                self.generate_bar_chart(
                    data=marketplace_asks[marketplace],
                    x_axis_title="Listing Price",
                    y_axis_title="# of Listings",
                    title=f"# of {project} Listings across prices on {marketplace}",
                )


    # get and plot ask marketplace distribution
    def ask_marketplace_distribution(
        self
    ) -> dict:
        project = self.name_from_contract(self.contract)
        asks = self.manage_asks(
            contract=self.contract,
            store_data=self.store_data,
            target_marketplaces=self.target_marketplaces,
        )
        ask_count = asks["ask_count"]
        parsed_ask_count = {}

        for key in ask_count.keys():
            if key in self.target_marketplaces:
                parsed_ask_count[key] = ask_count[key]

        self.generate_bar_chart(
            data=parsed_ask_count,
            x_axis_title=None,
            y_axis_title="# of Listings",
            title=f"# of Listings for {project} Across Marketplaces",
        )

        return parsed_ask_count


    # looks at how many projects are listed on one or multiple marketplaces (ask marketplace concentration)
    def ask_marketplace_concentration(
        self
    ) -> None:
        project = self.name_from_contract(self.contract)
        asks = self.manage_asks(
            contract=self.contract,
            store_data=self.store_data,
            target_marketplaces=self.target_marketplaces,
        )
        detailed_asks = asks["detailed_asks"]
        distribution = {1: 0, 2: 0, 3: 0}
        nft_ids = []

        # for each ask in the orderbook
        for ask in detailed_asks:
            # if that ask's corresponding NFT has not been scanned yet
            if ask.nft_id not in nft_ids:
                nft_id = ask.nft_id
                number_of_asks = 0
                # look through each ask in orderbook for the specific tokensetID
                for scanned_ask in detailed_asks:
                    # if the ask's tokenSetID we are looking at matches the tokenSetID we are looking for, increment marketplace count by one
                    if scanned_ask.nft_id == nft_id:
                        number_of_asks += 1
                # increment the distribution dict's appropriate value by one
                distribution[number_of_asks] += 1
                nft_ids.append(nft_id)

        self.generate_bar_chart(
            data=distribution,
            x_axis_title="Number of Marketplaces",
            y_axis_title="# of Listings",
            title=f"# of {project} Listings on a Given Number of Marketplaces",
        )


    # search for arb opportunities
    def find_arb_opportunities(
        self
    ) -> list:
        asks = self.manage_asks(
            contract=self.contract,
            store_data=self.store_data,
            target_marketplaces=self.target_marketplaces,
        )["detailed_asks"]
        bids = self.manage_bids(contract=self.contract, store_data=self.store_data, verbose=self.verbose)
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


    # manage bids
    def manage_bids(self) -> list:
        detailed_bids = []
        token_ids = []
        continuation = None

        # single bids
        for i in range(15):
            single_bids = data.get_looksrare_bids(
                contract=self.contract, continuation=continuation
            )
            try:
                continuation = single_bids[-1]["hash"]
            except:
                continuation = None

            parsed_bids = self.parse_looksrare_bids(
                single_bids, detailed_bids=detailed_bids, token_ids=token_ids
            )
            detailed_bids = parsed_bids["detailed_bids"]
            token_ids = parsed_bids["token_ids"]

        # collection bids
        for i in range(15):
            collection_bids = data.get_looksrare_bids(
                contract=self.contract, strategy="0x86F909F70813CdB1Bc733f4D97Dc6b03B8e7E8F3"
            )
            parsed_bids = self.parse_looksrare_bids(
                collection_bids, detailed_bids=detailed_bids, token_ids=token_ids
            )
            detailed_bids = parsed_bids["detailed_bids"]
            token_ids = parsed_bids["token_ids"]

        if self.store_data:
            self.insert_data(detailed_bids, "bids")

        if self.verbose:
            for bid in detailed_bids:
                print(
                    f"Marketplace: {bid.marketplace}\n Project: {bid.project_name}\n Currency: {bid.currency}\n Value: {bid.value}\n Created At: {bid.created_at}\n NFT ID: {bid.nft_id}\n Bid Type: {bid.bid_type}\n"
                )

        return detailed_bids


    # manage trades
    def manage_trades(
        self, 
    ) -> list:
        detailed_trades = []
        token_ids = []
        continuation = None

        for i in range(15):
            trade_data = data.get_trades(self.contract, self.api_key, continuation)
            trades = trade_data["trades"]
            continuation = trade_data["continuation"]

            parsed_trades = self.parse_trades(
                trades,
                detailed_trades,
                token_ids=token_ids,
                target_marketplaces=self.target_marketplaces,
            )
            detailed_trades = parsed_trades["detailed_trades"]
            token_ids = parsed_trades["token_ids"]

        if self.store_data:
            self.insert_data(detailed_trades, "trades")

        if self.verbose:
            for trade in detailed_trades:
                print(
                    f"Marketplace: {trade.marketplace} \n Project: {trade.project_name} \n Currency: {trade.currency} \n Value: {trade.value} \n Created At: {trade.timestamp} \n"
                )

        return detailed_trades
