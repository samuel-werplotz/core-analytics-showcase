"""
Multi-Tenant Security Middleware Showcase.

Ensures every authenticated HTTP request is bound strictly to the user's active organization.
Rejects any organization_id incoming from HTTP parameters to prevent tenant impersonation.
"""
from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware responsible for setting `request.current_organization`.
    Enforces strict tenant isolation across the entire Django request lifecycle.
    """

    def process_request(self, request):
        # 1. Security Directive: Disallow frontend-provided organization overrides
        if "organization_id" in request.GET or "organization_id" in request.POST:
            raise PermissionDenied("Direct organization_id override in request parameters is forbidden.")

        # 2. Resolve organization exclusively via authenticated user session
        if request.user.is_authenticated:
            # Fetches active organization bound to user membership
            active_membership = request.user.memberships.filter(is_active=True).first()
            if active_membership:
                request.current_organization = active_membership.organization
            else:
                request.current_organization = None
        else:
            request.current_organization = None

    def process_response(self, request, response):
        return response
