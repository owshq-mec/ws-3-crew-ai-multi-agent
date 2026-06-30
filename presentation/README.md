# presentation/ — workshop slide decks

The teaching collateral for the **Formação AI Data Engineer / AIDE Brasil**
workshop series, authored by Luan Moreno Medeiros Maciel. Each file is a single,
self-contained `.html` slide deck — open it in a browser, scroll to advance.

> These are deliverables for *teaching* the project's concepts, not part of the
> runnable platform. Nothing in [`../src`](../src), [`../platform`](../platform),
> or [`../sentinel`](../sentinel) imports, serves, or tests them. Project-wide
> context (the two-component split, the agent fleet, the operating rules) lives in
> [`../CLAUDE.md`](../CLAUDE.md); it is referenced here, not duplicated.

---

## WHAT — the decks

| File | Title | Topic | Slides |
|------|-------|-------|--------|
| `w3-multi-agent.html` | W03 — CrewAI Multi-Agent: Autonomous DataOps Sentinel | The deck for **this** repo's workshop. The agentic shift (reason → act → observe), why one monolithic agent fails, hierarchical crews (a manager delegates), the 6-layer AI-native platform ("one pipeline, one Sentinel"), and the Converge build method. Acts I–VII. | 40 |
| `w1-rag.html` | W01 — Enterprise RAG: LlamaIndex + Pydantic | RAG fundamentals → production: the 9-step ingestion/runtime pipeline, the three cognitive stores (Postgres text-to-SQL, Qdrant vector, Neo4j graph), Langflow prototyping, and LlamaIndex as the orchestrator. Acts I–VII. | 55 |
| `cvg-aut-systems-spine-deck.html` | Converge — Compile Intent into Autonomous Systems | Methodology-only deck: the end-to-end "Converge" spine — seven passes, one fork, one gate (Intent · Structure · Decomposition · Consensus · Tasking · Harness · Execution). Successor to the deleted `w-converge.html`. | 10 |

Slide counts are exact: each deck's nav script counts its own `section.slide`
elements (see *HOW* below), and these are those counts. They are the source of
truth if the table ever drifts.

---

## WHY — three decks, no build step

- **Why self-contained HTML.** A deck must open from a USB stick, a download
  folder, or a fork with no toolchain. Each file inlines its own CSS in a
  `<style>` block and its nav logic in a trailing `<script>`; the only external
  dependency is Google Fonts over CDN (offline → default fonts, layout intact).
  There is no bundler, no server, no shared asset directory to keep in sync.
- **Why no shared template.** Each deck duplicates its own CSS and nav script on
  purpose. There is **no** partial, include, or template to edit globally — a
  change to one deck does not propagate to the others, and a maintainer must not
  assume reuse. The decks are deliberately independent artifacts.
- **Why the numbering gap (W01, W03, no W02).** The filenames track the workshop
  series, not this folder; W02 is simply not part of this repo. The gap is
  expected, not a missing file.

---

## HOW — viewing and navigating

Open any deck directly in a browser (`open presentation/w3-multi-agent.html`).
There is nothing to install or serve. Scroll to move between slides — each deck
uses CSS scroll-snap, one slide per viewport.

Navigation chrome is vanilla JS in the trailing `<script>`, and comes in two
shapes:

- **`w1-rag.html` and `w3-multi-agent.html`** share one scheme: a top
  `.deck-progress` bar, a bottom-right `.deck-counter` showing `NN / NN`
  (`#n` / `#total`), and a `.deck-tracker` (`#tracker`) dot rail. The script
  builds the dots and counter from `deck.querySelectorAll('section.slide')`, then
  updates them on scroll.
- **`cvg-aut-systems-spine-deck.html`** is simpler: a single `.deck-counter`
  text node, no progress bar or dot rail. Its script also sets
  `window.__captureReady = true` after wiring up — a readiness flag for an
  external screenshot / PDF capture tool. `docs/cvg-aut-systems-spine.pdf` at the
  repo root shares this deck's slug and is most likely produced from it via that
  hook, though the capture tooling itself is not in this repo.

---

## WHERE — git state and maintenance

- `w1-rag.html` is committed. `w3-multi-agent.html` and
  `cvg-aut-systems-spine-deck.html` are currently untracked — commit them to make
  the set complete.
- `w-converge.html` was removed; `cvg-aut-systems-spine-deck.html` is its
  successor (same methodology, refreshed).
- When you edit a deck, update the slide count in the *WHAT* table if you added
  or removed `section.slide` elements — the deck's own counter will show the new
  total, but this table will not update itself.
- These are presentation files only: do not add platform logic, imports, or test
  hooks to them.
