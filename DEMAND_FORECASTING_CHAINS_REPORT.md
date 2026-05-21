# Demand Forecasting and Product-Code Continuity

Student report based on the pitch presentation and project implementation

Prepared by: Paula Banach, Igor Kolodziej, and Mikita Silivestrau

## Introduction

Demand forecasting depends on a simple idea: future sales are easier to predict when a company can see reliable past sales. In real business systems this idea becomes harder than it sounds, since products are not always tracked under one stable code. A product can receive a new code after a formula change, a new package, a regulatory update, or a market change. When this happens, the new product code may look like a new product even if customers still see it as the same product.

The project solves this problem through a "Chains" system. The system links old and new product codes into product families, so the history of one product is not lost when its code changes. The practical implementation is a Flask adapter that exposes the required REST API and forwards requests to a Django backend at `https://durczok.ovh/chains`. The official test script called the local Flask API, checked setup, event ingestion, validation, recomputation, and family resolution, and the final test result was successful: 75 out of 75 tests passed.

This report develops the pitch presentation in more detail. It explains the business idea, the data science value, the preparation work, and the implementability of the solution. The report does not claim that a forecasting model was trained in this project. Instead, it explains how the Chains system prepares better input data for forecasting models.

## 1. Business Idea

### 1.1 The business problem

Demand forecasting is used to estimate how many units of a product will be needed in the future. It supports many important decisions: how much to produce, how much stock to hold, when to send products to warehouses, and when to plan promotions. For a company that sells many products in many countries, even small forecast errors can create large costs.

Forecasting models usually need historical demand data. If a shampoo sold 10,000 units each month for two years, this history is valuable. It shows seasonality, trend, promotion effects, and possible changes in customer behavior. A model can use this information to estimate future demand. The problem appears when the product code changes.

In the case study, the system works with two code types:

| Code type | Meaning |
| --- | --- |
| `IPC` | Internal Product Code, used inside the company |
| `GTIN` | Global Trade Item Number, commonly used as a retail barcode |

These codes can change for normal business reasons. A product may receive a new code after a reformulation. A bottle size or package design may change. A new law may require different labeling. One regional product may be split into several products, or several regional products may be merged into one standard product.

From the customer point of view, the product may still be similar or even almost the same. From the data system point of view, a new code may look like a new item with no sales history. The old code still has past sales, but that history is no longer directly visible for the new code. The demand history becomes broken.

### 1.2 Why broken history matters

Broken product history creates a practical business risk. A forecast made only from the new code can treat the product as a cold-start case, even if the company has several years of useful history under older codes. This can cause the model to underuse the most relevant data.

The effect can reach many parts of the supply chain.

| Business area | Why product-code continuity matters |
| --- | --- |
| Production planning | A factory needs realistic demand estimates before planning capacity, materials, and shifts. |
| Inventory management | Missing history can lead to too much stock or stockouts, especially after a product relaunch. |
| Distribution | Warehouses and stores need product forecasts by country and product family, not only by current code. |
| Procurement | Suppliers need earlier signals when demand for a continuing product will stay high. |
| Finance and sales planning | Forecasts affect revenue plans, budgets, and commercial targets. |

For a large consumer-goods company such as P&G, the issue is especially relevant. A company like this can manage many brands, countries, package formats, and product variants. Product codes are part of daily operations, but customers do not think in product codes. They think in products and brands. The Chains system helps the technical data structure match the business reality more closely.

### 1.3 The proposed solution: product chains

The solution is to record links between product codes. When one code continues another code, the system stores a chain link. Over time, several links can form one product family.

Example:

| Product code | Active period | Business meaning |
| --- | --- | --- |
| `1001` | 2021-01-01 to 2022-06-30 | Original product code |
| `1002` | 2022-07-01 to 2024-03-31 | Updated version of the same product |
| `1003` | 2024-04-01 to present | Current version |

