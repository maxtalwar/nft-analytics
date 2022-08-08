import data_client as client
import contracts

"""output = client.get_looksrare_single_bids(contracts.contract_data["BAYC"])
total = 0

for key in output.keys():
    print(key + ":" + str(output[key]))
    total += 1
    print("\n")


for trade in output:
    print(trade)
    print("\n")
    total += 1

print(total)"""

continuation = None
API_KEY = None

bids = client.get_opensea_bids_stream(contracts.contract_data["BAYC"], API_KEY)