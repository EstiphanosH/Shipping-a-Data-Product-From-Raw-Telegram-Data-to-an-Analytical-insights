# API schemas
from pydantic import BaseModel
from typing import List

class ProductCount(BaseModel):
    name: str
    count: int

class TopProductsResponse(BaseModel):
    products: List[ProductCount]

class DailyActivity(BaseModel):
    date: str
    count: int

class ChannelActivityResponse(BaseModel):
    activity: List[DailyActivity]

class MessageSearchResult(BaseModel):
    message_id: int
    channel_name: str
    message_text: str
    created_at: str