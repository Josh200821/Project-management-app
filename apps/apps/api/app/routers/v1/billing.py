"""Billing router — Stripe integration."""

from fastapi import APIRouter, Request

from app.config import settings
from app.dependencies import CurrentUser, DbSession
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/billing")


@router.post("/checkout")
async def create_checkout(plan: str, org_id: str, current_user: CurrentUser):
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    price_map = {
        "pro": settings.STRIPE_PRO_PRICE_ID,
        "enterprise": settings.STRIPE_ENTERPRISE_PRICE_ID,
    }
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_map.get(plan, ""), "quantity": 1}],
        mode="subscription",
        success_url=f"{settings.FRONTEND_URL}/billing/success",
        cancel_url=f"{settings.FRONTEND_URL}/billing/cancel",
        metadata={"org_id": org_id, "user_id": str(current_user.id)},
    )
    return ApiResponse(data={"checkout_url": session.url})


@router.post("/webhook")
async def stripe_webhook(request: Request, session: DbSession):
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        return {"error": "Invalid signature"}
    # Handle subscription events via Celery
    from app.workers.report_tasks import handle_stripe_event

    handle_stripe_event.delay(event["type"], event["data"]["object"])
    return {"received": True}
