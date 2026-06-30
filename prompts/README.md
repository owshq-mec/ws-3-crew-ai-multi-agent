# prompts/ — Converge: the 4-pass planning methodology

The front of the funnel. Before any code is written, a problem travels from a raw
business document to two adversarially-hardened build plans through four ordered
passes. These files are the **operator prompts** for that journey: copy-paste
scripts a human pastes into a named AI engine, one pass at a time. They are
human-facing prose, not executable code — there is nothing here to run, only to
read and paste.

The final output of this folder — [`../sketch/analytical-backbone.md`](../sketch/analytical-backbone.md)
and [`../sketch/sentinel-engine.md`](../sketch/sentinel-engine.md) — is what every
tech agent later builds against. Get the plans right here and the build downstream
inherits the rigor; get them wrong and no amount of careful coding recovers it.

> This README is the folder-level overview the four pass files cannot give
> themselves. Project-wide context (the two-component split, the agent fleet, the
> open decisions U1–U3, the acceptance criteria) lives in [`../CLAUDE.md`](../CLAUDE.md);
> it is referenced here, not duplicated. The longer-form narrative of the
> methodology lives in the decks and PDF noted under WHERE.

---

## WHAT — the pipeline at a glance

Converge is a strictly linear four-stage relay. Each pass's output is the next
pass's input; the engine deliberately changes per pass so the work gets the right
kind of thinking at each stage (see WHY below).

| Pass | Engine | Input | Output | Gate |
|------|--------|-------|--------|------|
| [P1 · Intent](p1-intent.md) | Claude Chat (no repo) | `docs/business-requirements-document.pdf` | `docs/engineering-brief.pdf` | Problem confirmed; scope explicit; every acceptance criterion verifiable; metrics trace to BRD KPIs; **no technology choices** |
| [P2 · Structure](p2-structure.md) | Claude Code (repo open) | tech-spec PDF + engineering-brief PDF + `src/` | **none** — shared understanding held in session | You can explain the whole system; it is consistent with the brief and the real repo |
| [P3 · Decomposition](p3-decomposition.md) | Claude Code, Auto Mode (**same session as P2**) | the P2 understanding + tech-spec + `src/` | `sketch/analytical-backbone.md` + `sketch/sentinel-engine.md` | Two plans split along the spec's seam; each lists features/deps/build order; the Sentinel names its interface to the backbone |
| [P4 · Consensus](p4-consensus.md) | Codex (adversary) + Claude (defends/revises) + docs as ground truth | both sketch plans + tech-spec + brief | the **same two plans sharpened in place** + an open-questions list | No open objection remains — every attack is FIXED in a plan or ACCEPTED with an owner |

### The relay, drawn

```
docs/business-requirements-document.pdf
            │
            ▼
   ┌──────────────────┐   Claude Chat
   │ P1 · Intent      │   (no repo, pure problem)
   └──────────────────┘
            │  emits
            ▼
   docs/engineering-brief.pdf
            │
            ▼
   ┌──────────────────┐   Claude Code
   │ P2 · Structure   │   + tech-spec PDF + src/
   └──────────────────┘   (check spec vs. real repo)
            │  emits NO file
            │  (understanding held in the live session)
            ▼
   ┌──────────────────┐   Claude Code, Auto Mode
   │ P3 · Decompose   │   *** SAME SESSION AS P2 ***
   └──────────────────┘
            │  emits
            ▼
   sketch/analytical-backbone.md  +  sketch/sentinel-engine.md
            │
            ▼
   ┌──────────────────┐   Codex attacks · Claude revises
   │ P4 · Consensus   │   + docs as ground truth
   └──────────────────┘
            │  sharpens in place
            ▼
   same two plans, hardened  +  open-questions list
            │
            ▼
   handoff to task decomposition (outside prompts/)
```

---

## WHEN — picking the right pass

Each pass has an entry precondition and an exit gate. Run them in order; do not
skip into the middle of the relay.

- **P1 · Intent** — when you have a raw BRD and **no agreed problem statement**.
  Enter with the business document; leave with an engineering brief whose every
  acceptance criterion is verifiable and traces to a BRD KPI, and that names zero
  technologies.
- **P2 · Structure** — when a **tech-spec exists** and must be understood and
  grounded against the real repo before anyone plans. Enter with spec + brief +
  `src/`; leave when you can explain the whole system and it is consistent with
  what is actually on disk.
- **P3 · Decomposition** — when the understanding is **loaded in session** and you
  need to split the system into its two-component plans. Enter still inside the
  P2 session; leave with two `sketch/*.md` plans split along the spec's seam, the
  backbone→sentinel interface named.
- **P4 · Consensus** — when the **plans exist** and need adversarial hardening
  before they feed the build. Enter with both plans + the docs; leave when no
  objection is unresolved — each one fixed in a plan or accepted on the record
  with an owner.

---

## The two mistakes a newcomer makes

These are the two easiest ways to break the methodology. Both are encoded in the
pass files but easy to miss.

1. **P2 emits no file — so P2 and P3 must run in the SAME Claude Code session.**
   Pass 2's entire output is *in-session understanding*; there is no artifact to
   hand off. Close the session and the handoff is gone — you would have to redo
   P2's comprehension before you can decompose. Keep one live Claude Code session
   open from the start of P2 through the end of P3. (See [`p2-structure.md`](p2-structure.md)
   lines 5 and the Notes; [`p3-decomposition.md`](p3-decomposition.md) line 3.)

