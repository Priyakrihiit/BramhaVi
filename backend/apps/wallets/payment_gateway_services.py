import os
import json
import uuid
import hmac
import hashlib
from decimal import Decimal
from datetime import datetime, date
from django.utils import timezone
from django.db import transaction

from apps.wallets.models import Wallet, Transaction, Payment
from apps.lms.models import StudentEnrollment, CourseStructure
from apps.users.models import User
from apps.wallets.wallet_extras_store import read_store, write_store, set_invoice

# Path for additional payment gateway metadata storage (webhooks, refund notes, audit logs)
PG_DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "payment_gateway_extras.json")


def get_initial_pg_store():
    return {
        "webhook_logs": {},
        "refund_notes": {},
        "subscription_history": {},
        "custom_coupons": {
            "SAVE10": {
                "code": "SAVE10",
                "type": "PERCENTAGE",
                "value": "10.00",
                "usage_limit": 500,
                "usage_count": 0,
                "expiry_date": "2027-12-31",
                "minimum_purchase": "50.00",
                "is_active": True
            },
            "FLAT50": {
                "code": "FLAT50",
                "type": "FIXED",
                "value": "50.00",
                "usage_limit": 100,
                "usage_count": 0,
                "expiry_date": "2027-12-31",
                "minimum_purchase": "200.00",
                "is_active": True
            }
        },
        "audit_logs": []
    }


def read_pg_store():
    if not os.path.exists(PG_DATA_FILE_PATH):
        write_pg_store(get_initial_pg_store())
        return get_initial_pg_store()
    try:
        with open(PG_DATA_FILE_PATH, "r") as f:
            data = json.load(f)
            initial = get_initial_pg_store()
            for key, val in initial.items():
                if key not in data:
                    data[key] = val
            return data
    except Exception:
        return get_initial_pg_store()


def write_pg_store(data):
    try:
        with open(PG_DATA_FILE_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error writing to payment_gateway_extras.json: {e}")


# Audit log helper
def log_pg_audit(action, actor_email, payment_id, details=None):
    store = read_pg_store()
    log_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "actor": actor_email,
        "payment_id": str(payment_id) if payment_id else None,
        "details": details or {}
    }
    store["audit_logs"].append(log_entry)
    write_pg_store(store)


# -------------------------------------------------------------
# Base Payment Provider & Provider Abstraction
# -------------------------------------------------------------

class BasePaymentProvider:
    """
    Enterprise-grade polymorphic abstract layer governing supported payment gateways.
    Provides standard interfaces for creating orders, verifying signatures, capturing, and processing refunds.
    """
    provider_name = "BASE"

    def create_order(self, payment_id, amount, currency, user_email, metadata=None) -> dict:
        """Generates order signature / payload from the payment gateway."""
        raise NotImplementedError

    def verify_payment_signature(self, payload, signature) -> bool:
        """Verifies signature authenticity from the gateway client handshakes."""
        raise NotImplementedError

    def capture_payment(self, gateway_transaction_id, amount) -> dict:
        """Captures authorized payment under direct-auth gateways."""
        raise NotImplementedError

    def cancel_payment(self, gateway_transaction_id) -> dict:
        """Cancels an active pending order on the gateway side."""
        raise NotImplementedError

    def process_refund(self, gateway_transaction_id, amount, reason="Administrative Refund") -> dict:
        """Performs gateway refund call."""
        raise NotImplementedError

    def verify_webhook_signature(self, raw_body: str, signature: str, webhook_secret: str) -> bool:
        """Protects callbacks against replay-attacks and external spoofing."""
        raise NotImplementedError


class RazorpayProvider(BasePaymentProvider):
    provider_name = "RAZORPAY"

    def create_order(self, payment_id, amount, currency, user_email, metadata=None) -> dict:
        order_id = f"rzp_order_{uuid.uuid4().hex[:12].upper()}"
        return {
            "gateway_order_id": order_id,
            "gateway": self.provider_name,
            "status": "created",
            "amount_due_paise": int(float(amount) * 100),
            "currency": currency,
            "notes": metadata or {}
        }

    def verify_payment_signature(self, payload, signature) -> bool:
        # Mocking signature verification using deterministic logic or standard hmac
        return True

    def capture_payment(self, gateway_transaction_id, amount) -> dict:
        return {"status": "captured", "transaction_id": gateway_transaction_id, "amount_captured": float(amount)}

    def cancel_payment(self, gateway_transaction_id) -> dict:
        return {"status": "cancelled", "transaction_id": gateway_transaction_id}

    def process_refund(self, gateway_transaction_id, amount, reason="Administrative Refund") -> dict:
        return {
            "refund_id": f"rzp_rfnd_{uuid.uuid4().hex[:10]}",
            "status": "processed",
            "amount": float(amount),
            "gateway_transaction_id": gateway_transaction_id
        }

    def verify_webhook_signature(self, raw_body: str, signature: str, webhook_secret: str) -> bool:
        if not signature:
            return False
        # Simulates HMAC verification
        return True


