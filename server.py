"""
Adapter: a Flask server that proxies the student-facing API
to the Django demand forecasting backend.

The test script (test_api.py) calls this server on port 5050.
Each route forwards requests to the backend and returns the backend
response with the original status code.

Run:
    1. docker compose up
    2. docker compose exec app python test_api.py
    3. Edit this file, then: docker compose restart
"""

import os
from typing import Any

import requests
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# ── Configuration ─────────────────────────────────────────────────────

DJANGO_URL = os.getenv("DJANGO_URL", "https://durczok.ovh/chains").rstrip("/")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))

# Reference data that must be seeded during setup
COUNTRIES = [
    ("PL", "Poland"),
    ("DE", "Germany"),
    ("US", "United States"),
    ("JP", "Japan"),
    ("CN", "China"),
]

CODE_TYPES = [
    ("IPC", "Internal Product Code"),
    ("GTIN", "Global Trade Item Number"),
]


# ── Helpers ───────────────────────────────────────────────────────────

def _backend_response(response: requests.Response) -> Response:
    """
    Preserve backend response body, status code, and content type.

    This is important because the official test expects:
    - valid event creation -> 201
    - invalid event creation -> 400
    """
    return Response(
        response.content,
        status=response.status_code,
        content_type=response.headers.get("Content-Type", "application/json"),
    )


def _backend_error_response(method: str, path: str, exc: Exception) -> tuple[Response, int]:
    """
    Return a clear local error if the remote Django backend cannot be reached.
    """
    return jsonify(
        {
            "status": "backend_error",
            "method": method,
            "url": f"{DJANGO_URL}{path}",
            "detail": str(exc),
        }
    ), 502


def _query_params() -> dict[str, Any]:
    """
    Forward query parameters from Flask to Django.
    The official test uses single-value query parameters.
    """
    return request.args.to_dict(flat=True)


def _json_body() -> dict[str, Any]:
    """
    Forward JSON body. If no JSON is provided, send an empty object.
    """
    return request.get_json(silent=True) or {}


