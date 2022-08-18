import CLI, data_client

if __name__ == "__main__":
    configs = CLI.get_configs()
    contract = configs.contract_address
    data_type = configs.data_type
    target_marketplaces = configs.marketplaces
    store_data = configs.store_data
    verbose = configs.verbose

    print("fetching data...\n")

    # pull and organize ask price distribution data
    if data_type == "ask_price_distribution":
        data_client.ask_price_distribution(contract=contract, store_data=store_data, verbose=verbose, target_marketplaces=target_marketplaces)

    # pull and organize ask marketplace distribution data
    if data_type == "ask_marketplace_distribution":
        data_client.ask_marketplace_distribution(contract=contract, store_data=store_data, target_marketplaces=target_marketplaces)

    # pull and organize ask marketplace concentration data
    if data_type == "ask_marketplace_concentration":
        data_client.ask_marketplace_concentration(contract=contract, store_data=store_data, target_marketplaces=target_marketplaces)

    # pull and organize ask + bid data to search for arb opportunities
    if data_type == "arbitrage":
        data_client.find_arb_opportunities(contract=contract, store_data=store_data, verbose=verbose, target_marketplaces=target_marketplaces)

    # pull and organize bid data
    if data_type == "bids":
        data_client.manage_bids(contract=contract, store_data=store_data, verbose=verbose)

    # pull and organize trade data
    if data_type == "trades":
        data_client.manage_trades(contract=contract, target_marketplaces=target_marketplaces, store_data=store_data, verbose=verbose)

    print("data fetching complete")