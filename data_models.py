from sqlalchemy import ARRAY, Column, Numeric, String

class OrderModel():
    __tablename__ = "orders"

    project_name = Column(String)
    nft_id = Column(String)
    currency = Column(String)
    value = Column(Numeric)
    marketplace = Column(String)
    order_type = Column(String)
    created_at = Column(String)
    expires_on = Column(String)

class TradeModel():
    __tablename__ = "trades"

    project_name = Column(String)
    nft_id = Column(String)
    currency = Column(String)
    value = Column(Numeric)
    marketplace = Column(String)
    trade_data = Column(String)
    Buyer = Column(String)
    Seller = Column(String)