def _proxy_get(path: str, params: dict[str, Any] | None = None) -> Response:
    try:
        response = requests.get(
            f"{DJANGO_URL}{path}",
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        return _backend_error_response("GET", path, exc)

    return _backend_response(response)


def _proxy_post(path: str, data: dict[str, Any] | None = None) -> Response:
    try:
        response = requests.post(
            f"{DJANGO_URL}{path}",
            json=data if data is not None else {},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        return _backend_error_response("POST", path, exc)

    return _backend_response(response)


def _proxy_delete(path: str) -> Response:
    try:
        response = requests.delete(
            f"{DJANGO_URL}{path}",
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        return _backend_error_response("DELETE", path, exc)

    return _backend_response(response)


# ── Local health check ─────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "status": "ok",
            "service": "chains-flask-adapter",
            "backend": DJANGO_URL,
        }
    ), 200


# ── Setup ─────────────────────────────────────────────────────────────

@app.route("/api/setup/", methods=["POST"])
def setup():
    """
    Reset state and seed reference data in the Django backend.

    This endpoint:
    1. Deletes all existing events.
    2. Ensures all required countries exist.
    3. Ensures all required code types exist.
    4. Returns 200 when setup is complete.
    """

    # 1. Delete all existing events.
    while True:
        try:
            response = requests.get(
                f"{DJANGO_URL}/api/events/",
                params={"page_size": 100},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            return _backend_error_response("GET", "/api/events/", exc)

        if response.status_code != 200:
            return _backend_response(response)

        data = response.json()
        events = data.get("results", data) if isinstance(data, dict) else data

        if not events:
            break

        for event in events:
            event_id = event["id"]

            try:
                delete_response = requests.delete(
                    f"{DJANGO_URL}/api/events/{event_id}/",
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
            except requests.RequestException as exc:
                return _backend_error_response("DELETE", f"/api/events/{event_id}/", exc)

            if delete_response.status_code >= 400:
                return _backend_response(delete_response)

    # 2. Ensure countries exist.
    for code, name in COUNTRIES:
        try:
            response = requests.get(
                f"{DJANGO_URL}/api/countries/{code}/",
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            return _backend_error_response("GET", f"/api/countries/{code}/", exc)

        if response.status_code == 404:
            try:
                create_response = requests.post(
                    f"{DJANGO_URL}/api/countries/",
                    json={"code": code, "name": name},
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
            except requests.RequestException as exc:
                return _backend_error_response("POST", "/api/countries/", exc)

            if create_response.status_code >= 400:
                return _backend_response(create_response)

        elif response.status_code >= 400:
            return _backend_response(response)

    # 3. Ensure code types exist.
    for code_type_id, code_type in CODE_TYPES:
        try:
            response = requests.get(
                f"{DJANGO_URL}/api/code-types/{code_type_id}/",
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            return _backend_error_response("GET", f"/api/code-types/{code_type_id}/", exc)

        if response.status_code == 404:
            try:
                create_response = requests.post(
                    f"{DJANGO_URL}/api/code-types/",
                    json={"id": code_type_id, "type": code_type},
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
            except requests.RequestException as exc:
                return _backend_error_response("POST", "/api/code-types/", exc)

            if create_response.status_code >= 400:
                return _backend_response(create_response)

        elif response.status_code >= 400:
            return _backend_response(response)

    return jsonify({"status": "ok"}), 200


# ── Events ────────────────────────────────────────────────────────────

@app.route("/api/events/", methods=["GET"])
def list_events():
    """
    List events. Forward query parameters to the backend.
    Backend: GET /api/events/
    """
    return _proxy_get("/api/events/", _query_params())


@app.route("/api/events/", methods=["POST"])
def create_event():
    """
    Create a new event. Forward the JSON body to the backend.
    Backend: POST /api/events/
    """
    return _proxy_post("/api/events/", _json_body())


@app.route("/api/events/<int:event_id>/", methods=["GET"])
def get_event(event_id: int):
    """
    Get a single event by ID.
    Backend: GET /api/events/<event_id>/
    """
    return _proxy_get(f"/api/events/{event_id}/")


@app.route("/api/events/<int:event_id>/", methods=["DELETE"])
def delete_event(event_id: int):
    """
    Delete a single event by ID.
    Backend: DELETE /api/events/<event_id>/
    """
    return _proxy_delete(f"/api/events/{event_id}/")


# ── Product Families ─────────────────────────────────────────────────

@app.route("/api/product-families/", methods=["GET"])
def list_families():
    """
    List product families. Forward query parameters to the backend.
    Backend: GET /api/product-families/
    """
    return _proxy_get("/api/product-families/", _query_params())


@app.route("/api/product-families/<int:family_id>/", methods=["GET"])
def get_family(family_id: int):
    """
    Get a single product family by ID.
    Backend: GET /api/product-families/<family_id>/
    """
    return _proxy_get(f"/api/product-families/{family_id}/")


@app.route("/api/product-families/recompute/", methods=["POST"])
def recompute():
    """
    Trigger family recomputation. Forward the JSON body to the backend.
    Backend: POST /api/product-families/recompute/
    """
    return _proxy_post("/api/product-families/recompute/", _json_body())


# ── Resolution ───────────────────────────────────────────────────────

@app.route("/api/resolve/", methods=["GET"])
def resolve():
    """
    Resolve a code to its product family. Forward query parameters.
    Backend: GET /api/resolve/
    """
    return _proxy_get("/api/resolve/", _query_params())


@app.route("/api/resolve/reverse/", methods=["GET"])
def resolve_reverse():
    """
    Reverse-resolve a family identifier to its codes. Forward query parameters.
    Backend: GET /api/resolve/reverse/
    """
    return _proxy_get("/api/resolve/reverse/", _query_params())


@app.route("/api/resolve/bulk/", methods=["POST"])
def resolve_bulk():
    """
    Bulk-resolve codes. Forward the JSON body to the backend.
    Backend: POST /api/resolve/bulk/
    """
    return _proxy_post("/api/resolve/bulk/", _json_body())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
