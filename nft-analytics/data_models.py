from sqlalchemy import Column, Numeric, String


class AskModel:
    __tablename__ = "asks"

    project_name = Column("project_name", String)
    nft_id = Column("nft_id", String)
    currency = Column("currency", String)
    value = Column("value", Numeric)
    marketplace = Column("marketplace", String)
    created_at = Column("created_at", String)
    expires_on = Column("expires_on", String)
    maker = Column("maker", String)
    network = Column("network", String)


class BidModel:
    __tablename__ = "bids"

    project_name = Column("project_name", String)
    nft_id = Column("nft_id", String)
    currency = Column("currency", String)
    value = Column("value", Numeric)
    marketplace = Column("marketplace", String)
    created_at = Column("created_at", String)
    expires_on = Column("expires_on", String)
    maker = Column("maker", String)
    bid_type = Column("bid_type", String)
    network = Column("network", String)


class TradeModel:
    __tablename__ = "trades"

    project_name = Column("project_name", String)
    nft_id = Column("nft_id", String)
    currency = Column("currency", String)
    value = Column("value", Numeric)
    marketplace = Column("marketplace", String)
    timestamp = Column("timestamp", Numeric)
    buyer = Column("buyer", String)
    seller = Column("seller", String)
    network = Column("network", String)
    tx_id = Column("tx_id", String)
    offer_type = Column("offer_type", String)
    fee = Column("fee", Numeric)


class Ask:
    def __init__(
        self,
        project_name,
        nft_id,
        currency,
        value,
        marketplace,
        created_at,
        expires_on,
        maker,
        network,
    ):
        self.project_name = project_name
        self.nft_id = nft_id
        self.currency = currency
        self.value = value
        self.marketplace = marketplace
        self.created_at = created_at
        self.expires_on = expires_on
        self.maker = maker
        self.network = network


class Bid:
    def __init__(
        self,
        project_name,
        nft_id,
        currency,
        value,
        marketplace,
        created_at,
        maker,
        bid_type,
        network,
    ):
        self.project_name = project_name
        self.nft_id = nft_id
        self.currency = currency
        self.value = value
        self.marketplace = marketplace
        self.created_at = created_at
        self.maker = maker
        self.bid_type = bid_type
        self.network = network


class Trade:
    def __init__(
        self,
        project_name,
        nft_id,
        currency,
        value,
        marketplace,
        timestamp,
        buyer,
        seller,
        network,
        tx_id,
        offer_type,
        fee,
    ):
        self.project_name = project_name
        self.nft_id = nft_id
        self.currency = currency
        self.value = value
        self.marketplace = marketplace
        self.timestamp = timestamp
        self.buyer = buyer
        self.seller = seller
        self.network = network
        self.tx_id = tx_id
        self.offer_type = offer_type
        self.fee = fee
