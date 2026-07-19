"""
Wallet Transaction Authorization Gates - BrahmaVidya Galaxy
Purpose: Ensures financial queries are scoped strictly to verified owners or ledger operators.
"""

from rest_framework import permissions

class IsWalletOwnerOrAdmin(permissions.BasePermission):
    """
    Allows wallets to be viewed only by their owner, or by an Admin/Superadmin.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Admin/Superadmin bypass
        if user.is_superuser:
            return True
        if hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]:
            return True

        # Owner check
        if hasattr(obj, "user"):
            return obj.user == user
        elif hasattr(obj, "wallet"):
            return obj.wallet.user == user
        return False


class IsFinanceOrAdmin(permissions.BasePermission):
    """
    Grants permission to modify funds (credits/debits) strictly to Finance, Admin, or Superadmin roles.
    """
    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True
        if hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN", "FINANCE"]:
            return True

        return False