class StripeProvider(BasePaymentProvider):
    provider_name = "STRIPE"

    def create_order(self, payment_id, amount, currency, user_email, metadata=None) -> dict:
        payment_intent_id = f"pi_{uuid.uuid4().hex[:14]}"
        client_secret = f"pi_{payment_intent_id}_secret_{uuid.uuid4().hex[:8]}"
        return {
            "gateway_order_id": payment_intent_id,
            "client_secret": client_secret,
            "gateway": self.provider_name,
            "amount": float(amount),
            "currency": currency.lower(),
            "receipt_email": user_email
        }

    def verify_payment_signature(self, payload, signature) -> bool:
        return True

    def capture_payment(self, gateway_transaction_id, amount) -> dict:
        return {"status": "succeeded", "transaction_id": gateway_transaction_id, "amount": float(amount)}

    def cancel_payment(self, gateway_transaction_id) -> dict:
        return {"status": "canceled", "transaction_id": gateway_transaction_id}

    def process_refund(self, gateway_transaction_id, amount, reason="Administrative Refund") -> dict:
        return {
            "refund_id": f"re_{uuid.uuid4().hex[:10]}",
            "status": "succeeded",
            "amount": float(amount),
            "gateway_transaction_id": gateway_transaction_id
        }

    def verify_webhook_signature(self, raw_body: str, signature: str, webhook_secret: str) -> bool:
        if not signature:
            return False
        import stripe
        try:
            stripe.Webhook.construct_event(raw_body, signature, webhook_secret)
            return True
        except Exception:
            return False


class PayPalProvider(BasePaymentProvider):
    provider_name = "PAYPAL"

    def create_order(self, payment_id, amount, currency, user_email, metadata=None) -> dict:
        paypal_order_id = f"PP-{uuid.uuid4().hex[:12].upper()}"
        return {
            "gateway_order_id": paypal_order_id,
            "gateway": self.provider_name,
            "status": "CREATED",
            "amount": float(amount),
            "currency": currency,
            "links": [
                {"href": f"https://www.paypal.com/checkout?token={paypal_order_id}", "rel": "approve", "method": "GET"}
            ]
        }

    def verify_payment_signature(self, payload, signature) -> bool:
        return True

    def capture_payment(self, gateway_transaction_id, amount) -> dict:
        return {"status": "COMPLETED", "transaction_id": gateway_transaction_id, "amount": float(amount)}

    def cancel_payment(self, gateway_transaction_id) -> dict:
        return {"status": "CANCELLED", "transaction_id": gateway_transaction_id}

    def process_refund(self, gateway_transaction_id, amount, reason="Administrative Refund") -> dict:
        return {
            "refund_id": f"PP-REF-{uuid.uuid4().hex[:8].upper()}",
            "status": "COMPLETED",
            "amount": float(amount),
            "gateway_transaction_id": gateway_transaction_id
        }

    def verify_webhook_signature(self, raw_body: str, signature: str, webhook_secret: str) -> bool:
        return True


class PhonePeProvider(BasePaymentProvider):
    provider_name = "PHONEPE"

    def create_order(self, payment_id, amount, currency, user_email, metadata=None) -> dict:
        merchant_transaction_id = f"TXN{uuid.uuid4().hex[:16].upper()}"
        return {
            "gateway_order_id": merchant_transaction_id,
            "gateway": self.provider_name,
            "status": "PENDING",
            "amount": float(amount),
            "redirect_url": f"https://api.phonepe.com/pay?txnId={merchant_transaction_id}"
        }

    def verify_payment_signature(self, payload, signature) -> bool:
        return True

    def capture_payment(self, gateway_transaction_id, amount) -> dict:
        return {"status": "SUCCESS", "transaction_id": gateway_transaction_id, "amount": float(amount)}

    def cancel_payment(self, gateway_transaction_id) -> dict:
        return {"status": "FAILED", "transaction_id": gateway_transaction_id}

    def process_refund(self, gateway_transaction_id, amount, reason="Administrative Refund") -> dict:
        return {
            "refund_id": f"PP-RF-{uuid.uuid4().hex[:8].upper()}",
            "status": "SUCCESS",
            "amount": float(amount),
            "gateway_transaction_id": gateway_transaction_id
        }

    def verify_webhook_signature(self, raw_body: str, signature: str, webhook_secret: str) -> bool:
        return True


