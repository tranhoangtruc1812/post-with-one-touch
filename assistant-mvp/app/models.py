from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Product(BaseModel):
    product_id: str
    name: str
    short_description: Optional[str] = ""
    target_customer: Optional[str] = ""
    pain_point: Optional[str] = ""
    benefit: Optional[str] = ""
    price: Optional[float] = 0.0
    cta: Optional[str] = ""
    status: Optional[str] = "active"

class Post(BaseModel):
    post_id: Optional[str] = ""
    product_id: str
    topic: Optional[str] = ""
    channel: str = "Facebook"
    content: str
    status_draft: str = "draft"
    approved: bool = False
    scheduled_time: Optional[datetime] = None
    posted_time: Optional[datetime] = None
    post_url: Optional[str] = ""

class Order(BaseModel):
    order_id: str
    created_time: datetime
    customer_name: Optional[str] = ""
    phone: Optional[str] = ""
    source: Optional[str] = ""
    product_name: Optional[str] = ""
    amount: Optional[float] = 0.0
    payment_status: str = "unpaid"
    order_status: str = "new"
    priority: str = "normal"
    note: Optional[str] = ""
    ai_reply_suggestion: Optional[str] = ""
