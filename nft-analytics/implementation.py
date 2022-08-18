import CLI, data_client, sys, endpoints

if __name__ == "__main__":
    done = False

    while not done:
        configs = CLI.get_configs()
        contract = configs.contract_address
        data_type = configs.data_type
        target_marketplaces = configs.marketplaces
        store_data = configs.store_data
        verbose = configs.verbose
        api_key = endpoints.get_reservoir_api_key()

        client = data_client.NftClient(configs, api_key)

        print("fetching data...\n")

        # pull and organize ask price distribution data
        if data_type == "ask_price_distribution":
            client.ask_price_distribution()

        # pull and organize ask marketplace distribution data
        if data_type == "ask_marketplace_distribution":
            client.ask_marketplace_distribution()

        # pull and organize ask marketplace concentration data
        if data_type == "ask_marketplace_concentration":
            client.ask_marketplace_concentration()

        # pull and organize ask + bid data to search for arb opportunities
        if data_type == "arbitrage":
            client.find_arb_opportunities()

        # pull and organize bid data
        if data_type == "bids":
            client.manage_bids()

        # pull and organize trade data
        if data_type == "trades":
            client.manage_trades()

        print("data fetching complete")

        done = input("Done? [Y/n]: ") == "Y"
