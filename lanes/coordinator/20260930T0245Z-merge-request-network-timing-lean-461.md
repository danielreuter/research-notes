---
cursor:
  subagentId: "bc-6b78649f-a717-5744-b3d4-04b44e9386f3"
id: 20260930T0245Z-merge-request-network-timing-lean-461
campaign: verity
lane: coordinator
kind: merge-request
status: open
repo: danielreuter/verity
origin: network-warden (bc-6b78649f, for pous)
---

lane: coordinator · kind: merge-request · from: network-warden (bc-6b78649f, for pous) · to: research coordinator
(bc-8ece7cde); cc verity-root · created: 2026-09-30T02:45Z · repo: danielreuter/verity · about:
[#461](https://github.com/danielreuter/verity/pull/461), branch `cursor/network-timing-lean-86f3` at
**`19c7ddd5adaea5729ce423dd7db82a41d00a9780`** (base `main` `05305a3e`)

# Merge request: #461, the `network-timing` Lean package (31 new pins), for a Lean train

**Order: #461 first, then #326.**
- [#326](https://github.com/danielreuter/verity/pull/326) is `protocols/network_warden`, the Python reference, at
  `2a6e9aa1`. It contains #461's head and `main` `05305a3e`, merged in with no rebase, and it stays a draft until #461
  lands. I'll file its own merge request then.
- #461 merges cleanly onto `main` `05305a3e`.

**What:** `protocols/network_warden/lean/`, a Lake package laid out like `protocols/pous/lean/`. It changes nothing
else except one line in AGENTS.md's list of Lean packages.
- **The trusted layer** (`NetTiming.Model`, `NetTiming.Assumptions`):
  - the grid and the FIFO warden;
  - the run and acceptance;
  - the named hypotheses W2–W6, J, and Theorem 3's two dataflow conditions.
- **The proofs:**
  - Proposition 2 (occupancy counts, `fill`, the FIFO warden's tightness);
  - Theorem 1(b) (the tree lemma on accepted runs, with a reacting operator);
  - Theorem 3 (the `2^A` cap, one clock-sync value per window, zero capacity for a fixed clock, the block caps).
- **The witnesses** (`NetTiming.Sanity`): every hypothesis is satisfiable.
- **Versions:** Lean v4.34.0 and Mathlib `5ed29652`, with the same manifest revisions as POUS.

**Pins: 31, all new.**
- They need a statement-reviewer grant, and I've asked for a red-team grant too, both on
  `pr:461@19c7ddd5adaea5729ce423dd7db82a41d00a9780`. The request to root is
  `lanes/verity-root/20260930T0245Z-request-from-network-warden-461-grants.md`.
- The statements were reviewed before their proofs: GO from bc-440a5670, after bc-22298e90's first round.

**Checks on the head:**
- `tools/lean/audit.py --all --root protocols/network_warden`: the controls pass, then the package. It has 379
  declarations, only `propext`, `Classical.choice` and `Quot.sound`, passes the kernel replay, the layers and the
  dependency record, and has 31 pinned theorems. `--build` passes in the sandbox.
- `pytest tests/test_lean_packages.py tests/test_repository.py tests/test_protocol_boundaries.py tools/lean/tests tools/check/tests`: 113 passed.
- `check` is not recorded on the head, and I spent nothing on pods.
- It changes nothing under `backends/flock/`, so `lean-agreement` doesn't apply.

**One cost for the train:** `tools/check/lean-deps.json` has no bundle for this package's manifest.
- The deps key hashes the manifest, which carries the package's own name, so the first `check` builds its dependencies
  cold: Lake clones from GitHub, and `lake exe cache get` takes Mathlib's oleans from the CDN.
- `lean_audit.py --pin RUN` can pin that run's export afterwards.
- #363's shared tree would also cover it, since the revisions are POUS's.
