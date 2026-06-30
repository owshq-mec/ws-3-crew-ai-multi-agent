# ws-3-crew-ai-multi-agent — an AI-native DataOps platform

A high-volume e-commerce company runs its storefront **and** its analytics on one
PostgreSQL database; the two workloads compete — heavy analytical queries lock
resources order processing needs, schema changes break reporting, and engineers
firefight instead of build. This repo is the fix: a purpose-built analytical
backbone that separates the two workloads, plus an autonomous agent crew that
watches it, diagnoses injected failures, and is **scored against ground truth**.

> **New here? Read the handbook first:** [`CLAUDE.md`](CLAUDE.md) is the project
> handbook (the two-component split, the agent fleet, the operating rules, the
> open decisions U1–U3, the acceptance criteria). The enforceable conventions are
> in [`.claude/rules/agent-operating-rules.md`](.claude/rules/agent-operating-rules.md).
> This README is the repo map; it points at the detailed per-package guides rather
> than restating them.

---

## WHAT — two components on one source

The system is **two components** over a shared source, with a strict one-way
dependency: **B reads A read-only; A never depends on B** (rule R3).

| Layer | Lives in | What it is |
| --- | --- | --- |
| **Source (C1)** | [`src/`](src/) | The operational e-commerce Postgres DB, a deterministic seeder, and a 14-mode chaos generator that injects failures and logs each as ground truth in the `injected_incidents` ledger. The only thing that writes to source Postgres. |
| **Component A — Analytical backbone (deterministic)** | [`platform/`](platform/) | Postgres → Dagster ingestion (C2) → dbt medallion bronze/silver/gold (C3) → DuckDB warehouse (C4) → FastAPI + MCP intelligence (C5), plus the peak-load harness (C4h) and freshness probe (C8) that measure the acceptance criteria. |
| **Component B — Sentinel engine (probabilistic)** | [`sentinel/`](sentinel/) | A CrewAI **hierarchical** crew (manager A1 + specialists A2–A5) with a trigger (B1) and a scoring oracle (I4). It watches A, diagnoses the injected failures, proposes gated fixes, and is graded against the ledger — never asserted correct. |

The `injected_incidents` ledger is the **architectural seam**: the generator
writes it (ground truth); the Sentinel reads it read-only as its scoring oracle
(interface I4). Each package has its own contributor handbook:

- [`src/README.md`](src/README.md) — schema, deterministic seeder, the 14-failure registry.
- [`platform/README.md`](platform/README.md) — the six backbone components, the one-DAG asset graph, the evals and AC verdicts.
- [`sentinel/README.md`](sentinel/README.md) — the five-agent crew, the 14-failure → CrewAI-capability map, the I1–I5 interface, the scoring rubric.

The locked architectural decisions are recorded as ADRs in
[`docs/adrs/`](docs/adrs/) — [ADR-0001 (backbone)](docs/adrs/0001-analytical-backbone.md)
and [ADR-0002 (sentinel)](docs/adrs/0002-sentinel-engine.md). The reference PDFs
(engineering brief, BRD, canonical tech spec) are indexed in
[`docs/README.md`](docs/README.md).

---

## WHY — the design in one line each

- **Why separate source from analytics.** Analytical load must never lock the
  transactional path; the backbone lifts the source into a DuckDB warehouse so the
  two workloads stop competing. The separation is *measured* against the source,
  not assumed (AC-1 peak isolation).
- **Why chaos with a ground-truth ledger.** The generator injects the exact
  failures the pipeline must survive and records what it injected. That ledger
  makes the Sentinel **scorable** instead of merely asserted — did the crew
  diagnose the failure that was actually injected?
- **Why a deterministic A and a probabilistic B (R5).** Component A is verified by
  assertion (did the row land, did the query hit the latency budget); Component B
  is verified by scoring against the I4 oracle. Two verification models, hence two
  halves of the repo.
- **Why decisions live in ADRs.** The open questions (U1 scope, U2 raw boundary,
  U3 detection seam) are non-obvious and will be re-litigated; ADR-0001/0002 lock
  them against shipped code so they are answered by a file, not by memory.

---

## HOW — running it

`uv` for packages, `ruff` for lint, Docker Compose for Postgres. `make help`
lists every target. **Set the environment contract** (the Makefile sets it for
you; export it for bare commands):

```bash
export PYTHONPATH=$(pwd)          # the local platform/ package shadows stdlib platform
export DUCKDB_DATABASE=$(pwd)/platform/warehouse/warehouse.duckdb
export DAGSTER_HOME=$(pwd)/.dagster_home
```

> **DuckDB is single-writer.** Never run two warehouse-writing steps (C2 ingest,
> C3 dbt build, C8 probe, the defect eval) concurrently. If a step reports
> "database is locked", clear the stale holder before retrying:
> `lsof -t platform/warehouse/warehouse.duckdb | xargs -r kill -9`.

