from fastapi import FastAPI, Depends, Query
from .database import get_db
from .schemas import TopProductsResponse, ChannelActivityResponse, MessageSearchResult
from .crud import get_top_products, get_channel_activity, search_messages
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/api/reports/top-products", response_model=TopProductsResponse)
def top_products(
    limit: int = Query(10, gt=0, le=100),
    db: Session = Depends(get_db)
):
    products = get_top_products(db, limit=limit)
    return {"products": products}

@app.get("/api/channels/{channel_name}/activity", response_model=ChannelActivityResponse)
def channel_activity(
    channel_name: str,
    db: Session = Depends(get_db)
):
    activity = get_channel_activity(db, channel_name=channel_name)
    return {"activity": activity}

@app.get("/api/search/messages", response_model=list[MessageSearchResult])
def search_messages(
    query: str = Query(..., min_length=3),
    limit: int = Query(10, gt=0, le=50),
    db: Session = Depends(get_db)
):
    return search_messages(db, query=query, limit=limit)

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}