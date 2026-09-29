---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: red team (M0 statement review), via the research coordinator
created: 2026-09-28T08:30Z
---

# Proposal, not built: raise `verity/flock-circuit`'s block limit from 2^26 to 2^27 bits, so M0 attention reaches T = 171–287

Daniel asked for this write-up. Nothing is built or merged.

## Why

- **#101's attention serves T = 1–287,** with 16 VUs at each T.
- **One instance per block.** An M0 attention instance (one T, G = 1) is its tensor-core units, the SHA-512 row compressions,
  the hm96 slots, the tail stages and one lookup slot per ex2 read. All of them grow with T.
- **Where it stops fitting:** composed at `main` `3ba4d8b3`, it fits a 2^26-bit block up to **T = 170** (`k_log` 26 at T = 128,
  129, 160 and 168–170). At **T ≥ 171** it needs 2^27, and the writer refuses it (`circuit.py` `K_MAX = 26`: "an instance needs
  a block of 2^27 bits").
- **What that leaves uncovered:** 117 of #101's 287 key-count values, T = 171–287. That's c2's upper half and all of c3.

## The change

1. **The writer:** `backends/flock/python/verity_flock/circuit.py` `K_MAX = 26` → `27`. That's one constant. `compose` picks
   the smallest block that fits, so every circuit that fits today keeps its `k_log`, its bytes and its pin. Only new
   circuits, T ≥ 171, get `k_log = 27`.
2. **Nothing else in the statement's code changes:**
   - **Rust verifier** (`live/src/circuit.rs`): `Composite::parse` takes `k_log` from META. It checks only each range's
     alignment and fit (`r.start() + span > 1 << self.k_log`, in `usize`) and has no upper bound. `Stmt::new` sizes
     everything from `k_log + nbl` in `usize`.
   - **Lean verifier** (`Flock/Circuit.lean`): `kLog : Nat` from META, with the same alignment and fit check against
     `2 ^ c.kLog`. There's no bound.
   - **GPU prover** (`cuda/prove_circuit.cuh`): block sizes and range checks are `long long` (`1LL << k_log`,
     `(long long)(…) << type_log`). A 16-instance point at `k_log` 27 is `m = 31`. M0 has already proved `m = 34` statements
     (A4, GEMM, 923 drawn instances).

## What I'd ask you to check

1. **That the relation is only a size change.** It's the same row type, regions, Δ copies, lookup slots and bindings, over a
   block twice as long. Does any grant, lemma or pinned theorem assume `k_log ≤ 26`?
   - the soundness stack's `Model/Statement.lean`;
   - level 3's fold lemmas (`LookupFold`, `FoldStmt`), `foldB_get`;
   - the Lean verifier's `lean-audit` pinned statements.
2. **Security per proof at `m` up to 31–32.** `flock-128-r2`'s per-rep and per-proof figures (−97.8 per rep; the union bound
   over sub-batches) are stated for the profile's code parameters. Do they hold unchanged at the larger `m`? They did at A4's
   `m = 34`, but please confirm the profile table covers it.
3. **Memory and time.** They double per instance. That's performance, not soundness, but it bounds the cell sizes a pod can
   hold.
4. **Nothing moves for existing pins.** T ≤ 170 circuits, GEMM and every other template keep their block sizes, so no
   existing pin changes.

## Alternatives, if you'd rather not raise the limit

- **Inline the tail's table reads** instead of lookup slots. That's #192's inline path plus #195's constant-bit drop: about
  27k rows per ex2 read against a 2^16 slot. It buys some range, but not T = 287.
- **Split a T ≥ 171 head across two blocks.** That's a larger statement change, with cross-block wires, and I don't recommend
  it.

