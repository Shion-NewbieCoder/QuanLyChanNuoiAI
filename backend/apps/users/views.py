from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse


@login_required
@permission_required("auth.view_user", raise_exception=True)
def protected_operation(request):
    return HttpResponse("Protected operation available.")
