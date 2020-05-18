from datetime import date
import logging

from django.conf import settings
from django.contrib.auth.models import User
from stripe import (
    Customer,
    Subscription,
    PaymentIntent
)

from lessons.models import UserProfile

MONTH = 'month'
YEAR = 'year'

API_KEY = settings.STRIPE_SECRET_KEY
PLAN_DICT = {
    MONTH: settings.STRIPE_PLAN_MONTHLY_ID,
    YEAR: settings.STRIPE_PLAN_ANNUAL_ID
}

logger = logging.getLogger(__name__)


def create_or_update_user_profile(user, timestamp_or_date):
    #
    # timestamp_or_date can be instance of
    #  (1) datetime.date
    #  (2) timestamp e.g. 122343454 = expressed as integer
    #  (3) timestamp e.g. 232321133 = expressed as string
    #
    #  (2) and (3) input is received from stripe API
    #  (1) is used in testing, just to make sure it works as expected

    if isinstance(timestamp_or_date, int):
        some_date = date.fromtimestamp(timestamp_or_date)
    elif isinstance(timestamp_or_date, str):
        some_date = date.fromtimestamp(int(timestamp_or_date))
    else:
        some_date = timestamp_or_date

    # some_date instance of datetime.date

    if hasattr(user, 'profile'):
        logger.info(
            f"user already has a profile; some_date={some_date}"
        )
        user.profile.update_pro_enddate(some_date)
        user.save()
        logger.info(f"pro_enddate={user.profile.pro_enddate}")
        logger.info(f"is_pro={user.profile.is_pro_user()}")
    else:
        profile = UserProfile(
            user=user,
            pro_enddate=some_date
        )
        profile.save()


class LessonsMonthPlan:
    def __init__(self):
        self.stripe_plan_id = settings.STRIPE_PLAN_MONTHLY_ID
        self.amount = 1995


class LessonsAnnualPlan:
    def __init__(self):
        self.stripe_plan_id = settings.STRIPE_PLAN_ANNUAL_ID
        self.amount = 19950


class LessonsPlan:
    def __init__(self, plan_id):
        """
        plan_id is either string 'm' (stands for monthly)
        or a string letter 'a' (which stands for annual)
        """
        if plan_id == 'm':
            self.plan = LessonsMonthPlan()
            self.id = 'm'
        elif plan_id == 'a':
            self.plan = LessonsAnnualPlan()
            self.id = 'a'
        else:
            raise ValueError('Invalid plan_id value')

        self.currency = 'usd'

    @property
    def stripe_plan_id(self):
        return self.plan.stripe_plan_id

    @property
    def amount(self):
        return self.plan.amount


def create_payment_intent(
    lesson_plan,
    payment_method_type="card"
):
    payment_intent = PaymentIntent.create(
        api_key=API_KEY,
        amount=lesson_plan.amount,
        currency=lesson_plan.currency,
        payment_method_types=[payment_method_type],
    )
    return payment_intent.client_secret


def create_payment_subscription(
    email,
    lesson_plan,  # = 'month' | 'year'
    payment_method_id
):
    customer = Customer.create(
        api_key=API_KEY,
        email=email,
        payment_method=payment_method_id,
        invoice_settings={
            'default_payment_method': payment_method_id,
        },
    )

    subscription = Subscription.create(
        api_key=API_KEY,
        customer=customer.id,
        items=[
            {
                'plan': lesson_plan.stripe_plan_id,
            },
        ],
    )
    return subscription.status


def upgrade_customer(invoice):
    """
    invoice = is stripe.invoice object instance
    from invoice.payment_succeeded webhook
    """
    # invoice['customer_email']
    # invoice['paid'] = true|false
    # invoice['current_period_end'] # timestamp of end of subscription
    email = invoice['customer_email']
    logger.info(f"email={email}")
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.warning(
            f"User with email {email} not found while trying to upgrade to PRO"
        )
        return False

    subscr = Subscription.retrieve(
        api_key=API_KEY,
        id=invoice['subscription']
    )

    current_period_end = subscr['current_period_end']
    logger.info(f"subscription_id={invoice['subscription']}")
    logger.info(f"invoice paid = {invoice['paid']}")
    logger.info(f"pro_enddate= {subscr['current_period_end']}")

    if invoice['paid']:
        create_or_update_user_profile(user, current_period_end)
        logger.info(
            f"Profile with {current_period_end} saved for user {email}"
        )
    else:
        logger.info("Invoice is was NOT paid!")

    return True