### 1. Source — bring it up and seed (`src/`)

```bash
make setup                 # install Python deps with uv
cp .env.example .env
make up                    # PostgreSQL on :5432 (schema auto-applied on first boot)
make seed                  # clean correlated baseline (500 customers / 200 products / 5000 orders)
make failures              # list every failure mode
make inject FAILURE=negative_price   # inject one failure (recorded in injected_incidents)
make reset-schema          # revert the schema-drift rename (repeatable demos)
```

Full source detail (tables, factory invariants, the 14-failure registry, the R7
reset caution): [`src/README.md`](src/README.md).

### 2. Component A — run the backbone (`platform/`)

```bash
make ingest-once           # C2 raw ingestion (Postgres -> DuckDB raw.raw_*), incremental
make dbt-build             # C3 dbt medallion: raw -> bronze/silver/gold
make dagster-dev           # interactive Dagster UI on :3000 (do NOT launch a second one)
make evals                 # ALL acceptance-criteria evals, scaled-down, + verdict table
```

The acceptance-criteria evals (`eval-ac1/ac2/ac3`, `eval-defects`) print
`PASS`/`FAIL`/`SKIP` and the exit code is the contract. Per the honesty rule a
verdict must be the **measured** result of an actual run, never asserted. Full
backbone detail (the one-DAG asset graph, single-writer rule, the AC verdict
table): [`platform/README.md`](platform/README.md).

### 3. Component B — run the Sentinel (`sentinel/`)

```bash
# Poll the I4 ledger for incidents since a cursor captured before inject, dispatch, score:
uv run python -m sentinel.trigger --since "2026-06-30T00:00:00+00:00"
```

The trigger routes a single failure to the hierarchical crew and a
`multi_failure_cascade` to the deterministic cascade Flow; the oracle grades the
typed `Diagnosis` against the ledger. Running the *crew* needs an LLM API key; the
cascade Flow and the scoring oracle are deterministic and run offline. Full
Sentinel detail (the agent roster, the capability map, the scoring rubric, the
stub-LLM vs live verification): [`sentinel/README.md`](sentinel/README.md).

### Tests

```bash
make lint                  # ruff check src platform sentinel tests
PYTHONPATH=$(pwd) DUCKDB_DATABASE=$(pwd)/platform/warehouse/warehouse.duckdb \
  DAGSTER_HOME=$(pwd)/.dagster_home uv run pytest
```

Suites live under [`tests/`](tests/): backbone end-to-end + per-component tests,
and `tests/sentinel/` (crew assembly, tools, dispatch, the cascade Flow, the
offline inject→detect→score proof, and the API-key-gated live scorecard). Warehouse-touching
tests serialize under the single-writer rule; live-LLM cases skip with a clear
reason when no API key is present.

---

## WHERE — repo map

```text
src/                  C1 source: Postgres schema + seeder + 14-failure chaos generator → injected_incidents
platform/             Component A (deterministic): C2 ingestion · C3 transform · C4 warehouse · C5 intelligence · C4h harness · C8 probe · evals
sentinel/             Component B (probabilistic): CrewAI hierarchical crew A1–A5 + B1 trigger + I4 scoring oracle + cascade Flow
tests/                pytest suites (backbone e2e + per-component; tests/sentinel/ for Component B)
sketch/               the two design plans (analytical-backbone.md, sentinel-engine.md)
docs/                 reference PDFs + adrs/ (ADR-0001 backbone, ADR-0002 sentinel)
.claude/              agent fleet, KBs, operating rules, doctrine (source of truth for AGENTS.md / Cursor / Copilot — R9)
CLAUDE.md             the project handbook — read this first
Makefile              the public command surface (make help)
```

## Stack

PostgreSQL 17 · Dagster · dbt · DuckDB · FastAPI + MCP · CrewAI · Python 3.12+ ·
psycopg 3 · Faker · uv · Docker Compose

## Status

Both components are built and verified end-to-end. Most recent full run:

- **Backbone (A):** `dagster job execute -j backbone_end_to_end` → SUCCESS; dbt
  `PASS=14`. Acceptance criteria measured **PASS** — AC-1 peak isolation (zero
  analytics-attributable lock-waits), AC-2 gold query p95 ≈ 18 ms (≤ 5 s budget),
  AC-3 freshness within the ≤ 5 min budget, and U3 defect-survival (every injected
  defect quarantined to `*_rejects`, none leaked to gold). Backbone test suite green.
- **Sentinel (B):** `pytest tests/sentinel/` → **79 passed, 6 skipped** (the 6
  skips are the API-key-gated live-LLM scorecard; the offline inject→detect→score
  loop is fully covered). Closer review: **APPROVE, 0 blockers**.

Numbers are the measured result of an actual run, per the honesty rule — re-run
`make evals` and `pytest` to refresh them.
