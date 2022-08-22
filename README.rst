More info can be found here: https://docs.google.com/document/d/1RJ3_Ypvgv_AbifZQahioFnhhUhYFBvvVA6EZMaIjp1k/edit?usp=sharing

You will initially be prompted about the following information:

Collection Name

In this field, enter the name of the collection that you want to get data for. The options are: 
- Cryptopunks
- Moonbirds
- Otherdeed
- Goblintown
- BAYC
- MAYC
- CloneX
- Meebits
- Doodles
- Azuki
- Veefriends -
Only these specific names will be accepted. 

Data Type

In this field, enter the type of data you want to collect. The options are asks, bids, trades, ask distributions, and arbitrage opportunities.
Ask price distribution generates a graph of the open listings on given marketplaces across a price range
Ask marketplace distribution generates a streamlit chart of the number of asks on various exchanges. 
Ask marketplace concentration generates a streamlit chart of the number of asks listed on 1, 2, or 3 exchanges. Can give you a sense for how concentrated liquidity is per collection.
Arbitrage opportunities searches for arbitrage opportunities across exchanges and displays them on the CLI. 
Bids returns the open offers for a given collection on a given marketplace. NOTE: Only Looksrare bids have been implemented so far, because Opensea does not provide access to historical bids on their API. 
Trades returns all the historical trades for a given collection on a given marketplace. 
 

Marketplace Name

The name of the marketplace[s] you want to pull data from. Opensea, Looksrare, and X2Y2 are supported. Multiple marketplaces can be used in one query.

Whether to store data in a .db file

In this field, enter whether you would like the queried data to be stored in a .db file. When prompted by the program, "Y" means yes, anything else means no. 
In the command line, the options are True or False

Whether to output data to CLI

In this field, enter whether you would like the queried data to be displayed in the CLI. When prompted by the program, "Y" means yes, anything else means no. 
In the command line, the options are True or False.
This is automatically set to True if you are not storing data because otherwise you wouldn't be doing anything with the data, so there wouldn't be any point in running the program at all. 


Troubleshooting:

If you are told "writing data failed -- try resetting the database file", just delete the database.db file and run "table_manager.py" again. This isn't automated because automatically deleting the database file with all the data the collected data should only be done expliitly by the user. 

To run: 

poetry run python3 data_client.py

or, to run while generating a chart:

poetry run streamlit run data_client.py

Remember to use streamlit for all functions except arbitrage opportunities, bids, and trades! Streamlit should also notify you if the section of code that you are running is supposed to be run with streamlit. 
note: streamlit has a bug causing arguments to automatically be interpreted as streamlit arguments, so you will have to enter configs manually for data types that use streamlit
