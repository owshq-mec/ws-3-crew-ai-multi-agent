# Sketch · Sentinel Engine

The autonomous DataOps system — Layer 6 of the tech spec. A CrewAI hierarchical
crew that monitors the Analytical Backbone, detects injected failures,
diagnoses root cause, and proposes remediation — without human intervention.
Probabilistic; verified by *did it catch and correctly diagnose the failure?*

> Plan altitude: features, components, dependencies, build order. No atomic
> tasks, no code.

---

## Components (the crew)

### A1 · Manager (Tech Lead) — hierarchical coordinator
Owns the investigation. Receives the failure trigger, delegates to the squads,
validates findings, approves the post-mortem.
- **Tools:** AssignTask, ReviewOutput.
- **Depends on:** all other agents (it orchestrates them).

### Investigation Squad

### A2 · Log Analyst
Parses Dagster and dbt logs to pinpoint the broken node and error trace.
- **Tools:** ReadDagsterLogs, ReadDbtRunResults.
- **Depends on:** backbone interface — Dagster logs (C2), dbt run results (C3).

### A3 · Data Profiler
Queries DuckDB to confirm the anomaly — missing column, statistical drift,
constraint violation — correlating it to the failure.
- **Tools:** QueryDuckDB, ProfileTable.
- **Depends on:** backbone interface — DuckDB `gold_`/`silver_` tables (C4).

### Resolution Squad

### A4 · Data Engineer
Writes the fix — the dbt migration or Dagster patch — for the diagnosed root cause.
- **Tools:** WriteCodePatch, ValidateDbtModel.
- **Depends on:** A2 + A3 diagnosis.

### A5 · Incident Commander
Searches the historical incident RAG for similar past issues; authors a
blameless post-mortem.
- **Tools:** QueryHistoricalRAG, WriteMarkdownReport.
- **Depends on:** the full investigation; the RAG store.

---

## The remediation loop (build target)

```text
Detect ──► Trigger ──► Investigate ──────► Resolve
generator   webhook     Manager assigns:    Manager assigns:
injects     fires to     A2 Log Analyst      A4 Data Engineer (fix)
failure     Manager      A3 Data Profiler    A5 Incident Commander (post-mortem)
```

Ground truth for each run: the `injected_incidents` row + failure signature —
"did the crew's diagnosis match what was actually injected?"

---

## Interface needed FROM the backbone (the seam)

Read-only consumption — the Sentinel never reaches into backbone internals
beyond these:

| Needs | From | Used by |
| --- | --- | --- |
| Dagster run logs / asset status | C2 Ingestion | A2 Log Analyst |
| dbt run results | C3 Transform | A2 Log Analyst |
| DuckDB `gold_` / `silver_` tables | C4 Warehouse | A3 Data Profiler |
| `injected_incidents` + failure signature | C1 Source | Manager (ground truth) |
| Failure trigger (webhook on pipeline failure) | C2/C3 | A1 Manager |

This table is the contract. As long as the backbone provides these, the two
plans build independently.

---

## Dependencies & build order

```text
A2 Log Analyst ┐
A3 Data Profiler ┘─► A1 Manager ─► A4 Data Engineer ─► A5 Incident Commander
(build + test each agent against ONE injected failure, then wire the loop)
```

Build order: the two **investigation** agents first (A2, A3 — they only read,
easiest to verify against a known injected failure), then the **Manager** (A1)
to orchestrate, then the **resolution** agents (A4, A5). Wire the full loop last.

---

## Open / unresolved

- **Trigger mechanism:** webhook on pipeline failure vs. Sentinel polling
  Dagster/dbt status on a schedule. *(Owner: decide at task time.)*
- **RAG store** for A5 — needs a seed of historical incidents; `injected_incidents`
  can bootstrap it.
- **Model tiering:** spec suggests GPT-4o (Manager) + GPT-4o-mini (specialists);
  confirm against cost target.
- **Hard dependency:** the Sentinel can't be meaningfully tested until the
  backbone (C2/C3) produces real logs and DuckDB tables to read.