Without chains, code `1003` would only have its own visible history from 2024-04-01. With chains, code `1003` belongs to the same product family as `1001` and `1002`. A forecasting system can then use the full history of the family, while still knowing which exact code was active at each date.

The main business value is continuity. The product family becomes the stable business object, while individual codes become time-limited generations of that family. This is closer to how people inside a company talk about products. A planner may say, "this product was repackaged," not "this is a totally new product with no past." The system makes that business knowledge available to software.

### 1.4 Value for large consumer-goods businesses

Large consumer-goods businesses often work with many markets. A package change in Poland may not happen at the same time as a package change in Germany. A GTIN may change because of retail needs, while an internal code may change for another reason. A system for product-code continuity must therefore support country, code type, date, and transition type.

The Chains approach gives several benefits:

| Value | Explanation |
| --- | --- |
| Better historical visibility | The new code can be connected to older codes instead of starting from zero. |
| More stable forecasting inputs | Forecasting data can be built around product families, not only current product codes. |
| Clear audit trail | Events show when and why product codes were introduced, discontinued, or linked. |
| Better support for market changes | Splits and merges can be represented as graph relationships. |
| Reusable API | Other systems can resolve codes to families and families to active codes through REST endpoints. |

The solution does not remove the need for business judgment. Some code changes may represent a very different product, while others may represent a small update. The system needs correct chain events from the business or master-data process. Still, once those links are recorded, the company has a much better structure for forecasting and analysis.

## 2. Data Science

### 2.1 Why continuous history is important

Forecasting models depend on the quality of input data. For demand forecasting, one of the most important inputs is a time series: sales over time for a product or product group. A clean time series lets the model learn patterns such as:

- average demand level;
- growth or decline over time;
- seasonal peaks;
- promotion effects;
- country differences;
- sudden drops caused by stockouts or market changes.

When product-code history breaks, the time series also breaks. The old code has history, but the current code has little or none. A model may then act as if there is not enough data. This is called a cold-start problem. Cold starts are common for truly new products, but a changed product code should not always be treated as a truly new product.

Product families reduce this problem. Instead of training or preparing features only for the current code, the company can collect demand across all generations that belong to the same family. The model can still include code-level details when needed, but the family gives a stronger historical base.

### 2.2 Product generations

The case study uses the idea of a generation. A generation is the lifespan of one product code. It has a code, a start date, and an end date. If the code is still active, the end date can be open-ended, represented in the case study as `9999-12-31`.

Example:

| Generation | Code | Start date | End date |
| --- | --- | --- | --- |
| 1 | `1001` | 2021-01-01 | 2022-06-30 |
| 2 | `1002` | 2022-07-01 | 2024-03-31 |
| 3 | `1003` | 2024-04-01 | 9999-12-31 |

This structure is useful for data science because it adds time validity. It is not enough to know that a code belongs to a family. The system must also know when each code was active. A forecast dataset for March 2023 should not use a code that only became active in April 2024. Date logic protects the data from wrong joins and future leakage.

### 2.3 Chain links, splits, and merges

Simple product changes can be represented as a chain:

`1001 -> 1002 -> 1003`

Real product history can be more complex. One product may split into two products. Two products may merge into one. The case study therefore treats product families as graphs, not just as simple lists.

| Pattern | Example | Meaning |
| --- | --- | --- |
| Straight chain | `A -> B -> C` | One product continues through several codes. |
| Split | `A -> B` and `A -> C` | One old product becomes two successor products. |
| Merge | `A -> C` and `B -> C` | Two old products become one successor product. |

These patterns matter for forecasting. In a split, the future demand of each successor may be only part of the old product's demand. In a merge, the new product may inherit demand from more than one predecessor. The Chains system does not decide the forecast formula by itself, but it gives the model-building process the structure needed to make a better decision.

For example, a data scientist may choose to:

- aggregate all family history for a high-level demand forecast;
- use only direct predecessor history for a more narrow forecast;
- add a feature showing that a product is after a split or merge;
- apply business rules to divide historical demand after a split;
- review merged families before training a model.

