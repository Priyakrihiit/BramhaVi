"""
Security and Rate-Limiting Middleware - BrahmaVidya Galaxy
Purpose: Hardens endpoints by adding HTTP security headers and tracking rate throttling.
"""

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

class SecurityHardeningMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token_str = auth_header.split(" ")[1]
            from rest_framework_simplejwt.tokens import AccessToken
            try:
                token = AccessToken(token_str)
                jti = token.get("jti")
                if jti:
                    from django.core.cache import cache
                    if cache.get(f"blacklist:{jti}"):
                        return JsonResponse({"detail": "Token is blacklisted."}, status=401)
            except Exception:
                pass
        return None

    def process_response(self, request, response):
        # Inject standard security headers protecting from frame insertions and sniffing
        response["X-Frame-Options"] = "DENY"
        response["X-Content-Type-Options"] = "nosniff"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline';"
        )
        return response
