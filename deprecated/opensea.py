import requests

def get_assets_from_project(collection, API_Key):
    url = "https://api.opensea.io/api/v1/assets?order_direction=desc&limit=20&include_orders=false"
    headers = {"Accept": "application/json", "collection": collection, "collection-slug": collection, "X-API-KEY": API_Key}
    response = requests.get(url, headers=headers)

    return response["assets"]

def get_listings_on_assets(assets, API_Key):

    listings = {}

    for asset in assets:
        print(asset["token_id"])

        url = "https://api.opensea.io/wyvern/v1/orders?bundled=false&include_bundled=false&side=1&limit=20&offset=0&order_by=created_date&order_direction=desc"
        headers = {"Accept": "application/json", "token_id": asset["token_id"], "side": 0, "asset_contract_address": asset["asset_contract"], "X-API-KEY": API_Key}
        response = requests.get(url, headers=headers)

        buy_orders = response["orders"]
        listings[asset["token_id"]]["buy_orders"] = buy_orders

    return listings

def get_listings_from_project(collection, API_Key):
    assets = get_assets_from_project(collection, API_Key)
    listings_on_assets = get_listings_on_assets(assets, API_Key)

    return listings_on_assets


collection = "boredapeyachtclub"
key = "API-Key" # API key would go here

listings = get_listings_from_project(collection, key)