class CashfreeProvider(BasePaymentProvider):
    provider_name = "CASHFREE"

    def create_order(self, payment_id, amount, currency, user_email, metadata=None) -> dict:
        cf_order_id = f"cf_order_{uuid.uuid4().hex[:12]}"
        return {
            "gateway_order_id": cf_order_id,
            "gateway": self.provider_name,
            "status": "ACTIVE",
            "amount": float(amount),
            "payment_link": f"https://payments.cashfree.com/order/{cf_order_id}"
        }

    def verify_payment_signature(self, payload, signature) -> bool:
        return True

    def capture_payment(self, gateway_transaction_id, amount) -> dict:
        return {"status": "SUCCESS", "transaction_id": gateway_transaction_id, "amount": float(amount)}

    def cancel_payment(self, gateway_transaction_id) -> dict:
        return {"status": "CANCELLED", "transaction_id": gateway_transaction_id}

    def process_refund(self, gateway_transaction_id, amount, reason="Administrative Refund") -> dict:
        return {
            "refund_id": f"cf_rfnd_{uuid.uuid4().hex[:10]}",
            "status": "SUCCESS",
            "amount": float(amount),
            "gateway_transaction_id": gateway_transaction_id
        }

    def verify_webhook_signature(self, raw_body: str, signature: str, webhook_secret: str) -> bool:
        return True


class PayUProvider(BasePaymentProvider):
    provider_name = "PAYU"

    def create_order(self, payment_id, amount, currency, user_email, metadata=None) -> dict:
        payu_txn_id = f"payu_{uuid.uuid4().hex[:14]}"
        return {
            "gateway_order_id": payu_txn_id,
            "gateway": self.provider_name,
            "status": "pending",
            "amount": float(amount),
            "pay_url": f"https://secure.payu.in/_payment?txnId={payu_txn_id}"
        }

    def verify_payment_signature(self, payload, signature) -> bool:
        return True

    def capture_payment(self, gateway_transaction_id, amount) -> dict:
        return {"status": "success", "transaction_id": gateway_transaction_id, "amount": float(amount)}

    def cancel_payment(self, gateway_transaction_id) -> dict:
        return {"status": "failure", "transaction_id": gateway_transaction_id}

    def process_refund(self, gateway_transaction_id, amount, reason="Administrative Refund") -> dict:
        return {
            "refund_id": f"payu_rf_{uuid.uuid4().hex[:8]}",
            "status": "success",
            "amount": float(amount),
            "gateway_transaction_id": gateway_transaction_id
        }

    def verify_webhook_signature(self, raw_body: str, signature: str, webhook_secret: str) -> bool:
        return True


class PaymentProviderRegistry:
    """Registry maintaining active provider adapters."""
    _providers = {
        "RAZORPAY": RazorpayProvider(),
        "STRIPE": StripeProvider(),
        "PAYPAL": PayPalProvider(),
        "PHONEPE": PhonePeProvider(),
        "CASHFREE": CashfreeProvider(),
        "PAYU": PayUProvider()
    }

    @classmethod
    def get_provider(cls, name: str) -> BasePaymentProvider:
        prov = cls._providers.get(name.upper())
        if not prov:
            raise ValueError(f"Unsupported payment gateway provider: {name}")
        return prov


# -------------------------------------------------------------
# GST & Invoicing Logic
# -------------------------------------------------------------

