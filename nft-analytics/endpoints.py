import requests, json, math, contracts, sys, time

# gets an API key from the reservoir.tools API
def get_reservoir_api_key() -> json:
    url = "https://api.reservoir.tools/api-keys"

    payload = "appName=Marketplace_Indexer&email=proton0x%40photonmail.com&website=https%3A%2F%2Fgithub.com%2F0xphoton%2FNFT-Marketplaces"
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "x-api-key": "demo-api-key",
    }

    response = requests.post(url, data=payload, headers=headers)

    # backup key: "9240bc7c-a6a7-5657-9619-b1f6dbb6d065"
    return json.loads(response.text)["key"]


# gets the floor price for a specific project
def get_floor_price(contract: str, key: str = get_reservoir_api_key()) -> json:
    url = f"https://api.reservoir.tools/collection/v3?id={contract}&includeTopBid=false"

    headers = {"Accept": "*/*", "x-api-key": key}

    response = json.loads(requests.get(url, headers=headers).text)

    return int(math.floor(response["collection"]["floorAsk"]["price"]))


# gets bid on looksrare
def get_looksrare_bids(
    contract: str, continuation: str = None, strategy: str = None
) -> json:
    url = f"https://api.looksrare.org/api/v1/orders?isOrderAsk=false&collection={contract}&price%5Bmin%5D=1000000000000000000&status%5B%5D=VALID&pagination%5Bfirst%5D=150"

    if continuation != None:
        url += f"&pagination[cursor]={continuation}"

    if strategy != None:
        url += f"&strategy={strategy}"

    headers = {"Accept": "*/*"}

    response = json.loads(requests.get(url, headers=headers).text)["data"]

    return response


# gets bids from reservoir
def get_open_bids(contract: str, key: str, continuation: str = None):
    url = f"https://api.reservoir.tools/orders/bids/v4?contracts={contract}&includeMetadata=false&includeRawData=false&sortBy=createdAt&limit=100"

    if continuation != None:
        url += f"&continuation={continuation}"

    headers = {"Accept": "*/*", "x-api-key": key}

    try:
        response = json.loads(requests.get(url, headers=headers).text)
    except:
        sys.exit("504 Error: Gateway timeout")

    return {"bids": response["orders"], "continuation": response["continuation"]}


# gets open asks on a specific project from the reservoir API
def get_open_asks(contract: str, key: str, continuation: str = None) -> json:
    url = f"https://api.reservoir.tools/orders/asks/v2?contracts={contract}&includePrivate=false&limit=100"

    if continuation != None:
        url += f"&continuation={continuation}"

    headers = {"Accept": "*/*", "x-api-key": key}

    try:
        response = json.loads(requests.get(url, headers=headers).text)
    except:
        time.sleep(15)
        key = get_reservoir_api_key()
        return get_open_asks(contract, key, continuation)

    return {"orders": response["orders"], "continuation": response["continuation"]}


# gets past trades
def get_trades(contract: str, key: str, continuation: str = None):
    url = f"https://api.reservoir.tools/sales/v3?contract={contract}&limit=100"

    if continuation != None:
        url += f"&continuation={continuation}"

    headers = {"Accept": "*/*", "x-api-key": key}

    try:
        response = json.loads(requests.get(url, headers=headers).text)
    except:
        sys.exit("504 Error: Gateway timeout")

    return {"trades": response["sales"], "continuation": response["continuation"]}


# get bids from opensea API stream
def get_opensea_bids_stream(contract: str, api_key: str) -> json:
    url = f"wss://stream.openseabeta.com/socket/websocket?token={api_key}"

    slug = contracts.contract_to_collection_slug[contract]
    headers = {
        "topic": f"collection:{slug}",
        "event": "item_received_bid",
        "payload": {},
        "ref": 0,
    }

    stream = requests.Session()
    response = stream.get(url, headers=headers, stream=True)

    return response
