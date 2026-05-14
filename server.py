"""
Adapter: a Flask server that proxies the student-facing API
to the Django demand forecasting backend.

The test script (test_api.py) calls this server on port 5050.
Your job is to implement each route so that it correctly forwards
requests to the backend and returns the responses.

Run:
    1. docker compose up
    2. docker compose exec app python test_api.py
    3. Edit this file, then: docker compose restart

Repeat steps 2–3 until all tests pass.
"""

import requests
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# ── Configuration ─────────────────────────────────────────────────────

DJANGO_URL = "https://durczok.ovh/chains"

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
# TIP: You may want to create helper functions to avoid repeating
# the same requests.get / requests.post / requests.delete logic
# in every route. Think about what parameters they need and what
# they should return (hint: look at Flask's Response class).


def _backend_response(response: requests.Response) -> Response:
    return Response(
        response.content,
        status=response.status_code,
        content_type=response.headers.get("Content-Type", "application/json"),
    )


def _proxy_get(path: str, params: dict | None = None) -> Response:
    response = requests.get(f"{DJANGO_URL}{path}", params=params)
    return _backend_response(response)


def _proxy_post(path: str, data: dict | None = None) -> Response:
    response = requests.post(f"{DJANGO_URL}{path}", json=data)
    return _backend_response(response)


def _proxy_delete(path: str) -> Response:
    response = requests.delete(f"{DJANGO_URL}{path}")
    return _backend_response(response)


# ── Setup ─────────────────────────────────────────────────────────────

@app.route("/api/setup/", methods=["POST"])
def setup():
    """
    Reset state and seed reference data in the Django backend.

    This endpoint should:
    1. Delete ALL existing events (fetch pages of events and delete each one)
    2. Ensure all COUNTRIES exist (check if each exists, create if not)
    3. Ensure all CODE_TYPES exist (check if each exists, create if not)

    Backend API reference:
      - GET  /api/events/?page_size=100  → paginated list (check "results" key)
      - DELETE /api/events/<id>/
      - GET  /api/countries/<code>/       → 404 if missing
      - POST /api/countries/              → {"code": ..., "name": ...}
      - GET  /api/code-types/<id>/        → 404 if missing
      - POST /api/code-types/             → {"id": ..., "type": ...}

    Return: jsonify({"status": "ok"}), 200
    """
    while True:
        response = requests.get(f"{DJANGO_URL}/api/events/", params={"page_size": 100})
        if response.status_code != 200:
            return _backend_response(response)

        data = response.json()
        events = data.get("results", data) if isinstance(data, dict) else data
        if not events:
            break

        for event in events:
            delete_response = requests.delete(f"{DJANGO_URL}/api/events/{event['id']}/")
            if delete_response.status_code >= 400:
                return _backend_response(delete_response)

    for code, name in COUNTRIES:
        response = requests.get(f"{DJANGO_URL}/api/countries/{code}/")
        if response.status_code == 404:
            create_response = requests.post(
                f"{DJANGO_URL}/api/countries/",
                json={"code": code, "name": name},
            )
            if create_response.status_code >= 400:
                return _backend_response(create_response)
        elif response.status_code >= 400:
            return _backend_response(response)

    for code_type_id, code_type in CODE_TYPES:
        response = requests.get(f"{DJANGO_URL}/api/code-types/{code_type_id}/")
        if response.status_code == 404:
            create_response = requests.post(
                f"{DJANGO_URL}/api/code-types/",
                json={"id": code_type_id, "type": code_type},
            )
            if create_response.status_code >= 400:
                return _backend_response(create_response)
        elif response.status_code >= 400:
            return _backend_response(response)

    return jsonify({"status": "ok"}), 200


# ── Events ────────────────────────────────────────────────────────────

@app.route("/api/events/", methods=["GET"])
def list_events():
    """
    List events. Forward query parameters (e.g. page_size) to the backend.
    Backend: GET /api/events/
    """
    return _proxy_get("/api/events/", dict(request.args))


@app.route("/api/events/", methods=["POST"])
def create_event():
    """
    Create a new event. Forward the JSON body to the backend.
    Backend: POST /api/events/
    """
    return _proxy_post("/api/events/", request.get_json())


@app.route("/api/events/<int:event_id>/", methods=["GET"])
def get_event(event_id):
    """
    Get a single event by ID.
    Backend: GET /api/events/<event_id>/
    """
    return _proxy_get(f"/api/events/{event_id}/")


@app.route("/api/events/<int:event_id>/", methods=["DELETE"])
def delete_event(event_id):
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
    return _proxy_get("/api/product-families/", dict(request.args))


@app.route("/api/product-families/<int:family_id>/", methods=["GET"])
def get_family(family_id):
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
    # TODO: Implement
    pass


# ── Resolution ───────────────────────────────────────────────────────

@app.route("/api/resolve/", methods=["GET"])
def resolve():
    """
    Resolve a code to its product family. Forward query parameters.
    Backend: GET /api/resolve/
    """
    # TODO: Implement
    pass


@app.route("/api/resolve/reverse/", methods=["GET"])
def resolve_reverse():
    """
    Reverse-resolve a family identifier to its codes. Forward query parameters.
    Backend: GET /api/resolve/reverse/
    """
    # TODO: Implement
    pass


@app.route("/api/resolve/bulk/", methods=["POST"])
def resolve_bulk():
    """
    Bulk-resolve codes. Forward the JSON body to the backend.
    Backend: POST /api/resolve/bulk/
    """
    # TODO: Implement
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
