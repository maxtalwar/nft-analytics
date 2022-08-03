from sqlalchemy import ARRAY, Column, Numeric, String

class AskModel():
    __tablename__ = "asks"

    project_name = Column('project_name', String)
    nft_id = Column('nft_id', String)
    currency = Column('currency', String)
    value = Column('value', Numeric)
    marketplace = Column('marketplace', String)
    created_at = Column('created_at', String)
    expires_on = Column('expires_on', String)
    maker = Column('maker', String)

class BidModel():
    __tablename__ = "bids"

    project_name = Column('project_name', String)
    nft_id = Column('nft_id', String)
    currency = Column('currency', String)
    value = Column('value', Numeric)
    marketplace = Column('marketplace', String)
    created_at = Column('created_at', String)
    expires_on = Column('expires_on', String)
    maker = Column('maker', String)
    bid_type = Column("bid_type", String)

class TradeModel():
    __tablename__ = "trades"

    project_name = Column('project_name', String)
    nft_id = Column('nft_id', String)
    currency = Column('currency', String)
    value = Column('value', Numeric)
    marketplace = Column('marketplace', String)
    timestamp = Column('timestamp', Numeric)
    buyer = Column('buyer', String)
    seller = Column('seller', String)

class Ask:
    def __init__(self, project_name, nft_id, currency, value, marketplace, created_at, expires_on, maker):
        self.project_name = project_name
        self.nft_id = nft_id
        self.currency = currency
        self.value = value
        self.marketplace = marketplace
        self.created_at = created_at
        self.expires_on = expires_on
        self.maker = maker

class Bid:
    def __init__(self, project_name, nft_id, currency, value, marketplace, created_at, maker, bid_type):
        self.project_name = project_name
        self.nft_id = nft_id
        self.currency = currency
        self.value = value
        self.marketplace = marketplace
        self.created_at = created_at
        self.maker = maker
        self.bid_type = bid_type

class Trade:
    def __init__(self, project_name, nft_id, currency, value, marketplace, timestamp, buyer, seller):
        self.project_name = project_name
        self.nft_id = nft_id
        self.currency = currency
        self.value = value
        self.marketplace = marketplace
        self.timestamp = timestamp
        self.buyer = buyer
        self.seller = seller