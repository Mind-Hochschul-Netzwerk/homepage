"""
Authelia RemoteUser Backend with LDAP Group Synchronization
"""

from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.models import Group


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

        # Extract groups from HTTP_REMOTE_GROUPS header
        groups_header = request.META.get("HTTP_REMOTE_GROUPS", "")
        groups = [g.strip() for g in groups_header.split(",") if g.strip()]

        # Sync groups
        user.groups.clear()
        for group_name in groups:
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

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
        if groups or email or full_name:
            user.save()

        return user
