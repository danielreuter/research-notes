---
lane: pous
kind: handoff
from: verity-root
created: 2026-09-27T06:15Z
---

# Orientation for the POUS coordinator: how Verity is organized

Daniel asked me to help you get oriented. Ask me anything through `lanes/verity-root/`.

## Where things are

- **The repo** (`danielreuter/verity`):
  - `AGENTS.md` holds the binding rules; `README.md` holds the architecture.
  - `packages/verity/` is the core. `verity.ir` is standard-library only. Import from the module that owns a name.
  - `tools/research/` is the harness: the `research` CLI, with runs, pods, the evidence store and merges. It must not import `verity`.
  - Components (`backends/`, `integrations/`) are created only when real code lands.
- **Lean, on `main`:** `backends/flock/verifier/lean/` has three parts:
  - the executable verifier;
  - `level3/`, the proofs about its arithmetic;
  - `soundness/`, the proofs, with `ASSUMPTIONS.md` as the ledger, `DESIGN.md`, and `Check.lean` as the axiom-audit list.

  Every Lean PR gets an independent build and `#print axioms` audit on a pod before it merges. Allowed are `propext`, `Classical.choice` and `Quot.sound`, with named hypotheses only.
  - A new worker (bc-866e1acc, "Design Verity Lean organization") is writing `docs/lean-organization.md` in the Verity store tonight. That covers the package layout, the trust boundary, a shared axiom-audit tool, and cross-Project reuse. Your trusted Lean layer and grader overlap with it, so please send it your design through me, or via `lanes/verity-root/`.
- **The notes repo** (`danielreuter/research-notes`):
  - `kb/LANE-CONTRACT.md` is the lane rulebook.
  - Each lane keeps `lanes/<lane>/` for its report (`research notes checkpoint <lane> …`) and handoffs (`<UTC>-handoff-from-<lane>.md`).
  - `machines.d/` is the pod registry.
- **The evidence store:** runs are recorded with `research run --tool … --campaign …`, and each one is published as an Attempt. Findings are labels, `research data label <run> <key> <value> --by <lane>`. The contract is `tools/research/src/research/store/README.md`.

## How work flows

- **Lanes** are cloud agents with one scope each. They report to a coordinator: the research coordinator (bc-8ece7cde) for Flock, Lean and benchmarks, and the vLLM coordinator (bc-ecac3029) for vLLM. The root, which is me, routes between them and talks to Daniel.
- **Merges:** only the research coordinator merges to `main`. A merge needs a passing `check` for the exact commit (`research merge`), and approved PRs merge in trains. There's no GitHub Actions.
- **Pods:** use `research run --on <machine>`. Never prove on a laptop or the control pod, give every pod a guard and an estimate first, and never copy secrets to a pod.
- **Writing:** only code, tests and maintained docs go in the repo. Reports and handoffs go in notes, and evidence goes in R2 or the store. Don't create report-style files in the repo; a test rejects them.

## For you

- Before pous code goes into the Verity repo, tell me where you'd put it. By `AGENTS.md`, a new component appears only with real code, and it must import inward to the core.
- If your VM lacks `RESEARCH_NOTES_TOKEN`, tell Daniel.
