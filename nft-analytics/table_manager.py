from ast import Or
from sqlalchemy import create_engine, Table, MetaData
from data_models import AskModel, BidModel, TradeModel
from typing import Union


def insert_order(
    order: Union[AskModel, BidModel, TradeModel], input_table: str
) -> None:
    if input_table == "ask":
        addition = asks.insert().values(
            project_name=order.project_name,
            nft_id=order.nft_id,
            currency=order.currency,
            value=order.value,
            marketplace=order.marketplace,
            created_at=order.created_at,
            expires_on=order.expires_on,
            maker=order.maker,
            network=order.network,
        )
    if input_table == "bid":
        addition = bids.insert().values(
            project_name=order.project_name,
            nft_id=order.nft_id,
            currency=order.currency,
            value=order.value,
            marketplace=order.marketplace,
            created_at=order.created_at,
            maker=order.maker,
            bid_type=order.bid_type,
            network=order.network,
        )
    if input_table == "trade":
        addition = trades.insert().values(
            project_name=order.project_name,
            nft_id=order.nft_id,
            currency=order.currency,
            value=order.value,
            marketplace=order.marketplace,
            timestamp=order.timestamp,
            buyer=order.buyer,
            seller=order.seller,
            network=order.network,
            tx_id=order.tx_id,
            offer_type=order.offer_type,
            fee=order.fee,
        )

    connection = engine.connect()
    connection.execute(addition)


engine = create_engine("sqlite:///database.db", echo=False)
meta = MetaData()

asks = Table(
    AskModel.__tablename__,
    meta,
    AskModel.project_name,
    AskModel.nft_id,
    AskModel.currency,
    AskModel.value,
    AskModel.marketplace,
    AskModel.created_at,
    AskModel.expires_on,
    AskModel.maker,
    AskModel.network,
)

bids = Table(
    BidModel.__tablename__,
    meta,
    BidModel.project_name,
    BidModel.nft_id,
    BidModel.currency,
    BidModel.value,
    BidModel.marketplace,
    BidModel.created_at,
    BidModel.maker,
    BidModel.bid_type,
    BidModel.network,
)

trades = Table(
    TradeModel.__tablename__,
    meta,
    TradeModel.project_name,
    TradeModel.nft_id,
    TradeModel.currency,
    TradeModel.value,
    TradeModel.marketplace,
    TradeModel.timestamp,
    TradeModel.buyer,
    TradeModel.seller,
    TradeModel.network,
    TradeModel.tx_id,
    TradeModel.offer_type,
    TradeModel.fee,
)

if __name__ == "__main__":
    meta.create_all(engine)
