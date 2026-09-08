ROLE_MANAGEMENT = "quản lý"
ROLE_TECHNICIAN = "kỹ thuật viên"
ROLE_EMPLOYEE = "nhân viên"

ROLE_NAMES = (
    ROLE_MANAGEMENT,
    ROLE_TECHNICIAN,
    ROLE_EMPLOYEE,
)


def get_user_role(user):
    if not user.is_authenticated:
        return None
    user_roles = set(user.groups.filter(name__in=ROLE_NAMES).values_list("name", flat=True))
    for role_name in ROLE_NAMES:
        if role_name in user_roles:
            return role_name
    return None