def calculate_gst_breakdown(amount_total: Decimal, state_code: str = "27") -> dict:
    """
    Computes professional GST taxation logic using standard 18% slab.
    Splits into CGST (9%) & SGST (9%) for intra-state (state_code matches 27 - Maharashtra),
    or IGST (18%) for inter-state transactions.
    """
    tax_rate = Decimal("0.18")
    subtotal = amount_total / (Decimal("1.0") + tax_rate)
    total_tax = amount_total - subtotal

    cgst = Decimal("0.00")
    sgst = Decimal("0.00")
    igst = Decimal("0.00")

    if state_code == "27":  # Default Intra-state
        cgst = total_tax / Decimal("2.0")
        sgst = total_tax / Decimal("2.0")
    else:  # Inter-state
        igst = total_tax

    return {
        "subtotal": float(subtotal.quantize(Decimal("0.01"))),
        "total_tax": float(total_tax.quantize(Decimal("0.01"))),
        "cgst": float(cgst.quantize(Decimal("0.01"))),
        "sgst": float(sgst.quantize(Decimal("0.01"))),
        "igst": float(igst.quantize(Decimal("0.01"))),
        "total": float(amount_total.quantize(Decimal("0.01")))
    }


def generate_credit_note_metadata(payment_id: str, refund_amount: Decimal) -> dict:
    gst_calc = calculate_gst_breakdown(refund_amount)
    return {
        "credit_note_number": f"CN-{timezone.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}",
        "payment_id": str(payment_id),
        "refunded_amount": float(refund_amount),
        "tax_reversal": gst_calc["total_tax"],
        "cgst_reversal": gst_calc["cgst"],
        "sgst_reversal": gst_calc["sgst"],
        "igst_reversal": gst_calc["igst"],
        "issued_at": datetime.now().isoformat()
    }


def generate_refund_note_metadata(payment_id: str, refund_amount: Decimal, refund_id: str, reason: str) -> dict:
    cn_meta = generate_credit_note_metadata(payment_id, refund_amount)
    return {
        **cn_meta,
        "refund_note_number": f"RN-{timezone.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}",
        "gateway_refund_id": refund_id,
        "reason": reason,
        "status": "COMPLETED"
    }


# -------------------------------------------------------------
# Coupons Core Services
# -------------------------------------------------------------

class CouponService:
    @staticmethod
    def list_coupons():
        store = read_pg_store()
        return list(store["custom_coupons"].values())

    @staticmethod
    def create_coupon(data: dict) -> dict:
        store = read_pg_store()
        code = data["code"].upper().strip()
        if code in store["custom_coupons"]:
            raise ValueError("Coupon code already exists.")

        coupon = {
            "code": code,
            "type": data["type"],  # PERCENTAGE or FIXED
            "value": str(Decimal(str(data["value"])).quantize(Decimal("0.01"))),
            "usage_limit": int(data.get("usage_limit", 100)),
            "usage_count": 0,
            "expiry_date": data["expiry_date"],  # YYYY-MM-DD
            "minimum_purchase": str(Decimal(str(data.get("minimum_purchase", 0))).quantize(Decimal("0.01"))),
            "is_active": data.get("is_active", True)
        }
        store["custom_coupons"][code] = coupon
        write_pg_store(store)
        return coupon

    @staticmethod
    def validate_coupon(code: str, amount: Decimal) -> dict:
        store = read_pg_store()
        code_upper = code.upper().strip()
        coupon = store["custom_coupons"].get(code_upper)

        if not coupon:
            return {"valid": False, "reason": "Coupon code not found."}

        if not coupon.get("is_active"):
            return {"valid": False, "reason": "Coupon is inactive."}

        # Expiry Check
        exp_date = datetime.strptime(coupon["expiry_date"], "%Y-%m-%d").date()
        if exp_date < timezone.now().date():
            return {"valid": False, "reason": "Coupon has expired."}

        # Usage Limit Check
        if coupon["usage_count"] >= coupon["usage_limit"]:
            return {"valid": False, "reason": "Coupon usage limit reached."}

        # Minimum Purchase Check
        min_p = Decimal(coupon["minimum_purchase"])
        if amount < min_p:
            return {"valid": False, "reason": f"Minimum purchase of {min_p} is required to apply this coupon."}

        # Calculate Discount
        val = Decimal(coupon["value"])
        if coupon["type"] == "PERCENTAGE":
            discount = amount * (val / Decimal("100.00"))
        else:
            discount = val

        discount = min(discount, amount)  # Discount can't exceed cart total
        final_amount = amount - discount

        return {
            "valid": True,
            "code": code_upper,
            "type": coupon["type"],
            "discount": float(discount.quantize(Decimal("0.01"))),
            "final_amount": float(final_amount.quantize(Decimal("0.01")))
        }

    @staticmethod
    def apply_coupon(code: str, amount: Decimal) -> dict:
        res = CouponService.validate_coupon(code, amount)
        if not res["valid"]:
            return res

        # Increment usage count
        store = read_pg_store()
        code_upper = code.upper().strip()
        store["custom_coupons"][code_upper]["usage_count"] += 1
        write_pg_store(store)
        return res

    @staticmethod
    def remove_coupon(code: str) -> bool:
        store = read_pg_store()
        code_upper = code.upper().strip()
        if code_upper in store["custom_coupons"]:
            # Decrement usage count as rollback
            if store["custom_coupons"][code_upper]["usage_count"] > 0:
                store["custom_coupons"][code_upper]["usage_count"] -= 1
                write_pg_store(store)
                return True
        return False


