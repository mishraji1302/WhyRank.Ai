# Project Test Report

**Project:** WhyRank information retrieval system
**Date:** 2026-09-26
**Environment:** macOS ARM64, Python 3.13, local cached MiniLM model

## Summary

The API and frontend build work in the tested local environment. The cached MiniLM encoder loads, and all 32 backend tests now pass. The initial crawler test collection issue is fixed. The neural reranker still scores substantially below BM25 in the corrected comparison, and human user acceptance testing remains outstanding.

| Test stage | Result | Evidence and scope |
|---|---|---|
| Unit testing | **Pass** | All 32 backend tests passed, including the previously uncollected crawler/normalizer tests and new API security checks. |
| Integration testing | **Pass for local API flows** | FastAPI `TestClient` exercised health, document, indexing-protection, and search routes. Search returned results for an in-corpus query and zero results for the out-of-vocabulary query. |
| Functional testing | **Pass for sampled flows** | Valid search returned results; `blue cow is dancing` returned zero results and identified `blue`, `cow`, and `dancing` as missing keywords. Invalid weights, an out-of-range limit, unsupported scoring mode, and overlong query returned HTTP 422. |
| System testing | **Pass for local smoke scope** | API health and document endpoints returned HTTP 200; corpus contained 2,708 documents; cached MiniLM loaded. No persistent server was started. |
| Performance / load / stress | **Limited local sample** | After warm-up, 12 sequential searches had p50 42.2 ms and p95 42.7 ms. A burst of 9 requests across 3 worker threads returned all HTTP 200, with observed per-request times about 79–163 ms. A repeatable 9-request burst test also passed in the backend suite. This is not sustained or production-scale load/stress testing. Initial import/index preparation took about 46 seconds in this environment. |
| Security testing | **Reviewed findings fixed; limited scope** | Wildcard CORS, exception-detail leakage, unauthenticated write routes, and missing request bounds/rate limiting were addressed. Automated regression tests cover CORS, generic write denial, invalid write token, query size, and rate limiting. No penetration scanner was run. |
| ML model evaluation | **Models evaluated; neural reranker underperforms** | Corrected offline harness uses 15 judged CORA queries and separate TF-IDF and MiniLM rankers. BM25: P@10 1.0000, Recall@10 0.0306, MAP 0.0306, NDCG@5 0.4341, NDCG@10 0.5406. BM25 + TF-IDF: 1.0000, 0.0306, 0.0306, 0.4286, 0.5429. BM25 + MiniLM: 1.0000, 0.0306, 0.0306, 0.4286, 0.5361. BM25 + MiniLM + PyTorch neural reranker: 0.3267, 0.0113, 0.0055, 0.0689, 0.1368. |
| Explainability testing | **Partial pass** | Explanation structure and attribution tests passed. No faithfulness/fidelity measurement or user study was performed. |
| User acceptance testing | **Not performed** | Requires review by the intended user/stakeholder against agreed acceptance criteria. |
| Regression testing | **Pass for covered cases** | The full 32-test backend suite includes the unmatched-query, crawler/normalizer, security, and small concurrent-search regression cases. Frontend production build passed. |

## Security changes

- CORS now allows only origins listed in `CORS_ALLOWED_ORIGINS`; the default is the two local Vite origins.
- Unexpected exceptions are logged on the server and clients receive only `Internal server error`.
- `POST /api/documents` and `POST /api/index` require `X-API-Write-Token` matching `API_WRITE_TOKEN`. If the server token is unset, mutations are disabled with HTTP 503. Invalid or missing tokens when configured receive HTTP 401.
- Search queries are limited to 500 characters. New document title, body, and URL are bounded to 300, 200,000, and 2,048 characters respectively.
- API requests have a configurable sliding-window limit (`API_RATE_LIMIT_PER_MINUTE`, default 120 per client IP per minute), returning HTTP 429 and `Retry-After` when exceeded.
- `backend/.env.example` documents the configuration names. Generate a real write secret with `openssl rand -hex 32`, then set it as `API_WRITE_TOKEN` in the ignored `backend/.env` file.

The rate limiter is in-process and should be replaced with a shared store if the service runs in multiple workers/instances. These checks do not constitute a penetration test.

## Repairs made during testing

- Registered API routers when the FastAPI application is created, fixing route availability when lifespan startup hooks are not run.
- Changed PageRank’s fallback graph construction to run only when there are no usable citation edges. This avoids a costly all-pairs similarity graph for a sparse but non-empty citation graph.
- Updated the API regression query to use terms present in the CORA corpus and added a check that unmatched query keywords produce an empty result set.
- Restored the crawler/normalizer contract expected by its test module, including `SimpleCrawler`, normalized content hashing, HTML stripping, and URL query canonicalization; fixed the seed-data test path.
- Corrected the evaluation harness so TF-IDF and MiniLM are measured with separate retrievers instead of identical configurations.

## Test commands and outcomes

- Full backend suite: `HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false ./venv/bin/python -m pytest -q` from `backend/` — **32 passed, 1 warning in 94.10 seconds** (Starlette deprecation warning concerning `httpx`/`TestClient`).
- Frontend build: `npm run build` from `frontend/` — **passed**.
- Frontend lint: `npm run lint` from `frontend/` — **unable to run**, because the `eslint` executable is not installed (`eslint: command not found`).
- ML evaluation: `HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false ./backend/venv/bin/python evaluation/eval_harness.py` from the project root — completed with the metrics above.
- Loky cleanup regression: `./venv/bin/python -m pytest -q tests/test_joblib_processes.py` from `backend/` — **1 passed**. A direct `Parallel(n_jobs=-1)` probe ran serially (`joblib multiprocessing: None`, CPU count 1) with no semaphore warning.

## Recommended follow-up

1. Improve the neural reranker before relying on it. Its metric is far below BM25. This checkout contains a `neural_ranker.pt` checkpoint but no training script or checkpoint metadata, so training data, labels, and provenance cannot be independently verified. The evaluation uses grade >= 2 as relevant for P/R/MAP and graded gains for NDCG; the same CORA qrels are used across configurations.
2. Run sustained load and multi-instance rate-limit testing in the intended deployment environment.
3. Have a stakeholder complete UAT using the acceptance checklist below.

### UAT checklist for a project stakeholder

- Confirm an in-corpus query returns relevant documents and the displayed four signal weights match the submitted weights.
- Confirm an unrelated query such as `blue cow is dancing` shows no results and lists unmatched keywords.
- Compare manual and neural ranking on several judged queries; decide whether the neural mode is acceptable given the benchmark results above.
- Confirm each result explanation is understandable and corresponds to its shown score breakdown.
- Confirm protected indexing/document-write operations reject missing or incorrect tokens and succeed only when intentionally configured.

## Limitations

Results describe this local macOS ARM64 run and the available CORA data/model cache. They do not establish production capacity, broad security assurance, or acceptance by end users. Linting was unavailable because ESLint is missing, and no browser-driven end-to-end test or human UAT was performed.
