"""
Property Report purchase and generation endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from config.database import get_db
from api.models.schemas import ReportPurchaseRequest, ReportPurchaseResponse
from api.models.database import PurchasedReport, ListingEnriched
from reports.generator import generate_report_task

router = APIRouter()


@router.post("/listing/{listing_id}/purchase-report", response_model=ReportPurchaseResponse)
def purchase_property_report(
    listing_id: int,
    request: ReportPurchaseRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Purchase a detailed property report for £5.

    This endpoint:
    1. Validates the listing exists
    2. Creates a Stripe payment intent
    3. Stores the purchase record
    4. Triggers report generation (async)
    5. Returns payment status and report URL (when ready)

    The report includes:
    - Full planning application details
    - Restrictive covenants (if available)
    - Detailed local area data
    - AVM with comparable properties
    - Schools, crime, flood maps
    - Transport links
    """

    # Verify listing exists
    listing = db.query(ListingEnriched).filter(
        ListingEnriched.listing_id == listing_id
    ).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Check if user already purchased this report
    existing = db.query(PurchasedReport).filter(
        PurchasedReport.user_id == request.user_id,
        PurchasedReport.listing_id == listing_id,
        PurchasedReport.payment_status == 'succeeded'
    ).first()

    if existing:
        # Already purchased, return existing report
        return ReportPurchaseResponse(
            report_id=existing.report_id,
            payment_intent_id=existing.payment_intent_id,
            payment_status='succeeded',
            report_url=existing.report_url,
            amount_gbp=existing.amount_gbp
        )

    # Create Stripe payment intent (MOCK for prototype)
    payment_intent = _create_payment_intent(
        amount_gbp=5.00,
        payment_method_id=request.payment_method_id,
        metadata={
            'user_id': request.user_id,
            'listing_id': listing_id
        }
    )

    # Create purchase record
    purchase = PurchasedReport(
        user_id=request.user_id,
        listing_id=listing_id,
        payment_intent_id=payment_intent['id'],
        amount_gbp=5.00,
        payment_status=payment_intent['status']
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    # If payment succeeded, trigger report generation
    if payment_intent['status'] == 'succeeded':
        background_tasks.add_task(
            generate_report_task,
            report_id=purchase.report_id,
            listing_id=listing_id
        )

    return ReportPurchaseResponse(
        report_id=purchase.report_id,
        payment_intent_id=payment_intent['id'],
        payment_status=payment_intent['status'],
        report_url=purchase.report_url,  # Will be None until generated
        amount_gbp=purchase.amount_gbp
    )


@router.get("/report/{report_id}")
def get_report_status(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Check status of a purchased report.

    Returns:
    - payment_status: pending, succeeded, failed
    - report_url: CloudFront URL (if generated)
    - generated_at: timestamp
    """

    report = db.query(PurchasedReport).filter(
        PurchasedReport.report_id == report_id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        'report_id': report.report_id,
        'payment_status': report.payment_status,
        'report_url': report.report_url,
        'generated_at': report.generated_at,
        'purchased_at': report.purchased_at
    }


def _create_payment_intent(amount_gbp: float, payment_method_id: str, metadata: dict) -> dict:
    """
    Create Stripe payment intent.

    MOCK IMPLEMENTATION for prototype.
    In production, use Stripe SDK:

    import stripe
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

    intent = stripe.PaymentIntent.create(
        amount=int(amount_gbp * 100),  # Convert to pence
        currency='gbp',
        payment_method=payment_method_id,
        confirm=True,
        metadata=metadata
    )
    return intent
    """

    # Mock successful payment
    import uuid
    return {
        'id': f'pi_{uuid.uuid4().hex[:24]}',
        'status': 'succeeded',  # or 'pending', 'failed'
        'amount': int(amount_gbp * 100),
        'currency': 'gbp'
    }
