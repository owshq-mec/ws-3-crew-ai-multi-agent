# Sketch · Analytical Backbone

The deterministic platform — Layers 1–5 of the tech spec. Extracts from the
transactional PostgreSQL source, transforms via dbt Medallion, materializes in
DuckDB, and exposes analytics through an MCP server. Same input → same output;
verified by tests and data assertions.

> Plan altitude: features, components, dependencies, build order. No atomic
> tasks, no code.

---

## Components

### C1 · Source (Layer 1) — *exists*
PostgreSQL transactional database: `customers`, `products`, `orders`,
`payments`, plus `injected_incidents`. Populated by the seeder (clean baseline)
and the data generator (traffic + injected failures).
- **Status:** built (`src/db`, `src/seed`, `src/gen`).
- **Depends on:** nothing.
- **Serves criteria:** the realistic source the whole platform reads from; the
  failures the Sentinel must catch originate here.

### C2 · Ingestion (Layer 2) — Dagster
Software-defined assets that incrementally extract Postgres → raw DuckDB
tables. Manages lineage and run dependencies.
- **Features:** incremental/CDC-style extraction; one asset per source table;
  run metadata + logs (the Sentinel's Log Analyst reads these).
- **Depends on:** C1 (source schema), C4 (DuckDB target).
- **Serves criteria:** sync transactional → analytical store without errors;
  near-real-time freshness (minutes, not 24h).

### C3 · Transformation (Layer 3) — dbt Medallion
`bronze_` (raw mirrors) → `silver_` (cleansed, deduped, typed) → `gold_`
(business aggregates / One-Big-Tables).
- **Features:** bronze/silver/gold models; dbt tests as data assertions; gold
  OBTs optimized for query.
- **Depends on:** C2 (raw tables in DuckDB).
- **Serves criteria:** clean, queryable analytics; schema-change resilience;
  dbt run results (the Log Analyst reads these too).

### C4 · Warehouse (Layer 4) — DuckDB
Embedded analytical engine the models materialize into and the MCP server
queries. Cloud path: swap file for MotherDuck, no SQL rewrites.
- **Depends on:** none (it's the substrate C2/C3 write to and C5 reads from).
- **Serves criteria:** sub-5s p95 query latency; the Data Profiler queries this
  directly for anomaly checks.

### C5 · Intelligence (Layer 5) — FastAPI + MCP
MCP server exposing three tools over the `gold_` tables: `get_schema_info`,
`execute_analytical_query`, `generate_report`. Natural-language access via
Claude Desktop.
- **Depends on:** C4 (DuckDB), C3 (gold tables to expose).
- **Serves criteria:** self-serve analytics for non-technical users; democratized
  data access without engineers building dashboards.

---

## Dependencies & build order

```text
C1 Source ──► C2 Ingestion ──► C3 Transform ──► (C4 Warehouse) ──► C5 Intelligence
 (done)        Dagster           dbt              DuckDB             FastAPI/MCP
```

Build order: **C2 → C3 → C5** (C1 done; C4 is the substrate, stood up alongside
C2). Each stage needs the previous stage's output to exist before it's testable.

---

## Interface exposed to the Sentinel

The Sentinel consumes (read-only) — see `sentinel-engine.md`:
- **Dagster run logs / asset status** (from C2) — for the Log Analyst.
- **dbt run results** (from C3) — for the Log Analyst.
- **DuckDB `gold_`/`silver_` tables** (C4) — for the Data Profiler's anomaly checks.
- **`injected_incidents` + the failure signature** (C1) — ground truth for what was injected.

---

## Open / unresolved

- **Freshness vs. "real-time":** the brief implies real-time; a Dagster→dbt
  batch pipeline delivers *minutes-fresh*, not true real-time. Confirm minutes
  satisfies the criteria, or scope true real-time as a later phase. *(Owner: VP Data.)*
- **CDC mechanism** for C2 (true CDC vs. incremental-by-timestamp) — decide at task time.
