from fastapi import APIRouter, HTTPException, status, Request
from utils.auth import user_dependency
from utils.db import db_dependency
from schemas.subscriptions import Subscription
from schemas.users import User
from validations.payments import CheckoutRequest, CheckoutSessionResponse, WebhookResponse
import stripe
from dotenv import load_dotenv
import os
from sqlalchemy.future import select

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
APPLICATION_URL = os.getenv("APPLICATION_URL")


router = APIRouter(prefix="/payment")


# ✅ Create Stripe Checkout Session (accepts price_id dynamically)
@router.post("/create-checkout-session", status_code=status.HTTP_200_OK, response_model=CheckoutSessionResponse)
async def create_checkout_session(data: CheckoutRequest,
                                  current_user: user_dependency,
                                  db: db_dependency):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized Access"
        )

    stmt = select(User).where(User.id == current_user["id"])
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found"
        )

    try:
        
        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email,
            line_items=[{
                "price": data.price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=APPLICATION_URL +
            "/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=APPLICATION_URL + "/cancel",
        )
        return CheckoutSessionResponse(url=checkout_session.url)

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Stripe Error: {str(e)}")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected Error: {str(e)}"
        )


# ✅ Stripe Webhook Endpoint
@router.post("/webhook", status_code=status.HTTP_200_OK, response_model=WebhookResponse)
async def stripe_webhook(request: Request, db: db_dependency):
    print("webhok trigered")
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Webhook Signature"
        )

    if event["type"] == "invoice.paid":
        invoice = event["data"]["object"]
        customer_email = invoice.get("customer_email")

        if customer_email:
            stmt = select(User).where(User.email == customer_email)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                subscription = Subscription(
                    customer_id=user.id,
                    source_id=invoice.get("subscription"),
                    currency=invoice.get("currency"),
                    amount=invoice.get("amount_paid") / 100,
                    started_at=invoice["lines"]["data"][0]["period"]["start"],
                    ended_at=invoice["lines"]["data"][0]["period"]["end"],
                    status="active"
                )
                db.add(subscription)
                await db.commit()

    elif event["type"] == "customer.subscription.deleted":
        subscription_obj = event["data"]["object"]
        stripe_sub_id = subscription_obj.get("id")

        stmt = select(Subscription).where(
            Subscription.source_id == stripe_sub_id)
        result = await db.execute(stmt)
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = "canceled"
            await db.commit()

    return WebhookResponse(status="success")
