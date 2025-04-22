from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class StripePrice(BaseModel):
    id: str = Field(
        ...,
        description="Unique identifier for the Stripe Price Object"
    )
    unit_amount: int = Field(
        ...,
        description="Price Amount in the smallest Currency Unit"
    )
    currency: str = Field(
        ...,
        description="Currency code (e.g., 'usd')"
    )
    recurring: Optional[dict] = Field(
        default=None,
        description="Recurring billing details (interval, usage type, etc.)"
    )


class StripeProduct(BaseModel):
    id: str = Field(
        ...,
        description="Unique identifier for the Stripe product"
    )
    name: str = Field(
        ...,
        description="Product name as shown on Stripe"
    )
    description: Optional[str] = Field(
        default=None,
        description="Product Description"
    )
    prices: List[StripePrice] = Field(
        ...,
        description="List of Prices Associated with the Product"
    )


class CheckoutRequest(BaseModel):
    price_id: str = Field(
        ...,
        description="Stripe Price ID used to Create a Checkout Session"
    )


class CheckoutSessionResponse(BaseModel):
    url: str = Field(
        ...,
        description="Stripe-hosted Checkout Session Url"
    )


class WebhookResponse(BaseModel):
    status: Literal["success", "failed"] = Field(
        ...,
        description="Status of Webhook Processing"
    )
    event_type: Optional[str] = Field(
        default=None,
        description="Type of the Stripe event received"
    )
    message: Optional[str] = Field(
        default=None,
        description="Additional Information or Error Message"
    )
