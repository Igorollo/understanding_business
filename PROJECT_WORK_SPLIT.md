# Project Work Split

## A. Short Summary Of The Project

The project is to complete the Demand Forecasting "Chains" REST API assignment from the PDF and repository. The system preserves demand-history continuity when product codes change by linking old and new codes into product families.

In the provided repo, the practical implementation target is `server.py`: a Flask adapter that exposes the required API and forwards requests to the Django backend at `durczok.ovh/chains`.

The final output must include working code, passing API tests, and a presentation prepared by the team. Only Igor and Mikita will present, but slide creation can still be split across all three people.

## B. Proposed Solution Approach

1. Understand the actual assignment from the PDF, `CASE_STUDY.md`, `server.py`, `test_api.py`, and the live site.
2. Implement the Flask adapter in three blocks: foundation/setup, event ingestion/validation, family resolution/final verification.
3. Preserve backend response status codes exactly, especially `201` for valid events and `400` for invalid cases.
4. Run the official test script until all phases pass.
5. Prepare a concise presentation explaining the business problem, API design, validation logic, recomputation, resolution, and test results.

## C. Fair Work Split Table

| Person | Main responsibility                                                    | Specific tasks                                                                                                                                                                                                                                                                                  | Deliverables                                                                                                                                | Handover to next person                                                                                               | Presentation contribution                               |
| ------ | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Igor   | Part 1: requirements, architecture, setup, and API foundation          | Read the PDF and repo docs; inspect `test_api.py`; map all required endpoints; inspect live site/API; set `DJANGO_URL`; implement shared proxy helpers; implement `/api/setup/`; seed countries and code types; implement read-only proxy routes for event/family listing and detail            | Requirements summary; endpoint checklist; working proxy helpers; working setup/reset; seeded reference data; initial smoke test evidence    | Paula receives a working adapter foundation, backend URL, setup endpoint, endpoint checklist, and helper functions    | Creates slides 1-3; presents slides 1-3                 |
| Paula  | Part 2: event ingestion and validation                                 | Implement `POST /api/events/`; implement `DELETE /api/events/{id}/`; verify `GET /api/events/` and `GET /api/events/{id}/` behavior from Igor's routes; test valid event creation; test the 13 invalid cases from the PDF; document expected versus actual status codes; fix event-route issues | Working event lifecycle; valid event returns `201`; invalid cases return `400`; validation evidence table; event-ingestion test notes       | Mikita receives setup plus event ingestion working, with validation cases confirmed and any backend quirks documented | Creates slides 4-5 and slide 9; does not present        |
| Mikita | Part 3: product families, resolution, final testing, and deck assembly | Implement `POST /api/product-families/recompute/`; implement `GET /api/resolve/`; implement `GET /api/resolve/reverse/`; implement `POST /api/resolve/bulk/`; run full `test_api.py`; fix final integration issues; collect final test output; assemble final slide deck from all slides        | Working recompute endpoint; working resolve/reverse/bulk endpoints; full passing test result; final slide deck assembled; final demo script | Final handover is the completed project: code, test result, and presentation deck                                     | Creates slides 6-8; assembles deck; presents slides 4-8 |

## D. Fairness Check

| Person | Why the workload is fair                                                                                           |
| ------ | ------------------------------------------------------------------------------------------------------------------ |
| Igor   | Owns the most analysis-heavy part plus setup, proxy foundation, and opening presentation section                   |
| Paula  | Owns the highest validation burden: event lifecycle plus all invalid scenarios, and creates validation/risk slides |
| Mikita | Owns the final API behavior, full integration test, deck assembly, and the larger technical presentation section   |

No task is assigned to "everyone" or "all together." Every activity has one named owner.

## E. Slide Plan And Required Content