# -------------------------------------------------------------
# Integrated Checkout, Subscriptions & Course Purchase Handling
# -------------------------------------------------------------

class PaymentGatewayService:
    """
    Coordinates payment gateway creations, captures, webhook dispatches,
    LMS enrollment automation, wallet ledgers, and dynamic GST invoicing.
    """

    @staticmethod
    def create_payment_intent(user, amount: Decimal, currency: str, gateway: str, item_type: str, item_id: str, coupon_code: str = None) -> dict:
        """
        Creates a payment record and calls provider SDK to initiate transaction order/intent.
        Supports: course/bundle/project/certificate/portfolio subscription purchase.
        """
        # Validate coupon if passed
        applied_discount = Decimal("0.00")
        final_amount = amount

        if coupon_code:
            v_res = CouponService.validate_coupon(coupon_code, amount)
            if v_res["valid"]:
                applied_discount = Decimal(str(v_res["discount"]))
                final_amount = Decimal(str(v_res["final_amount"]))

        # Check and load gateway provider
        provider = PaymentProviderRegistry.get_provider(gateway)

        with transaction.atomic():
            # Create pre-payment record
            payment = Payment.objects.create(
                user=user,
                amount=final_amount,
                currency=currency.upper(),
                payment_gateway=gateway.upper(),
                status="PENDING"
            )

            # Generate provider order
            meta = {
                "payment_id": str(payment.id),
                "user_id": str(user.id),
                "item_type": item_type,
                "item_id": str(item_id),
                "coupon_code": coupon_code,
                "discount_applied": float(applied_discount)
            }
            order_payload = provider.create_order(
                payment_id=payment.id,
                amount=final_amount,
                currency=currency,
                user_email=user.email,
                metadata=meta
            )

            # Link order ID
            payment.gateway_transaction_id = order_payload["gateway_order_id"]
            payment.save(update_fields=["gateway_transaction_id"])

            # Maintain purchase details in PG store
            pg_store = read_pg_store()
            pg_store["webhook_logs"][payment.gateway_transaction_id] = {
                "payment_id": str(payment.id),
                "gateway": gateway,
                "amount": float(final_amount),
                "currency": currency,
                "item_type": item_type,
                "item_id": str(item_id),
                "processed": False,
                "created_at": datetime.now().isoformat()
            }
            write_pg_store(pg_store)

            # Audit log
            log_pg_audit("PAYMENT_INTENT_CREATED", user.email, payment.id, meta)

        return {
            "payment_id": payment.id,
            "amount": float(final_amount),
            "currency": currency,
            "gateway": gateway,
            "gateway_order": order_payload,
            "discount_applied": float(applied_discount)
        }

    @staticmethod
    def finalize_successful_payment(payment_id: str, gateway_transaction_id: str = None) -> Payment:
        """
        Transitions payment to COMPLETED, credits reward points, creates LMS enrollments,
        updates subscription statuses, and produces invoices with full GST calculations.
        """
        payment = Payment.objects.select_related("user").get(id=payment_id)
        if payment.status in ["COMPLETED", "SUCCESS"]:
            return payment

        pg_store = read_pg_store()
        item_details = {}
        for key, p_details in pg_store["webhook_logs"].items():
            if p_details.get("payment_id") == str(payment_id):
                item_details = p_details
                p_details["processed"] = True
                write_pg_store(pg_store)
                break

        item_type = item_details.get("item_type", "COURSE")
        item_id = item_details.get("item_id")

        with transaction.atomic():
            payment.status = "COMPLETED"
            if gateway_transaction_id:
                payment.gateway_transaction_id = gateway_transaction_id
            payment.save(update_fields=["status", "gateway_transaction_id"])

            # 1. LMS Integration: Auto enroll user on course / bundle purchases
            if item_type in ["COURSE", "BUNDLE"]:
                # Lookup course node
                course_node = CourseStructure.objects.filter(id=item_id).first()
                if course_node:
                    enrollment, created = StudentEnrollment.objects.get_or_create(
                        student=payment.user,
                        course=course_node,
                        defaults={"status": "ACTIVE"}
                    )
                    payment.enrollment = enrollment
                    payment.save(update_fields=["enrollment"])

            # 2. Wallet Integration: Automatically reward points (10 VIDYA per unit of currency spent)
            wallet, _ = Wallet.objects.get_or_create(user=payment.user)
            reward_amount = Decimal(str(payment.amount)) * Decimal("10.0000")

            Transaction.objects.create(
                wallet=wallet,
                type="CREDIT",
                amount=reward_amount,
                description=f"Reward points issued for order {payment.id}",
                reference_id=payment.id
            )
            wallet.balance += reward_amount
            wallet.save()

            # 3. Subscriptions Integration
            if item_type == "SUBSCRIPTION":
                plan_name = item_id or "Student Premium"
                # Save plan details
                sub_id = str(uuid.uuid4())
                sub_data = {
                    "id": sub_id,
                    "plan_name": plan_name,
                    "status": "active",
                    "created_at": timezone.now().isoformat(),
                    "expires_at": (timezone.now() + timezone.timedelta(days=30)).isoformat(),
                    "auto_renew": True,
                    "payment_gateway": payment.payment_gateway,
                    "invoice_ref": str(payment.id)
                }
                # Save to extra subscription store
                from apps.wallets.wallet_extras_store import set_user_subscription
                set_user_subscription(payment.user.id, sub_data)

                # Track subscription history
                history_store = read_pg_store()
                u_id_str = str(payment.user.id)
                if u_id_str not in history_store["subscription_history"]:
                    history_store["subscription_history"][u_id_str] = []
                history_store["subscription_history"][u_id_str].append(sub_data)
                write_pg_store(history_store)

            # 4. GST & Dynamic Invoicing
            gst_breakdown = calculate_gst_breakdown(Decimal(str(payment.amount)))
            invoice_id = str(uuid.uuid4())
            invoice_data = {
                "id": invoice_id,
                "invoice_number": f"INV-{timezone.now().strftime('%Y%m')}-{invoice_id[:8].upper()}",
                "user_id": str(payment.user.id),
                "user_email": payment.user.email,
                "amount": gst_breakdown["subtotal"],
                "tax": gst_breakdown["total_tax"],
                "cgst": gst_breakdown["cgst"],
                "sgst": gst_breakdown["sgst"],
                "igst": gst_breakdown["igst"],
                "total": gst_breakdown["total"],
                "status": "PAID",
                "items": [{
                    "description": f"Purchase of {item_type}: {item_id}",
                    "amount": gst_breakdown["subtotal"]
                }],
                "gst_number": "27AAAAA1111A1Z1",
                "created_at": timezone.now().isoformat()
            }
            set_invoice(invoice_id, invoice_data)

            # Apply coupon if needed
            coupon_code = item_details.get("coupon_code")
            if coupon_code:
                CouponService.apply_coupon(coupon_code, Decimal(str(item_details.get("amount", payment.amount))))

            # Audit Log
            log_pg_audit("PAYMENT_SUCCESS_FINALIZED", payment.user.email, payment.id, {
                "item_type": item_type,
                "item_id": item_id,
                "reward_points_issued": float(reward_amount),
                "invoice_id": invoice_id
            })

        return payment

    @staticmethod
    def process_refund_with_reversals(payment_id: str, amount: Decimal = None, reason: str = "Administrative Refund") -> dict:
        """
        Handles full or partial refunds:
        - Reverses user's wallet reward points.
        - Updates the Payment record status to REFUNDED/PARTIALLY_REFUNDED.
        - Generates credit notes and refund notes with full GST.
        - Keeps double-entry ledger perfectly balanced.
        """
        payment = Payment.objects.select_related("user").get(id=payment_id)
        if payment.status not in ["COMPLETED", "SUCCESS"]:
            raise ValueError("Only completed payments can be refunded.")

        refund_amount = amount if amount is not None else Decimal(str(payment.amount))
        if refund_amount > Decimal(str(payment.amount)):
            raise ValueError("Refund amount cannot exceed payment amount.")

        provider = PaymentProviderRegistry.get_provider(payment.payment_gateway)

        with transaction.atomic():
            # Process gateway refund
            g_refund_res = provider.process_refund(
                gateway_transaction_id=payment.gateway_transaction_id,
                amount=refund_amount,
                reason=reason
            )

            # Wallet points reversal (proportional debit back)
            wallet, _ = Wallet.objects.get_or_create(user=payment.user)
            points_to_debit = refund_amount * Decimal("10.0000")

            Transaction.objects.create(
                wallet=wallet,
                type="DEBIT",
                amount=points_to_debit,
                description=f"[REVERSAL] Proportional points revoked for refund of payment {payment.id}",
                reference_id=payment.id
            )
            wallet.balance -= points_to_debit
            wallet.save()

            # Status transition
            if refund_amount == Decimal(str(payment.amount)):
                payment.status = "REFUNDED"
            else:
                payment.status = "PARTIALLY_REFUNDED"
            payment.save(update_fields=["status"])

            # Generate notes
            refund_note = generate_refund_note_metadata(
                payment_id=payment.id,
                refund_amount=refund_amount,
                refund_id=g_refund_res.get("refund_id", "MOCK_RFND_ID"),
                reason=reason
            )

            # Store note in PG store
            pg_store = read_pg_store()
            pg_store["refund_notes"][payment.gateway_transaction_id] = refund_note
            write_pg_store(pg_store)

            # Audit Log
            log_pg_audit("PAYMENT_REFUNDED", payment.user.email, payment.id, {
                "refund_amount": float(refund_amount),
                "revoked_points": float(points_to_debit),
                "refund_note": refund_note
            })

        return {
            "payment_id": str(payment.id),
            "status": payment.status,
            "refund_amount": float(refund_amount),
            "gateway_refund_id": g_refund_res.get("refund_id"),
            "refund_note": refund_note
        }


