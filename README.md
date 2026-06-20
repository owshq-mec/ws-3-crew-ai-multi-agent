# E-Commerce Analytics Backbone

A purpose-built analytical data platform for a high-volume e-commerce company,
replacing a monolithic PostgreSQL system that was never designed for analytics.

This repository contains the **source system** and a **synthetic data
generator**: a transactional PostgreSQL database that mirrors the company's
production shape, seeded with realistic data, plus a generator that produces
continuous traffic and injects the exact failure modes the analytical pipeline
must survive.

The analytical pipeline (Dagster → dbt → DuckDB), the intelligence layer
(FastAPI + MCP), and the autonomous monitoring system (CrewAI Sentinel) are
built on top of this foundation. Full design:
[docs/tech-spec-analytics-backbone-sentinel-engine.pdf](docs/tech-spec-analytics-backbone-sentinel-engine.pdf).

## Why this exists

The business runs analytics directly against its transactional PostgreSQL
database. Heavy analytical queries lock resources needed for order processing,
schema changes in the application break downstream reporting, and engineers
spend their time firefighting instead of building. This backbone separates
transactional and analytical concerns — and proves the separation works by
continuously stress-testing it with injected failures.

## The data model

A transactional e-commerce schema —
[src/db/01_schema.sql](src/db/01_schema.sql):

| Table | Grain | Notes |
| --- | --- | --- |
| `customers` | one row per customer | segment, location, signup time |
| `products` | one row per SKU | category, unit price, cost |
| `orders` | one row per order line | references customer + product, priced |
| `payments` | one row per payment | references order, amount, method, status |
| `injected_incidents` | one row per injected failure | ground-truth ledger for evals |

The seeded data is **clean and referentially correct** — correlated orders,
prices consistent with the catalog, payments matching order totals, timestamps
that respect causality. It is the healthy baseline. All anomalies come from the
generator, on demand.

## Quickstart

```bash
make setup          # install Python deps with uv
cp .env.example .env
make up             # start PostgreSQL (schema auto-applied on first boot)
make seed           # load the clean, correlated baseline
make psql           # explore it
```

## The synthetic data generator

A permanent validation harness, not a demo script. It generates realistic
traffic and injects deliberate failures so the downstream pipeline and the
monitoring system can be proven against the chaos they will face in production.

```bash
make failures                       # list every failure mode
make traffic TRAFFIC=200            # insert normal orders
make inject FAILURE=schema_drift    # inject one failure
make reset-schema                   # revert schema drift (repeatable demos)
make watch                          # stream traffic + random failures (Ctrl-C)
```

### Failure modes

`make failures` lists them in two groups. Every injection is also written to
the `injected_incidents` ledger (see below).

**Base-crew failures** — detect, diagnose, report. Each maps to the monitoring
agent that catches it.

| Failure | Effect | Detected by |
| --- | --- | --- |
| `schema_drift` | renames `orders.customer_id` → `user_id`, breaking downstream models | Log Analyst |
| `negative_price` | order with a negative unit price and total | Data Profiler |
| `missing_customer` | order with a `NULL` customer reference | Data Profiler |
| `invalid_quantity` | order with a non-positive quantity | Data Profiler |
| `duplicate_order` | exact-duplicate order row | Data Profiler |
| `late_arrival` | order backdated 45 days (late-arriving data) | Data Profiler |
| `volume_spike` | sudden burst of orders | Data Profiler |
| `orphan_payment` | payment referencing a non-existent order | Data Profiler |

**Feature-unlocking failures** — each is designed to *demand* a specific CrewAI
capability. Read the failure, reason about what an agent would need to handle it
well, then build that capability.

| Failure | Effect | Unlocks |
| --- | --- | --- |
| `recurring_incident` | the same failure injected repeatedly | **Memory** — recognise a repeat offender instead of cold-starting |
| `ambiguous_anomaly` | revenue drops via cancellations *and* a price cut | **Knowledge/RAG** — consult a runbook to disambiguate root causes |
| `destructive_fix` | corrupts many rows; only a bulk overwrite fixes it | **Human-in-the-loop** — a destructive remediation must pause for approval |
| `malformed_data` | garbage text in status fields | **Guardrails + `output_pydantic`** — force a typed, validated post-mortem |
| `slow_source` | stalls the source database | **Tool reliability** — retries, timeouts, fallbacks |
| `multi_failure_cascade` | several failures at once | **Flows + conditional routing** — route each failure to the right squad |

The generator is **schema-drift aware**: traffic and every injector keep
working whether the customer column is `customer_id` or `user_id`, so a running
`watch` session never breaks itself. `make reset-schema` reverts the rename, so
the headline schema-drift scenario can be replayed as many times as needed.

### Incident ledger (ground truth)

Every injection is recorded in the `injected_incidents` table — failure key,
detail, the agent expected to detect it, and a timestamp. Because the generator
*knows* what it injected, this ledger is the ground truth a CrewAI evaluation
scores against: did the crew diagnose the failure that was actually injected?

## Make targets

```bash
make help           # list everything

# platform
make up / down / restart / reset
make seed / reseed
make psql / logs / ps / lint

# generator
make traffic / inject / failures / watch / reset-schema
```

Seed volume and generator behaviour are overridable:

```bash
make seed CUSTOMERS=2000 PRODUCTS=500 ORDERS=50000 SEED=7
make inject FAILURE=negative_price
make traffic TRAFFIC=1000
```

## Layout

```text
src/
  db/
    01_schema.sql       # DDL, auto-applied on container init
    connection.py       # PostgreSQL access
  seed/
    factories.py        # clean Faker domain factories
    seed.py             # baseline loader (CLI)
  gen/
    failures.py         # failure-mode registry
    engine.py           # traffic generation + watch daemon
    repository.py       # generator data access
    cli.py              # generator command surface
docs/                   # technical specification
```

## Stack

PostgreSQL 17 · Python 3.12+ · psycopg 3 · Faker · uv · Docker Compose
