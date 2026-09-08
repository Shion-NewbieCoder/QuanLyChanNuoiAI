from rest_framework.permissions import BasePermission

from .roles import ROLE_EMPLOYEE, ROLE_MANAGEMENT, ROLE_TECHNICIAN, get_user_role


READ_ACTIONS = {"list", "retrieve", "get"}
ACTION_NAMES = {
    "list": "read",
    "retrieve": "read",
    "get": "read",
    "create": "create",
    "update": "update",
    "partial_update": "update",
    "destroy": "delete",
}

FULL_ACCESS = {"create", "read", "update", "delete"}
CREATE_READ_UPDATE = {"create", "read", "update"}
CREATE_READ = {"create", "read"}
READ_ONLY = {"read"}

ROLE_ACTIONS = {
    "master_data": {
        ROLE_MANAGEMENT: FULL_ACCESS,
        ROLE_TECHNICIAN: READ_ONLY,
        ROLE_EMPLOYEE: READ_ONLY,
    },
    "care": {
        ROLE_MANAGEMENT: FULL_ACCESS,
        ROLE_TECHNICIAN: CREATE_READ_UPDATE,
        ROLE_EMPLOYEE: CREATE_READ,
    },
    "vaccination": {
        ROLE_MANAGEMENT: FULL_ACCESS,
        ROLE_TECHNICIAN: CREATE_READ_UPDATE,
        ROLE_EMPLOYEE: READ_ONLY,
    },
    "growth_reproduction": {
        ROLE_MANAGEMENT: FULL_ACCESS,
        ROLE_TECHNICIAN: CREATE_READ_UPDATE,
        ROLE_EMPLOYEE: READ_ONLY,
    },
    "sales": {
        ROLE_MANAGEMENT: FULL_ACCESS,
        ROLE_TECHNICIAN: READ_ONLY,
        ROLE_EMPLOYEE: READ_ONLY,
    },
    "statistics": {
        ROLE_MANAGEMENT: READ_ONLY,
        ROLE_TECHNICIAN: READ_ONLY,
        ROLE_EMPLOYEE: set(),
    },
    "ai": {
        ROLE_MANAGEMENT: READ_ONLY,
        ROLE_TECHNICIAN: READ_ONLY,
        ROLE_EMPLOYEE: set(),
    },
}


class RoleActionPermission(BasePermission):
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        action = getattr(view, "permission_action", None) or ACTION_NAMES.get(
            getattr(view, "action", request.method.lower())
        )
        resource = getattr(view, "permission_resource", None)
        role = get_user_role(request.user)
        if action is None or resource not in ROLE_ACTIONS or role is None:
            return False
        return action in ROLE_ACTIONS[resource].get(role, set())