These are modeling decisions, not API test results. The project provides the product-family structure that makes such decisions possible.

### 2.4 Directed Acyclic Graphs

The case study describes a product family as a Directed Acyclic Graph, or DAG. "Directed" means that links have a direction from predecessor to successor. "Acyclic" means that the graph should not loop back to an older node. A loop would not make business sense, since a product code cannot be both before and after itself in the same history path.

A DAG is a good structure for product-code continuity because it supports straight chains, splits, and merges while keeping time direction clear. It also helps recomputation. After events are ingested, the system can build generations, create generation links, and group connected generations into product families.

In data preparation, the DAG can support several useful operations:

| Operation | Data science use |
| --- | --- |
| Find all predecessors | Collect earlier demand history for a current code. |
| Find all successors | Understand how old demand moved into newer products. |
| Find active codes on a date | Build correct training rows for a chosen date. |
| Detect connected components | Assign one family identifier to all linked generations. |
| Validate date order | Reduce the risk of wrong historical sequences. |

The graph does not replace the forecast model. It improves the dataset that the model receives.

### 2.5 How product families improve model input data

Product families improve forecasting data mainly by reducing artificial breaks. A model trained on current product code only may see this:

| Month | Code | Sales visible to current-code model |
| --- | --- | --- |
| 2023-01 | `1001` | not visible for current code `1003` |
| 2023-02 | `1001` | not visible for current code `1003` |
| 2024-04 | `1003` | visible |
| 2024-05 | `1003` | visible |

A family-based dataset can see this:

| Month | Product family | Active code | Sales visible to family model |
| --- | --- | --- | --- |
| 2023-01 | `PL-IPC-0001` | `1001` | visible |
| 2023-02 | `PL-IPC-0001` | `1001` | visible |
| 2024-04 | `PL-IPC-0001` | `1003` | visible |
| 2024-05 | `PL-IPC-0001` | `1003` | visible |

The model now receives a longer and more stable time series. It can use more observations to estimate level, trend, and seasonality. This may improve forecast accuracy, but the project did not measure model accuracy directly. The final test measured the correctness of the API behavior and product-family resolution.

### 2.6 Possible forecasting models and metrics

The Chains system could support many forecasting methods. A simple model may use moving averages or exponential smoothing on the family time series. A more advanced system may use machine learning models with features such as price, promotion flags, country, season, product family, code generation, and event type. Time-series models, gradient boosting models, or deep learning methods could all use cleaner product-family history.

Suitable evaluation metrics would include:

| Metric | What it measures |
| --- | --- |
| MAE | Mean Absolute Error, the average absolute forecast error. |
| RMSE | Root Mean Squared Error, which gives more weight to larger errors. |
| MAPE | Mean Absolute Percentage Error, useful when percentage error is easy to explain. |
| Forecast bias | Shows whether forecasts are usually too high or too low. |

These metrics should be calculated on real demand data. A fair evaluation would compare forecasts created with code-level history against forecasts created with family-level history. The project does not include such a comparison, so no fake accuracy numbers are reported here.

## 3. Preparation

### 3.1 Understanding the case study

The team first needed to understand the business problem and the required API behavior. The case study explained the domain terms: countries, code types, events, transitions, generations, product families, and family lookups. The pitch presentation then reduced this into a five-minute story, while the implementation files gave the exact technical details.

The main project files were:

| File | Role in the project |
| --- | --- |
| `CASE_STUDY.md` | Main explanation of the business problem, domain concepts, validation rules, and API flow. |
| `server.py` | Flask adapter that exposes the local API and forwards requests to the Django backend. |
| `test_api.py` | Official-style test script used to check setup, events, validation, recomputation, and queries. |
| `test_results/mikita_final_test_output.txt` | Final test evidence showing 75 passed tests and 0 failed tests. |
| `PROJECT_WORK_SPLIT.md` | Team work split and implementation plan. |

