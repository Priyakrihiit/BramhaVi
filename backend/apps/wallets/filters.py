"""
Wallet and Payments Filters - BrahmaVidya Galaxy
Purpose: Mappings for Django filters supporting API ordering and search selectors.
"""

import django_filters
from apps.wallets.models import Transaction, Payment, Invoice, UserSubscription, TeacherPayout

class TransactionFilter(django_filters.FilterSet):
    class Meta:
        model = Transaction
        fields = {
            "type": ["exact"],
            "amount": ["gte", "lte"],
            "created_at": ["gte", "lte"],
        }

class PaymentFilter(django_filters.FilterSet):
    class Meta:
        model = Payment
        fields = {
            "status": ["exact"],
            "amount": ["gte", "lte"],
            "payment_gateway": ["exact"],
            "created_at": ["gte", "lte"],
        }

class InvoiceFilter(django_filters.FilterSet):
    class Meta:
        model = Invoice
        fields = {
            "status": ["exact"],
            "total": ["gte", "lte"],
            "created_at": ["gte", "lte"],
        }

class UserSubscriptionFilter(django_filters.FilterSet):
    class Meta:
        model = UserSubscription
        fields = {
            "status": ["exact"],
            "expires_at": ["gte", "lte"],
        }

class TeacherPayoutFilter(django_filters.FilterSet):
    class Meta:
        model = TeacherPayout
        fields = {
            "status": ["exact"],
            "amount": ["gte", "lte"],
            "created_at": ["gte", "lte"],
        }
