from ast import Or
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from data_models import AskModel, TradeModel

def create_all_tables():
    meta.create_all(engine)

def orders():
    return orders

def trades():
    return trades

def insert_orders(order):
    addition = orders.insert().values(project_name = order.project_name, nft_id = order.nft_id, currency = order.currency, value = order.value, marketplace = order.marketplace, created_at = order.created_at, expires_on = order.expires_on, maker = order.maker)

    connection = engine.connect()
    result = connection.execute(addition)

    return result

engine = create_engine("sqlite:///data.db", echo = False)
meta = MetaData()

orders = Table(
    AskModel.__tablename__, meta,
    AskModel.project_name,
    AskModel.nft_id,
    AskModel.currency,
    AskModel.value,
    AskModel.marketplace,
    AskModel.created_at,
    AskModel.expires_on,
    AskModel.maker,
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