The preparation work was important because the project was not only about writing endpoints. The endpoints had to behave exactly as the tests expected. The case study expected valid event creation to return HTTP 201 and invalid events to return HTTP 400. The test script also accepted HTTP 200 for created valid events, but preserving the backend status code was still the safest choice. Changing status codes inside the adapter would have broken the meaning of the API response.

### 3.2 Main project constraints

The project used a fixed set of countries and code types.

| Country code | Country |
| --- | --- |
| `PL` | Poland |
| `DE` | Germany |
| `US` | United States |
| `JP` | Japan |
| `CN` | China |

| Code type | Meaning |
| --- | --- |
| `IPC` | Internal Product Code |
| `GTIN` | Global Trade Item Number |

The event model had three transition types:

| Transition type | Required fields | Effect |
| --- | --- | --- |
| `INTRO` | `introduction_code`, `date` | Creates a new active generation. |
| `DISCONT` | `discontinuation_code`, `date` | Ends an active generation. |
| `chain` | `introduction_code`, `discontinuation_code`, `date` | Links predecessor and successor codes. |

The tests also included valid and invalid cases. The valid scenarios included straight chains, longer chains, splits, and merges. The invalid cases checked that the API rejects wrong state transitions, missing fields, wrong references, and bad chain logic.

### 3.3 API phases

The official test script used three main phases.

| Phase | What happens | Expected result |
| --- | --- | --- |
| Setup | `POST /api/setup/` resets state and seeds reference data. | HTTP 200 |
| Event ingestion | The test creates 100 families and sends invalid events. | Valid events accepted, invalid events rejected with HTTP 400 |
| Recompute and query | The test recomputes product families, then calls resolve and reverse resolve. | Families resolve correctly |

This flow matches the business process. First the system must know valid reference data. Then it receives product lifecycle events. After events are stored, the product-family graph is recomputed. Finally, other systems can ask which family a code belongs to, or which codes are active in a family on a date.

### 3.4 Validation rules reviewed before implementation

The validation rules were a central part of the preparation. The team needed to know which data should be accepted and which data should be rejected.

| Validation area | Example invalid case |
| --- | --- |
| Product state | Double introduction of an already active code. |
| Product state | Discontinuation of a code that is not active. |
| Time logic | Overlapping generations for the same code. |
| Chain logic | Chain uses a code that does not exist. |
| Chain logic | Chain uses the same code as predecessor and successor. |
| Required fields | Missing `introduction_code`, `discontinuation_code`, or `date`. |
| References | Invalid country code or invalid code type. |

The final test output shows that all 13 invalid-event scenarios returned the expected HTTP 400 response. This means the API behavior matched the validation requirements used by the test script.

### 3.5 Work split

The project work split gave each team member a clear area. Igor focused on requirements, architecture, setup, and the API foundation. Paula focused on event ingestion and validation behavior. Mikita focused on product-family recomputation, resolution endpoints, full testing, and deck assembly.

This split also matched the story of the pitch:

| Presentation area | Main owner in the work split |
| --- | --- |
| Business problem and solution | Igor |
| API architecture | Igor |
| Event model and validation | Paula |
| Product-family computation | Mikita |
| Resolution endpoints and final test results | Mikita |

The split was useful because the system had several separate concerns. Setup and forwarding needed reliable adapter logic. Event ingestion needed strict validation behavior. Recompute and resolve needed correct product-family behavior. The final result required all parts to work together.

## 4. Implementability

### 4.1 Technical architecture

The implemented solution uses a local Flask adapter in `server.py`. The official test script sends HTTP requests to the local server at `http://localhost:5050`. The Flask adapter forwards those requests to the Django backend at `https://durczok.ovh/chains`.

The architecture can be described as:

| Layer | Role |
| --- | --- |
| `test_api.py` | Sends setup, event, recompute, resolve, and reverse-resolve requests. |
| Flask adapter | Exposes the required local REST API on port 5050. |
| Django backend | Stores events, validates data, recomputes families, and returns results. |
| Test output | Confirms that the local API behaves as expected. |

