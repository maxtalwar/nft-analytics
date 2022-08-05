import reservoir_tools_client_v2 as client
#import contracts

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

bids = client.get_looksrare_single_bids("0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D", continuation)
total = 0

for bid in bids:
    print(bid["order"])
    total += 1

print(total)
print("\n")
continuation = bids[-1]["id"]

print(bids)