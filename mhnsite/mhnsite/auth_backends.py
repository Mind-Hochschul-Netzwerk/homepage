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
        self._copy_header(request)
        if self._resync_current_user(request):
            return
        return super().process_request(request)

    async def aprocess_request(self, request):
        self._copy_header(request)
        if self._resync_current_user(request):
            return
        return await super().aprocess_request(request)

    def _copy_header(self, request):
        if (
            "HTTP_REMOTE_USER" in request.META
            and "REMOTE_USER" not in request.META
        ):
            request.META["REMOTE_USER"] = request.META["HTTP_REMOTE_USER"]

    def _resync_current_user(self, request):
        """
        Django's RemoteUserMiddleware only calls authenticate() (and thus our
        group/permission sync) once, the first time a session is logged in -
        if the header's username still matches request.user on later
        requests, it returns early and never re-authenticates. That means
        LDAP group changes (e.g. someone being granted or losing webadmin)
        would never take effect until the browser session is cleared. Here
        we re-sync permissions on every request for an already-logged-in
        user, without calling auth.login() again, so we don't rotate the
        CSRF token underneath an in-progress visit.
        """
        username = request.META.get(self.header)
        if not username or not request.user.is_authenticated:
            return False
        if request.user.get_username() != self.clean_username(username, request):
            return False
        AutheliaRemoteUserBackend().sync_permissions(request.user, request)
        return True


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
    # re-derived from LDAP on every request, so changing someone's LDAP
    # groups takes effect immediately without manual cleanup here.
    WEBREDAKTION_GROUP = "webredaktion"
    WEBADMIN_GROUP = "webadmin"

    def authenticate(self, request, remote_user=None):
        from logging import getLogger

        logger = getLogger("wagtail")
        logger.info(f"Authenticating user: {remote_user}")
        logger.debug(f"Request META: {request.META}")
        user = super().authenticate(request, remote_user)
        if not user or not request:
            return user
        self.sync_permissions(user, request)
        return user

    def sync_permissions(self, user, request):
        """
        Sync Wagtail/Django group membership and email/full name from the
        Authelia forward-auth headers on the given request.
        """
        # Extract groups from HTTP_REMOTE_GROUPS header. Only the groups
        # relevant to this app are synced; everything else LDAP hands us is
        # ignored, so no Group objects are created for irrelevant LDAP groups.
        # This runs on every request (see AutheliaRemoteUserMiddleware), so it
        # only touches the database when something actually changed.
        groups_header = request.META.get("HTTP_REMOTE_GROUPS", "")
        remote_groups = {g.strip() for g in groups_header.split(",") if g.strip()}
        changed = False

        # webredaktion: can edit pages/images/documents in the Wagtail admin
        target_group_names = set()
        if self.WEBREDAKTION_GROUP in remote_groups:
            target_group_names.add("Editors")

        current_group_names = set(user.groups.values_list("name", flat=True))
        if current_group_names != target_group_names:
            user.groups.clear()
            for name in target_group_names:
                group, _ = Group.objects.get_or_create(name=name)
                user.groups.add(group)

        # webadmin: full control, including Django admin (/django-admin/) and
        # Wagtail's own site settings/user management
        is_webadmin = self.WEBADMIN_GROUP in remote_groups
        if user.is_staff != is_webadmin or user.is_superuser != is_webadmin:
            user.is_staff = is_webadmin
            user.is_superuser = is_webadmin
            changed = True

        # Optionally sync email from Remote-Email
        email = request.META.get("HTTP_REMOTE_EMAIL", "").strip()
        if email and user.email != email:
            user.email = email
            changed = True

        # Optionally sync full name from Remote-Name
        full_name = request.META.get("HTTP_REMOTE_NAME", "").strip()
        if full_name and user.get_full_name() != full_name:
            parts = full_name.split(" ", 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""
            changed = True

        if changed:
            user.save()
