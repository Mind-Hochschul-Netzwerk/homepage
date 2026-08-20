"""
Authelia RemoteUser Backend with LDAP Group Synchronization
"""

from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.models import Group
from django.contrib.auth.middleware import RemoteUserMiddleware


class AutheliaRemoteUserMiddleware(RemoteUserMiddleware):
    header = "REMOTE_USER"

    # Traefik only forwards to Authelia for /admin/ and /django-admin/, not
    # for every request (e.g. static assets). Without this, any request that
    # doesn't carry the header would log the user out of their still-valid
    # session, rotating the CSRF token from under them mid-visit.
    force_logout_if_no_header = False

    def process_request(self, request):
        if (
            "HTTP_REMOTE_USER" in request.META
            and "REMOTE_USER" not in request.META
        ):
            request.META["REMOTE_USER"] = request.META["HTTP_REMOTE_USER"]
        return super().process_request(request)

    async def aprocess_request(self, request):
        if (
            "HTTP_REMOTE_USER" in request.META
            and "REMOTE_USER" not in request.META
        ):
            request.META["REMOTE_USER"] = request.META["HTTP_REMOTE_USER"]
        return await super().aprocess_request(request)


class AutheliaRemoteUserBackend(RemoteUserBackend):
    """
    Backend that authenticates users via Authelia's forward auth headers.

    Expects headers:
    - Remote-User: username (required)
    - Remote-Groups: comma-separated group names (optional)
    - Remote-Name: full name (optional)
    - Remote-Email: email address (optional)
    """

    create_unknown_user = True

    # LDAP groups mapped to Wagtail/Django admin access. Membership is
    # re-derived from LDAP on every login, so removing someone from these
    # groups revokes access on their next login without manual cleanup here.
    WEBREDAKTION_GROUP = "webredaktion"
    WEBADMIN_GROUP = "webadmin"

    def authenticate(self, request, remote_user=None):
        """
        Authenticate via remote user header and sync groups from Remote-Groups header.
        """
        from logging import getLogger

        logger = getLogger("wagtail")
        logger.info(f"Authenticating user: {remote_user}")
        logger.debug(f"Request META: {request.META}")
        user = super().authenticate(request, remote_user)
        if not user or not request:
            return user

        # Extract groups from HTTP_REMOTE_GROUPS header. Only the groups
        # relevant to this app are synced; everything else LDAP hands us is
        # ignored, so no Group objects are created for irrelevant LDAP groups.
        groups_header = request.META.get("HTTP_REMOTE_GROUPS", "")
        remote_groups = {g.strip() for g in groups_header.split(",") if g.strip()}

        user.groups.clear()

        # webredaktion: can edit pages/images/documents in the Wagtail admin
        if self.WEBREDAKTION_GROUP in remote_groups:
            editors, _ = Group.objects.get_or_create(name="Editors")
            user.groups.add(editors)

        # webadmin: full control, including Django admin (/django-admin/) and
        # Wagtail's own site settings/user management
        is_webadmin = self.WEBADMIN_GROUP in remote_groups
        staff_changed = user.is_staff != is_webadmin or user.is_superuser != is_webadmin
        user.is_staff = is_webadmin
        user.is_superuser = is_webadmin

        # Optionally sync email from Remote-Email
        email = request.META.get("HTTP_REMOTE_EMAIL", "").strip()
        if email and user.email != email:
            user.email = email

        # Optionally sync full name from Remote-Name
        full_name = request.META.get("HTTP_REMOTE_NAME", "").strip()
        if full_name and user.get_full_name() != full_name:
            parts = full_name.split(" ", 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""

        # Save user if anything changed
        if remote_groups or email or full_name or staff_changed:
            user.save()

        return user