This design is technically feasible because the Flask adapter is small and focused. It does not duplicate all backend logic. Instead, it makes the local interface expected by the test script compatible with the existing Django backend.

### 4.2 Adapter configuration

The adapter stores the backend URL and timeout in configuration variables. It also defines the required reference data for setup.

```python
DJANGO_URL = os.getenv("DJANGO_URL", "https://durczok.ovh/chains").rstrip("/")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))

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
```

This matters because setup must create or confirm the same countries and code types that the case study requires. The environment variable `DJANGO_URL` also makes the adapter easier to move to another backend if needed.

### 4.3 Preserving backend status codes

The adapter keeps the response body, status code, and content type returned by the backend.

```python
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
```

This is one of the most important implementation details. The tests check status codes directly. If the adapter changed all successful responses to HTTP 200, a valid event that should return HTTP 201 could fail the test. If it hid a backend validation error, invalid events could look accepted. Passing the original status code keeps the adapter honest.

The adapter also returns a clear local error if the backend cannot be reached.

```python
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
```

This does not solve backend downtime, but it makes the failure easier to understand. A 502 response shows that the problem is between the adapter and backend, not necessarily a validation error in the event data.

### 4.4 Request forwarding

The adapter has shared proxy helpers for GET, POST, and DELETE requests. These helpers forward query parameters or JSON bodies to the backend and then return the backend response.

```python
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
```

These helper functions make endpoint code shorter and reduce repeated logic. Query endpoints such as resolve need the query string, while event creation and recomputation use JSON bodies.

```python
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
```

The timeout prevents the adapter from waiting forever if the backend is slow or unavailable. The `try` and `except` block turns connection problems into a structured HTTP 502 response.

### 4.5 Setup endpoint

The setup endpoint prepares the backend state for testing. It deletes existing events, ensures that countries exist, ensures that code types exist, and returns HTTP 200 when complete.

```python
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
```

The reset is important for repeatable tests. If old events remain in the backend, the test may be affected by data from an earlier run. Setup makes the test start from a known state.

The setup endpoint checks whether each country already exists. If a country is missing, it creates it.

```python
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
```

The same pattern is used for code types. The adapter does not blindly recreate reference data. It checks first, then creates only when needed.

### 4.6 Event ingestion

Events are business occurrences in one country. Each event contains one or more transitions. In the implementation, event creation is handled by forwarding the JSON body to the backend.

```python
@app.route("/api/events/", methods=["POST"])
def create_event():
    """
    Create a new event. Forward the JSON body to the backend.
    Backend: POST /api/events/
    """
    return _proxy_post("/api/events/", _json_body())
```

This endpoint is simple, but it is important. The backend receives all event details and applies validation rules. The adapter then passes the result back to the test script. Valid events can be accepted, and invalid events can be rejected with the correct status code.

The test script created several valid family scenarios:

| Scenario | Shape |
| --- | --- |
| Chain of three codes | `A -> B -> C` |
| Chain of four codes | `A -> B -> C -> D` |
| Split | `A -> B` and `A -> C` |
| Merge | `A -> C` and `B -> C` |

The test script also sent 13 invalid cases. These checked double introduction, overlapping generation, double discontinuation, chain with missing or non-existing codes, chain with the same code on both sides, invalid country, invalid code type, and missing date. The final result shows that each invalid case returned HTTP 400.

### 4.7 Product-family recomputation

After events are ingested, the system needs to rebuild product families. In the pitch, this was shown as a pipeline:

`Events -> Generations -> Generation links -> Product families -> Resolve / Reverse resolve`

The Flask endpoint forwards the recompute request to the backend.

```python
@app.route("/api/product-families/recompute/", methods=["POST"])
def recompute():
    """
    Trigger family recomputation. Forward the JSON body to the backend.
    Backend: POST /api/product-families/recompute/
    """
    return _proxy_post("/api/product-families/recompute/", _json_body())
```

