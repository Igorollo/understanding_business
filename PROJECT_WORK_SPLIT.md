# Project Work Split

## A. Short Summary Of The Project

The project is to complete the Demand Forecasting "Chains" REST API assignment from the PDF and repository. The system preserves demand-history continuity when product codes change by linking old and new codes into product families.

In the provided repo, the practical implementation target is `server.py`: a Flask adapter that exposes the required API and forwards requests to the Django backend at `durczok.ovh/chains`.

The final output must include working code, passing API tests, and a presentation prepared by the team. Igor and Mikita will present (~2:30 each in a strict 5-minute slot). Paula creates slides covering her work area but does not present.

## B. Proposed Solution Approach

1. Understand the actual assignment from the PDF, `CASE_STUDY.md`, `server.py`, `test_api.py`, and the live site.
2. Implement the Flask adapter in three blocks: foundation/setup, event ingestion/validation, family resolution/final verification.
3. Preserve backend response status codes exactly, especially `201` for valid events and `400` for invalid cases.
4. Run the official test script until all phases pass.
5. Prepare a concise presentation explaining the business problem, API design, validation logic, recomputation, resolution, and test results.

## C. Fair Work Split Table

| Person | Main responsibility                                                    | Specific tasks                                                                                                                                                                                                                                                                                  | Deliverables                                                                                                                                | Handover to next person                                                                                               | Presentation contribution                               |
| ------ | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Igor   | Part 1: requirements, architecture, setup, and API foundation          | Read the PDF and repo docs; inspect `test_api.py`; map all required endpoints; inspect live site/API; set `DJANGO_URL`; implement shared proxy helpers; implement `/api/setup/`; seed countries and code types; implement read-only proxy routes for event/family listing and detail            | Requirements summary; endpoint checklist; working proxy helpers; working setup/reset; seeded reference data; initial smoke test evidence    | Paula receives a working adapter foundation, backend URL, setup endpoint, endpoint checklist, and helper functions    | Creates slides 1-3; presents slides 1-3 (~2:30)         |
| Paula  | Part 2: event ingestion and validation                                 | Implement `POST /api/events/`; implement `DELETE /api/events/{id}/`; verify `GET /api/events/` and `GET /api/events/{id}/` behavior from Igor's routes; test valid event creation; test the 13 invalid cases from the PDF; document expected versus actual status codes; fix event-route issues | Working event lifecycle; valid event returns `201`; invalid cases return `400`; validation evidence table; event-ingestion test notes       | Mikita receives setup plus event ingestion working, with validation cases confirmed and any backend quirks documented | Creates slides 4-5; does not present                    |
| Mikita | Part 3: product families, resolution, final testing, and deck assembly | Implement `POST /api/product-families/recompute/`; implement `GET /api/resolve/`; implement `GET /api/resolve/reverse/`; implement `POST /api/resolve/bulk/`; run full `test_api.py`; fix final integration issues; collect final test output; assemble final slide deck from all slides        | Working recompute endpoint; working resolve/reverse/bulk endpoints; full passing test result; final slide deck assembled; final demo script | Final handover is the completed project: code, test result, and presentation deck                                     | Creates slide 6; assembles deck; presents slides 4-6 (~2:30) |

## D. Fairness Check

| Person | Why the workload is fair                                                                                           |
| ------ | ------------------------------------------------------------------------------------------------------------------ |
| Igor   | Owns the most analysis-heavy part plus setup, proxy foundation, and opening presentation section                   |
| Paula  | Owns the highest validation burden: event lifecycle plus all invalid scenarios, and creates validation/risk slides |
| Mikita | Owns the final API behavior, full integration test, deck assembly, and the larger technical presentation section   |

No task is assigned to "everyone" or "all together." Every activity has one named owner.

## E. Slide Plan And Required Content

**Total duration: 5 minutes — 6 slides, ~50 seconds each. Igor presents slides 1-3 (0:00–2:30). Mikita presents slides 4-6 (2:30–5:00). Paula creates slides 4-5.**

| Slide                              | Owner  | Presenter | Time          | Must include (concise — one talking point per bullet)                                                                                                        |
| ---------------------------------- | ------ | --------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. Business Problem & Solution     | Igor   | Igor      | 0:00 – 0:50   | Demand forecasting needs history; code changes (reformulation, repackaging) orphan that history; chains link old code to new code; example `1001→1002→1003`  |
| 2. System Architecture             | Igor   | Igor      | 0:50 – 1:40   | Flask adapter on `:5050` proxies to Django backend; endpoints: setup, events, product-families, resolve; three test phases: setup → ingest → recompute+query |
| 3. Event Model                     | Paula  | Igor      | 1:40 – 2:30   | Three transition types: `INTRO`, `DISCONT`, `CHAIN`; required fields per type; example chain payload linking `1001→1002`; valid event returns HTTP 201        |
| 4. Validation Rules                | Paula  | Mikita    | 2:30 – 3:20   | 13 invalid cases → HTTP 400; key rules: no double intro, no overlap, no self-chain, codes must exist, missing fields rejected; status codes passed through    |
| 5. Product Families & Computation  | Mikita | Mikita    | 3:20 – 4:10   | Generation = code lifespan; chains form a DAG; recompute finds weakly connected components → one family per component; family ID e.g. `PL-IPC-0001`          |
| 6. Resolution & Test Results       | Mikita | Mikita    | 4:10 – 5:00   | `GET /api/resolve/` (code+date+country→family); `GET /api/resolve/reverse/` (family+date→active codes); all three test phases pass; final test output shown  |

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
| Presentation misses Paula's work            | Paula  | Put validation evidence into slides 4-5; Mikita presents them on her behalf          |

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
| Slides 1-2 completed                 | Igor   |
| Slides 3-4 completed                 | Paula  |
| Slides 5-6 completed                 | Mikita |
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