---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
lane: coordinator
kind: handoff
from: workstream-3 backend sweep (bc-ea1c2c4f)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T01:00Z
---

# To the research coordinator: backend sweep phase 1, recording and labels (plan: `docs/backend-sweep.md`)

The sweep isn't launched. It waits for Daniel's go and for M0's prover-of-record PR (a) with `check` passed. I need your call on four points about recording, so the per-shape and row figures render.

**What each run records:**
- **Tool:** `flock_class_sweep` (`backends/flock/tool.py`, registered in `research.store.tools_registry` on [PR #182](https://github.com/danielreuter/verity/pull/182)).
- **Command:** `bash backends/flock/pod/70-class-sweep.sh GRAPH=… SHAPES=… [MODULES=…] BATCH=auto WARM=1 RUNS=3`. GRAPH and SHAPES are content-keyed params.
- **Result:** `research/result/v0.1`, fingerprint `kind: class-sweep/v1`, with every shape's record in `class-sweep.jsonl` (the measurement file). A record holds:
  - its keys: shape digest (`verity.ir.units`), flat Definition, and units per Call and per row;
  - its statement: ANDs, `k_log`, unit rows and matrix entries, the class and statement SHA-512;
  - the median timed session: accepted, proof bytes, prove, witness and end-to-end seconds, verifier seconds, `dense_m`, peak memory;
  - the selftest, and where the shape broke.
- **Campaign:** `backend-sweep-p1`. One Attempt per chunk of about 50 shapes per pod.

**Four points for you:**
1. **Labels:** I propose `row={n}`, `program_digest={sha256}`, `shape={digest}` (for single-shape reruns) and `protocol=sweep-v0` on every Attempt, and `protocol=tables-v1` on the about 10 representative #101 shapes run under the full cell protocol with a separate verifier pod. Is that the vocabulary you want (`research.store.vocab`)?
2. **Rendering:** the per-shape and whole-row views are new (overhead against native on both of headline.py's bases, proof size, verifier time, and AND coverage per row). Should `views` render them from `class-sweep/v1` Attempts, or should I publish a derived roll-up Attempt (`--tool backend_sweep_rollup`) and you add a view over it?
3. **Cells:** do the about 10 full-protocol shapes register as ordinary `bench-result/v1` cells through `bench.cell` (C-interactive, statement `{shape id}+frame-v3-sha512/hm96-sha512`), or stay in the sweep's own view? They're not census subcircuits.
4. **A dry-run Attempt already reached the shared store:** `r20260928-003556-80b7`, campaign `backend-sweep-dryrun`. It was a CPU run of one #101 shape, accepted with 31 of 31 selftest cases. I ran it on a cloud VM whose environment carries the R2 secrets, and the CLI published it with "PRESERVED on the remote". Label or supersede it as you see fit; its result.json predates the contract fix and shows `invalid`.

**Money and pods:** the sweep has its own $100 line. The pods are prefixed `vyb-`, under one guard with a deadline, and I'll give Daniel the prefix and deadline before launch.
