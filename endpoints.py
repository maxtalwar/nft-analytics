import requests, json, math, os, contracts

# gets an API key from the reservoir.tools API
def get_reservoir_api_key() -> json:
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
def get_floor_price(contract: str, key: str) -> json:
    url = f"https://api.reservoir.tools/collection/v3?id={contract}&includeTopBid=false"

    headers = {
        "Accept": "*/*",
        "x-api-key": key
    }

    response = json.loads(requests.get(url, headers=headers).text)

    return int(math.floor(response["collection"]["floorAsk"]["price"]))

def get_looksrare_bids(contract: str, continuation=None, strategy=None) -> json:
    url = f'https://api.looksrare.org/api/v1/orders?isOrderAsk=false&collection={contract}&price%5Bmin%5D=1000000000000000000&status%5B%5D=VALID&pagination%5Bfirst%5D=150'

    if continuation != None:
        url += f'&pagination[cursor]={continuation}'

    if strategy != None:
        url += f'&strategy={strategy}'

    headers = {
        "Accept": "*/*"
    }

    response = json.loads(requests.get(url, headers=headers).text)["data"]

    return response

def get_open_bids_v2(contract: str, marketplace: str, key=None, continuation=None, bid_type="single") -> json:
    if marketplace == "LooksRare":
        if bid_type == "single":
            bids = get_looksrare_bids(contract, continuation=continuation)
        else:
            bids = get_looksrare_bids(contract, strategy="0x86F909F70813CdB1Bc733f4D97Dc6b03B8e7E8F3")
            print(bids)
    else:
        print("unsupported marketplace for bids")
        quit()

    return bids

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
        quit()

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
        quit()

    return {
        "orders": response["orders"], 
        "continuation": response["continuation"]
    }

# gets past trades
def get_trades(contract: str, key: str, continuation=None):
    url = f"https://api.reservoir.tools/sales/v3?contract={contract}&limit=100"

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
        quit()

    return {
        "trades": response["sales"],
        "continuation": response["continuation"]
    }

# get bids from opensea API stream
def get_opensea_bids_stream(contract: str, api_key: str) -> json:
    url = f"wss://stream.openseabeta.com/socket/websocket?token={api_key}"

    slug = contracts.contract_to_collection_slug[contract]
    headers = {
        "topic": f"collection:{slug}",
        "event": "item_received_bid",
        "payload": {},
        "ref": 0
    }

    stream = requests.Session()
    response = stream.get(url, headers=headers, stream=True)

    return response