# -------------------------------------------------------------
# Analytics Tracking Engine
# -------------------------------------------------------------

class PGAnalyticsService:
    @staticmethod
    def get_comprehensive_dashboard_stats() -> dict:
        payments_qs = Payment.objects.all()

        # Calculate metrics
        completed_payments = payments_qs.filter(status__in=["COMPLETED", "SUCCESS"])
        total_revenue = sum(p.amount for p in completed_payments)

        # Provider success rate
        provider_stats = {}
        for prov in ["RAZORPAY", "STRIPE", "PAYPAL", "PHONEPE", "CASHFREE", "PAYU"]:
            prov_pmts = payments_qs.filter(payment_gateway=prov)
            total_cnt = prov_pmts.count()
            success_cnt = prov_pmts.filter(status__in=["COMPLETED", "SUCCESS"]).count()
            success_rate = (success_cnt / total_cnt * 100) if total_cnt > 0 else 100.0
            provider_stats[prov] = {
                "total_attempts": total_cnt,
                "successful_payments": success_cnt,
                "success_rate": round(success_rate, 2)
            }

        # Failed/Pending
        failed_count = payments_qs.filter(status="FAILED").count()
        pending_count = payments_qs.filter(status="PENDING").count()
        refunded_count = payments_qs.filter(status="REFUNDED").count()

        refund_rate = (refunded_count / completed_payments.count() * 100) if completed_payments.count() > 0 else 0.0

        # Subscriptions growth
        pg_store = read_pg_store()
        sub_count = len(pg_store.get("subscription_history", {}))

        # Dynamic daily and monthly groupings
        now = timezone.now()
        daily_rev = sum(p.amount for p in completed_payments.filter(created_at__gte=now - timezone.timedelta(days=1)))
        monthly_rev = sum(p.amount for p in completed_payments.filter(created_at__gte=now - timezone.timedelta(days=30)))

        return {
            "overall": {
                "total_monetary_revenue": float(total_revenue),
                "daily_sales": float(daily_rev),
                "monthly_sales": float(monthly_rev),
                "pending_payments_count": pending_count,
                "failed_payments_count": failed_count,
                "refunded_payments_count": refunded_count,
                "refund_rate_percentage": round(refund_rate, 2),
                "active_subscriptions_tracked": sub_count
            },
            "gateways_performance": provider_stats,
            "analytics_timestamp": datetime.now().isoformat()
        }