**Coverage if granted:** M0 could then record T = 171–287 as further class cells, under the same driver (#261).

## Update 08:50Z: the red team's review, and the plan for the next window

Review: `private/red-team-reviews/m0-statement/block-limit-2-27.md`.

**The verdict:** not as a one-constant change. The pinned table-soundness theorems take `Stmt.InRange`
(`soundness/FlockSoundness/Accounting/Fast100.lean:264`: `kLog ≤ 26 ∧ nRegions ≤ 1024 ∧ mPts ≤ 64`). The spec and the GPU
guard assume `k_log ≤ 26` too. My "nothing else changes" was wrong on those three points.

The security change is about 0.0002 bits: `kLog` enters `piopError` only through `piopNumMax`'s bound, which goes from 20 to
21. So the review would grant the change once these steps land. None of it is for this window.

| # | Step | Owner | Gate |
|---|---|---|---|
| 1 | Extend `Stmt.InRange` to `kLog ≤ 27`, with `piopNumMax`'s 20 becoming 21 (`Fast100.lean:267`). Re-prove `table_sound_fast100` and `table_sound_fast100_34_35` and their `_exec` forms, then `Instance.lean`, `Audit/Flock.lean` (`hshape`), `SoundnessPad.lean` and the padded numbers. | flock-soundness (bc-9e538dc5), when free; requested in `20260928T0850Z-note-to-flock-soundness-from-flock-netlist-m0-inrange-27.md` | the red team reviews the four re-pinned theorems' read records |
| 2 | `backends/flock/verifier/PROTOCOL.md` §16.5 (line 1002) goes from "`k_log ≤ 26`" to "`k_log ≤ 27`" (and `m > 35` stays rejected). | M0, with the verifier lane (bc-8e519ca0) | same PR as 3–5 |
| 3 | `cuda/prove_circuit.cuh` `fc_bad_shape` (line 193): `k_log > 26` becomes `k_log > 27`. Then a GPU `selftest` at a `k_log = 27` point: attention T = 171, 16 instances, `m = 31`. | M0 | next GPU window (a same-DC pair, or the selftest on one L40S) |
| 4 | Enforce the proved range at parse time, recommended even without 1–3. The Rust `Composite::parse` and the Lean `Circuit.parse` refuse `k_log > K`, more than 1,024 regions, `m_pts > 64`, or `m > 35`, so that "accepted" implies "covered by the pins". | M0 (Rust), the verifier lane (Lean) | red team; a negative test each side |
| 5 | Only then, `circuit.py` `K_MAX = 26` → 27. | M0 | after 1–4 |

**Also:**

- **`verifier/transcript_check.py`'s `cap=1 << 26`:** check that no proof vector exceeds 2^26 entries at `m = 31–32`. It's
  a tool, not the verifier of record.
- **`flock-128-r2`'s per-proof figure:** recompute it at each cell's own `m`, as at A4's `m = 34`.
- **M1's padded (ZK) numbers** cover only `m = 25–27` (`padTableError_le_m1`). That's already true at today's `k_log = 26`,
  and M0's attention cells are `NON_ZK_PROOF`, so it's out of scope here.

**The backend sweep:** with steps 1–5, `k_log = 27` also reaches its classes above 2^26 (the stress test's `K_MAX`
question). Step 4 is worth landing first on its own, because today the writer is the only guard.

## Update 10:37Z: step 1 is granted; the change set for the next window

- **Soundness no longer blocks.** The red team granted #271 (`Stmt.InRange` to `kLog ≤ 27`, re-proved).
- **A correction to its earlier review:** the Lean verifier already refuses `k_log > 26` at setup. So the Lean verifier
  isn't "no bound" as I wrote on 08:30Z; it moves with the rest.
- **Step 4's Rust half** is #268: parse-time `Stmt.InRange`, with the research coordinator.

**Everything below moves to 27 together, in one PR or one train.** Nothing is built yet; it's for the next window.

| Where | Today (`main`) | Owner |
|---|---|---|
| Lean `Flock/Statement.lean:158` (`Stmt.setup`) | `if c.kLog > 26 \|\| m > 35 then throw …` | verifier lane (bc-8e519ca0) |
| Lean `Flock/HmRow.lean:755` (`setupH`) | the same line | verifier lane |
| #267's parse-time range constant (the Lean half of step 4) | 26 | verifier lane |
| `backends/flock/verifier/PROTOCOL.md` §16.5 (line ~1002) | "`k_log ≤ 26`, `m = k_log + nbl`; the spec rejects `m > 35`" | M0, with the verifier lane |
| `backends/flock/cuda/prove_circuit.cuh:193` `fc_bad_shape` | `k_log > 26` | M0 |
| #268's `IN_RANGE_K_LOG` (`live/src/circuit.rs`) | 26 | M0 |
| `backends/flock/python/verity_flock/circuit.py` `K_MAX` | 26 | M0 |

**What doesn't change:** `m > 35` stays rejected everywhere, and the regions (1,024) and `m_pts` (64) bounds are unchanged.

**The gates, in order:**

1. #268 and #267 on `main`, so the bound is enforced on both sides.
2. The one PR above, reviewed by the red team as a statement change: the spec text, and the identical bound in all three
   verifier places.
3. `flock-circuit selftest` at a `k_log = 27` point on CPU (attention T = 171, 16 instances), plus `selftest --gpu` on one
   L40S, when pods allow.
4. Only then, any cell at T ≥ 171.

**Checks to run with it:**

- `verifier/transcript_check.py`'s `cap=1 << 26` against proof vectors at `m = 31–32`;
- the per-proof figure re-derived at each cell's own `m`, as at A4.
