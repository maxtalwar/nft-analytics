from ast import Or
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from data_models import OrderModel, TradeModel

def create_all_tables():
    meta.create_all(engine)

def orders():
    return orders

def trades():
    return trades

def insert_orders(order):
    addition = orders.insert().values(project_name = order.project_name, nft_id = order.nft_id, currency = order.currency, value = order.value, marketplace = order.marketplace, order_type = order.order_type, created_at = order.created_at, expires_on = order.expires_on)

    connection = engine.connect()
    result = connection.execute(addition)

    return result

engine = create_engine("sqlite:///data.db", echo = False)
meta = MetaData()

orders = Table(
    OrderModel.__tablename__, meta,
    OrderModel.project_name,
    OrderModel.nft_id,
    OrderModel.currency,
    OrderModel.value,
    OrderModel.marketplace,
    OrderModel.order_type,
    OrderModel.created_at,
    OrderModel.expires_on,
)

trades = Table(
    TradeModel.__tablename__, meta,
    TradeModel.project_name,
    TradeModel.nft_id,
    TradeModel.currency,
    TradeModel.value,
    TradeModel.marketplace,
    TradeModel.trade_date,
    TradeModel.buyer,
    TradeModel.seller,
)