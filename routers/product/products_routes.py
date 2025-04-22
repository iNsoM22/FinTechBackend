from fastapi import APIRouter, status, HTTPException
from typing import List
from validations.payments import StripeProduct, StripePrice
import stripe
from dotenv import load_dotenv
import os

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


router = APIRouter(prefix="/payment", tags=["Payment"])


@router.get("/products", response_model=List[StripeProduct], status_code=status.HTTP_200_OK)
async def get_stripe_products():
    """End-Point to Fetch Pricing Plans"""
    try:
        products = stripe.Product.list(active=True)
        product_list: List[StripeProduct] = []

        for product in products.auto_paging_iter():
            prices = stripe.Price.list(product=product.id, active=True)
            price_data = []
            
            for price in prices.auto_paging_iter():
                price_model = StripePrice(id=price.id,
                                          unit_amount=price.unit_amount,
                                          currency=price.currency,
                                          recurring=price.recurring)
                price_data.append(price_model)
                
            product_model = StripeProduct(id=product.id,
                                          name=product.name,
                                          description=product.description,
                                          prices=price_data)
            product_list.append(product_model)
        return product_list

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to Fetch Products: {str(e)}")
