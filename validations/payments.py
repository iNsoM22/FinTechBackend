from pydantic import BaseModel, Field
from typing import Optional, List


class StripePrice(BaseModel):
    id: str
    unit_amount: int
    currency: str
    recurring: Optional[dict] = None


class StripeProduct(BaseModel):
    id: str
    name: str
    description: Optional[str]
    prices: List[StripePrice]
    
    

class CheckoutRequest(BaseModel):
    price_id: str


class CheckoutSessionResponse(BaseModel):
    url: str

class WebhookResponse(BaseModel):
    status: str
