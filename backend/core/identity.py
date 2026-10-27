"""Who is making the request, and which agencies they may see.

Today identity comes from a stand-in: the caller names a demo user in the `X-Demo-User` header. Once agency sign-in
exists (Azure AD B2C), `StandInAuthentication` is replaced by one that validates a bearer token and reads allowed
agencies from the portal database. Report code only ever sees `request.user` as a `PortalUser`, so swapping this out
doesn't touch any report.

Internal network only: never deploy the stand-in where agencies can reach it.
"""

import logging
from dataclasses import dataclass

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

log = logging.getLogger(__name__)

DEMO_USER_HEADER = "X-Demo-User"


@dataclass(frozen=True)
class PortalUser:
    user_id: str
    display_name: str
    # Internal staff (support, product) can see several agencies; agency users see exactly one.
    internal: bool
    allowed_agencies: tuple[str, ...]

    is_authenticated = True


DEMO_USERS: tuple[PortalUser, ...] = (
    PortalUser("indiana.analyst", "Indiana analyst", internal=False, allowed_agencies=("IN-DOT",)),
    PortalUser("iowa.analyst", "Iowa analyst", internal=False, allowed_agencies=("IA-DOT",)),
    PortalUser("ohio.analyst", "Ohio analyst", internal=False, allowed_agencies=("OH-DOT",)),
    PortalUser(
        "support.staff",
        "Customer support (internal)",
        internal=True,
        allowed_agencies=("IN-DOT", "IA-DOT", "OH-DOT"),
    ),
)


class StandInAuthentication(BaseAuthentication):
    users: tuple[PortalUser, ...] = DEMO_USERS

    def authenticate(self, request: Request) -> tuple[PortalUser, None] | None:
        user_id = request.headers.get(DEMO_USER_HEADER)
        user = next((u for u in self.users if u.user_id == user_id), None)
        return (user, None) if user else None

    def authenticate_header(self, request: Request) -> str:
        # Makes DRF answer 401 (not 403) when there's no identity.
        return DEMO_USER_HEADER


class IsIdentified(BasePermission):
    message = "Unknown or missing user"

    def has_permission(self, request: Request, view: object) -> bool:
        return isinstance(request.user, PortalUser)


def assert_agency_access(request: Request, agency: str) -> None:
    """Agency isolation: call this before running any query for `agency`.

    Raises 403 when the user may not see it, so no query runs and nothing about the agency's data leaks, not even
    whether it exists.
    """
    user: PortalUser = request.user
    if agency not in user.allowed_agencies:
        log.warning("agency access denied", extra={"user": user.user_id, "agency": agency})
        raise PermissionDenied("You do not have access to this agency")
