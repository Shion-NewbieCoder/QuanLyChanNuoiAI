const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS", "TRACE"]);


function getCookie(name) {
  const prefix = `${encodeURIComponent(name)}=`;
  const cookie = document.cookie
    .split(";")
    .map((value) => value.trim())
    .find((value) => value.startsWith(prefix));
  return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : "";
}


export async function apiRequest(path, options = {}) {
  if (typeof path !== "string" || !path.startsWith("/")) {
    throw new TypeError("API paths must be same-origin absolute paths.");
  }

  const method = (options.method ?? "GET").toUpperCase();
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");

  let body = options.body;
  if (body !== undefined && !(body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
    if (typeof body !== "string") {
      body = JSON.stringify(body);
    }
  }

  if (!SAFE_METHODS.has(method)) {
    const csrfToken = getCookie("csrftoken");
    if (csrfToken) {
      headers.set("X-CSRFToken", csrfToken);
    }
  }

  return fetch(path, {
    ...options,
    method,
    headers,
    body,
    credentials: "same-origin",
  });
}
