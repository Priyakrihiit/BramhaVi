"""
Dynamic Audit Logging Middleware - BrahmaVidya Galaxy
Purpose: Captures state mutations and writes structural audit records of mutations to the database.
"""

import logging
import json
from django.utils.timezone import now

logger = logging.getLogger("audit")

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Read parameters before processing the request
        request.start_time = now()
        
        response = self.get_response(request)
        
        # Track write operations (POST, PUT, PATCH, DELETE) for systemic transparency
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            self._log_mutation_event(request, response)
            
        return response

    def _log_mutation_event(self, request, response):
        actor = getattr(request, "user", None)
        actor_id = getattr(actor, "id", "ANONYMOUS") if actor and actor.is_authenticated else "ANONYMOUS"
        
        log_payload = {
            "timestamp": now().isoformat(),
            "actor_id": str(actor_id),
            "method": request.method,
            "path": request.path,
            "ip_address": request.META.get("REMOTE_ADDR"),
            "status_code": response.status_code,
        }
        
        # Non-blocking payload emission - in production, this is pushed to the system activity log database ledger or Kafka
        logger.info(f"AUDIT_MUTATION_EVENT: {json.dumps(log_payload)}")
