"""Safe HTML errors for browser routes, including local DEBUG demonstrations."""
from django.shortcuts import render


class BrowserErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.path.startswith(("/api/", "/static/")) and response.status_code in (403, 404, 500):
            # Deliberately minimal context: error rendering must not query the database.
            safe_response = render(None, "management/error.html", {"error_status": response.status_code}, status=response.status_code)
            # Preserve cookies and security headers already applied by middleware.
            response.content = safe_response.content
            response["Content-Type"] = safe_response["Content-Type"]
            if "Content-Length" in response:
                response["Content-Length"] = str(len(response.content))
        return response
