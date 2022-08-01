from sqlalchemy import Table, Column, Integer, String, MetaData
from data_models import OrderModel, TradeModel

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
    OrderModel.expires_on
)