2. **P4 must use a DIFFERENT engine (Codex) — not Claude reviewing its own plans.**
   The value of the consensus pass is cross-model refutation: Claude agrees with
   itself and will not attack its own plan hard enough. Bring Codex as the
   adversary; Claude only defends and revises. Running P4 as Claude self-review
   gives you agreement, not consensus. (See [`p4-consensus.md`](p4-consensus.md)
   line 3 and the Notes. Fallback if Codex is down: a fresh Claude session with no
   memory of writing the plans — weaker, but better than self-review in context.)

---

## WHY — the engine changes every pass

The engine is chosen per pass on purpose; it is not arbitrary.

- **P1 → Claude Chat (no repo).** Intent is a pure problem-understanding task.
  Keeping the repo out forces the conversation to stay on the business problem and
  off the solution — no technology leaks into the brief.
- **P2 → Claude Code (repo open).** Comprehension means checking the spec against
  the real `src/`. The repo is the evidence the spec must honor, so the engine has
  to see the schema and the generator, not just the document.
- **P3 → Claude Code, Auto Mode.** Decomposition is exploratory drafting — reading
  across the spec and repo to write two plans. Auto Mode earns its keep here;
  you gate the result.
- **P4 → Codex (the adversary).** Consensus requires a model with no ego in
  Claude's plans. A different engine refutes; Claude defends and revises. The
  cross-model disagreement is the whole point of the pass.

---

## The brief's PDF → markdown lifecycle

The engineering brief is **born as a PDF on purpose**. At P1 it is a *human
consensus object* — a document you circulate and align on with the team, like the
tech-spec. By design it converts to markdown only once consensus is locked and it
enters the build, the same lifecycle as the tech-spec.

**Current state on disk:** [`../docs/engineering-brief.pdf`](../docs/engineering-brief.pdf)
exists; there is no markdown engineering-brief. The brief is therefore still in its
PDF / consensus phase — which is exactly what the lifecycle predicts at this point
in the program. (P4's input list notes the brief is consumed "when it exists",
reflecting that this artifact is a consensus object that may still be in flux.)

---

## A design constraint behind the brevity

Every pass file ends with the same note: these prompts are short **because a human
is watching**. The operator narrates the flip in P1 Step 2, gates each pass, and
catches drift the conversation cannot fix on its own. To hand any step to an
**unattended** agent later, the prompt must become precise — spell out the output
structure and emit a file — because no one is in the loop to correct it. The gate
constraints (verifiable, tied to KPIs, no tech at P1; no unresolved objection at
P4) never relax, regardless of how short the prompt is. P4's Notes call this out
as where the "dark-factory gate" eventually lives: tomorrow the adversarial pass is
automated and "no unresolved objection" becomes the eval that gates the build.

---

## WHERE — how this connects to the rest of the repo

`prompts/` is the planning front-end; the rest of the repo is everything those
plans produce. The gate constraints map directly onto repo doctrine, so this
folder is not a detached island:

- **The plans it emits** — [`../sketch/analytical-backbone.md`](../sketch/analytical-backbone.md)
  and [`../sketch/sentinel-engine.md`](../sketch/sentinel-engine.md) — are the two
  components every tech agent builds against (Component A the deterministic
  backbone; Component B the Sentinel crew). The two-component split P3 finds along
  the spec's seam is the same split enforced repo-wide.
- **The open decisions** P4 hardens into are the repo's **U1–U3** in
  [`../CLAUDE.md`](../CLAUDE.md): U1 scope (the brief scopes Component B and the MCP
  layer *out* — "evaluate after the foundation is proven"; the Sentinel sketch
  carries this scope flag in its header), U2 raw boundary, U3 detection seam.
- **The "every AC verifiable" gate** at P1 and the **acceptance-criteria mapping**
  at P3 are the brief's **AC-1…AC-6** in [`../CLAUDE.md`](../CLAUDE.md), measured
  by the backbone's evals (see [`../platform/README.md`](../platform/README.md)).
- **The live ammunition** P4 cites is real and present in the sketch headers — the
  **freshness gap** (batch pipeline vs. real-time intent, flagged in
  `analytical-backbone.md`), the **Sentinel's hard dependency** on the backbone
  (it consumes A's exhaust read-only; A never depends on B), and **interface
  completeness** (does the Sentinel need anything not in the contract?).
- **The locked decisions** that resulted from this process are recorded as
  [`../docs/adrs/0001-analytical-backbone.md`](../docs/adrs/0001-analytical-backbone.md)
  and [`../docs/adrs/0002-sentinel-engine.md`](../docs/adrs/0002-sentinel-engine.md).

### Related, longer-form methodology (not operational prompts)

These describe the Converge methodology as narrative; the four files here are the
operational scripts. They are present in the repo but not linked from the passes:

- [`../docs/converge-spine-methodology.pdf`](../docs/converge-spine-methodology.pdf)
  and [`../docs/cvg-aut-systems-spine.pdf`](../docs/cvg-aut-systems-spine.pdf) — the
  long-form methodology write-ups.
- [`../presentation/`](../presentation) — the workshop decks
  (`cvg-aut-systems-spine-deck.html`, `w3-multi-agent.html`).

### Source documents the passes consume

- [`../docs/business-requirements-document.pdf`](../docs/business-requirements-document.pdf) — the BRD, P1's input.
- [`../docs/engineering-brief.pdf`](../docs/engineering-brief.pdf) — P1's output, P2's input.
- [`../docs/tech-spec-analytics-backbone-sentinel-engine.pdf`](../docs/tech-spec-analytics-backbone-sentinel-engine.pdf) — the tech-spec, input to P2/P3/P4.