| Slide                   | Owner  | Presenter | Must include                                                                                                            |
| ----------------------- | ------ | --------- | ----------------------------------------------------------------------------------------------------------------------- |
| 1. Project Goal         | Igor   | Igor      | Title, team names, one-sentence goal: preserve demand history when product codes change                                 |
| 2. Business Problem     | Igor   | Igor      | Why demand forecasting needs historical data; why product-code changes break continuity; example `1001 -> 1002 -> 1003` |
| 3. API Architecture     | Igor   | Igor      | Flask adapter, Django backend, `/chains/api/...` backend path, test script calling local API on port `5050`             |
| 4. Event Model          | Paula  | Mikita    | `INTRO`, `DISCONT`, `chain`; required fields; example event payload                                                     |
| 5. Validation Rules     | Paula  | Mikita    | The 13 invalid cases; expected `400`; explanation that status codes must be preserved from backend                      |
| 6. Product Families     | Mikita | Mikita    | Generations, chains, DAG, split and merge examples, family identifier such as `PL-IPC-0001`                             |
| 7. Resolution Endpoints | Mikita | Mikita    | `GET /api/resolve/`, `GET /api/resolve/reverse/`, `POST /api/resolve/bulk/`; what each endpoint returns                 |
| 8. Test Results         | Mikita | Mikita    | `test_api.py` phases: setup, event ingestion, recompute, family queries; final pass result                              |
| 9. Risks And Safeguards | Paula  | Igor      | Wrong backend URL, dropped query params, lost status codes, incomplete setup reset, shared backend reset risk           |

## F. Risk Points And How To Avoid Them

| Risk                                        | Owner  | Avoidance action                                                                     |
| ------------------------------------------- | ------ | ------------------------------------------------------------------------------------ |
| Wrong project scope                         | Igor   | Base implementation on `server.py`, `test_api.py`, and `notebooks/server_example.py` |
| Wrong backend URL                           | Igor   | Use `/chains` as backend base so API paths become `/chains/api/...`                  |
| Setup does not reset data                   | Igor   | Delete events page by page until no events remain                                    |
| Event status codes are changed accidentally | Paula  | Return backend status codes directly                                                 |
| Invalid events accidentally accepted        | Paula  | Check all 13 invalid cases against expected `400`                                    |
| Query params or JSON body not forwarded     | Mikita | Use `dict(request.args)` for GET and `request.get_json()` for POST                   |
| Recompute or resolution endpoints fail late | Mikita | Run full `test_api.py` after implementing final endpoints                            |
| Presentation misses Paula's work            | Paula  | Put validation evidence and risks into slides 4-5 and 9                              |

## G. Final Checklist

| Item                                 | Owner  |
| ------------------------------------ | ------ |
| PDF and repo reviewed                | Igor   |
| Live site/API reviewed               | Igor   |
| Endpoint checklist completed         | Igor   |
| Proxy helpers implemented            | Igor   |
| Setup/reset implemented              | Igor   |
| Reference data seeding implemented   | Igor   |
| Event create/delete implemented      | Paula  |
| Event validation checked             | Paula  |
| 13 invalid cases documented          | Paula  |
| Product-family endpoints implemented | Mikita |
| Recompute endpoint implemented       | Mikita |
| Resolve endpoints implemented        | Mikita |
| Full test run completed              | Mikita |
| Slides 1-3 completed                 | Igor   |
| Slides 4-5 and 9 completed           | Paula  |
| Slides 6-8 completed                 | Mikita |
| Final deck assembled                 | Mikita |
| Igor's speaking part rehearsed       | Igor   |
| Mikita's speaking part rehearsed     | Mikita |

## H. Igor Local Smoke-Test Evidence

Local Docker smoke was run through the Flask adapter on `localhost:5050` using only non-mutating `GET` requests. `POST /api/setup/` and `test_api.py` were intentionally not run because they reset shared live backend data.

| Check                                    | Result                              |
| ---------------------------------------- | ----------------------------------- |
| `GET /api/events/?page_size=1`           | `200 application/json`, 49495 bytes |
| `GET /api/events/1089/`                  | `200 application/json`, 326 bytes   |
| `GET /api/product-families/?page_size=1` | `200 application/json`, 10517 bytes |
| `GET /api/product-families/511/`         | `200 application/json`, 616 bytes   |