Conceptually, recomputation groups transitions by country and code type, sorts events by time, builds generations, links predecessors to successors, and creates one product family for each connected group of generations. The implementation details of this computation are handled by the Django backend, while the Flask adapter exposes the required local endpoint.

### 4.8 Resolve, reverse resolve, and bulk resolve

After recomputation, other systems can query product families.

| Endpoint | Purpose |
| --- | --- |
| `GET /api/resolve/` | Finds the product family for a code, country, code type, and date. |
| `GET /api/resolve/reverse/` | Finds active codes in a product family on a date. |
| `POST /api/resolve/bulk/` | Resolves many queries in one request. |

The implementation forwards each route to the backend.

```python
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
```

These endpoints are the final business-facing value of the system. A forecasting pipeline can use resolve to find the stable product family for a code. It can use reverse resolve to find which exact codes were active in a family on a certain date. Bulk resolve is useful when many codes must be processed at once.

### 4.9 Final testing

The final test run passed every check.

| Test area | Result |
| --- | --- |
| Setup | `POST /api/setup/` returned HTTP 200. |
| Family creation | 100 test families were created. |
| Invalid events | 13 invalid scenarios returned expected HTTP 400. |
| Recompute | Product-family recomputation returned HTTP 200. |
| Resolve | Sampled codes resolved to product-family identifiers. |
| Reverse resolve | Sampled product families returned active codes successfully. |
| Final score | 75 passed, 0 failed, 100%. |

The final output was:

```text
=== RESULTS ===
  Passed: 75
  Failed: 0
  Score:  75/75 (100%)
```

This result proves that the implemented API matched the test expectations. It does not prove that a demand forecast is more accurate, since no forecasting model was trained or evaluated. It proves that the product-code continuity API works according to the assignment tests.

### 4.10 Risks and limitations

The solution is feasible, but it has some risks and limits.

| Risk or limitation | Explanation |
| --- | --- |
| Backend availability | The Flask adapter depends on the Django backend. If the backend is down, the adapter cannot complete normal operations. |
| Data quality | Product-family quality depends on correct event data. Wrong chain events can create wrong families. |
| Event order | Dates and state changes must be valid. Poor event order can create invalid or confusing histories. |
| Validation complexity | Splits, merges, reintroductions, and overlapping periods require careful validation. |
| Forecasting impact not measured | The project tested API behavior, not forecast accuracy on real sales data. |
| Shared backend state | Setup deletes existing events, so this approach is suited to a test environment, not a shared production environment without stronger controls. |

Future improvements could include stronger audit logging, user-friendly validation messages, role-based access control, and a separate evaluation using real sales data. A later data science phase could compare forecasts with and without product-family continuity using MAE, RMSE, MAPE, and forecast bias.

## Conclusion

The project addressed a practical problem in demand forecasting: product-code changes can break visible sales history. This matters because production planning, inventory management, distribution, procurement, and business planning all depend on reliable forecasts. The Chains idea solves the problem by linking old and new product codes into product families, so a product can keep its historical context across reformulation, repackaging, regulation changes, and market restructuring.

From a data science point of view, the system prepares better forecasting input. It turns separate code histories into family-level histories, supports generations with valid time periods, and represents splits and merges through a Directed Acyclic Graph. This can reduce cold-start problems and help forecasting models use more complete demand history. The project did not invent model results, but it created the data structure that would make a stronger forecasting evaluation possible.

From an implementation point of view, the solution was technically feasible. The Flask adapter exposed the required local REST API, forwarded requests to the Django backend, preserved backend status codes, handled setup, passed event requests, triggered recomputation, and supported resolve, reverse-resolve, and bulk-resolve endpoints. The final test result was 75 passed tests, 0 failed tests, and a 100% score.

The main achievement is that the presentation idea was turned into a working API workflow. Product-code changes no longer have to mean lost demand history. With product families, companies can connect operational product data to forecasting needs in a cleaner and more useful way.
