"""
Standardized API Response Utility - BrahmaVidya Galaxy
Purpose: Wraps standard payload containers for success, error, and list items.
"""

from typing import Any, Optional
from django.http import JsonResponse
from rest_framework import status

def api_success(data: Any = None, message: str = "Operation completed successfully", status_code: int = status.HTTP_200_OK) -> JsonResponse:
    """
    Returns a unified success response envelope.
    """
    return JsonResponse({
        "success": True,
        "message": message,
        "data": data,
        "error": None
    }, status=status_code)

def api_error(message: str, error_code: str, details: Optional[Any] = None, status_code: int = status.HTTP_400_BAD_REQUEST) -> JsonResponse:
    """
    Returns a structured error response envelope to simplify frontend error mapping.
    """
    return JsonResponse({
        "success": False,
        "message": message,
        "data": None,
        "error": {
            "code": error_code,
            "details": details
        }
    }, status=status_code)
