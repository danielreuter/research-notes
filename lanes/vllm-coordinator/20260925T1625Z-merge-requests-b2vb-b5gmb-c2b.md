---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Merge requests: b2vb, b5gmb, c2b (pre-epoch), from vLLM coordinator bc-ecac3029, 2026-09-25 16:25Z

Merge all three into `main`, each `--no-ff`, in any order. Every evidence path is relative to
`/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lanes/`.

## Recheck against current main `239c0e28` (16:20Z)
- Since `33e4d8d1` (a4), main has c1 (`8b3537d5`, `integrations/vllm`), then only `backends/`, `tools/research` and the
  reverify-tile-2 merge. The lanes' gates ran against a4's tree, and c1 is the only intervening change inside
  `integrations/vllm`.
- `git merge --no-ff` onto `239c0e28` in a scratch worktree (nothing pushed): each branch alone, and all three stacked.
  **No conflict in any combination.**
- P10 size ratchet (`tests/lint/test_p10_size.py`, all 3 tests): **pass** on main alone, on main plus each branch, and on
  all three stacked.
- Every other ratchet lint in `integrations/vllm/tests/lint/` on the stacked tree: **37/37 pass**. `test_ratchet.py`
  couldn't run (it needs pytest, which this VM lacks). The three branches auto-merge into the same allowlist JSONs
  (P07, P09, P10, P11), and the lints hold on the merged result.
- Overlap with c1: b2vb and c1 both edit `pipeline/commit.py`, in separate hunks about 550 lines apart. b5gmb and c2b touch
  allowlist JSONs only in common with c1.

## 1. b2vb: one verdict and `properties/` records (SYNTHESIS §6 B2, verdict part)
- **Merge:** `lane/vllm-rf-b2vb` @ **`ed8f6625`**, 10 commits, 48 files, all under `integrations/vllm`, +1,889/−1,400.
  Rebased onto `33e4d8d1` from `8d847755`. `git diff 8d847755 ed8f6625 -- integrations/vllm packages/verity` is empty,
  so the evidence carries over.
- **Gates:**
  - lints 45/45;
  - gate (b), head against base on one pod: no new failure, skip or skip reason; 15 new tests pass;
  - gate (a) T0+T1: 73 passed / 85 skipped, test by test as a23b's base (`r20260925-105008-bca1`).
- **Acceptance:**
  - The verdict JSON is byte-identical at base and head for the 10 rows with a Commit record.
  - #101 (world 1) equals the record: program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`, PASS.
  - #70 (world 2) equals the record (tp run root `0b91229f…`, FAIL), and 32/32 Commit fields equal f1's base Commit of
    record.
  - The non-interference records `be83f678…` (world 1) and `442979b3…` (world 2) recompute from the rows' own Match
    arms. Worlds 3 and 4 are refused.
- **Behaviour change:** one, unreachable today. A frozen gate reporting a status outside pass/fail/skipped made the Match
  verdict ACCEPTED before, and makes it INCOMPLETE now. No frozen gate returns such a status.
- **Custody:** the run record is `art:b250b632…` (207 files, preserved). All pods are terminated; about $13.1 of $30 spent.
- **Evidence:** `vllm-rf-b2vb/READY.md`, `vllm-rf-b2vb/evidence/` and `vllm-rf-b2v/evidence/`.
- **Found, not fixed:** the TP Commit writes no `commit/verdict.json`, so `from_record` gives INSUFFICIENT_EVIDENCE on TP
  rows (a5's area).

## 2. b5gmb: split `check/match/global_match.py` (B5, pure structure)
- **Merge:** `lane/vllm-rf-b5gmb` @ **`03e7b182`**, one commit on `33e4d8d1`. It's the rebase of the gated `55b9d1ff` (on
  `10996616`). `git diff 55b9d1ff 03e7b182 -- integrations/vllm packages/verity` is empty.
- **The change:** `global_match.py` goes from 2,206 to 416 lines, and `_check` from 1,227 to 116. Its three P10 entries are
  deleted; the other allowlist entries moved with their code, and none grew. `global_match_fast.py` is untouched.
- **Gates:**
  - lints 45/45;
  - gate (b), same pod: 4,001 = 4,001, no test on one side only, no outcome change;
  - gate (a) T0+T1 (`r20260925-105053-df3a`): identical to a4's run at the base, and 158/158 against a23b's base (only the
    two skip rewordings a4 reported).
- **Acceptance:** GM-01 on row #23 over two base/head pairs on one pod. Every output is byte-identical apart from timings
  (the global program sha `e5c5afba…` in all four runs). Wall time is +3.6% on the mean and CPU time −0.05%.
- **Open question (reviewer's call):** the P09 module-cycle entry keeps its count, but its member list now names the new
  modules. The lint says "a cycle that gains a member fails too", and it passes on the merged tree. If the member list
  counts as allowlist growth, the fix is to pass `batch_decomp`/`program_compare` through `MatchRun`, or to cut
  GMF→GM. Both are outside a pure split.
- **Evidence:** `vllm-rf-b5gmb/READY.md`, and `vllm-rf-b5gm/evidence/` for GM-01 and the code digests. Pods are terminated;
  about $9.2 of $15 spent.

## 3. c2b: Definition library, **only up to `4d053f01`**
- **Merge:** `4d053f01` (`lane/vllm-rf-c2b`, c2's `5e21eead`), 4 commits on `33e4d8d1`. **Don't take the tip
  `dedf5313`:** it's the re-baseline epoch (Ampere k16 step v1→v2). It moves the Program digests of the 10 L40S rows,
  and leaves `test_golden` red until the golden corpus is re-recorded. It waits for the epoch (owner decision 4).
- **The change:**
  - the registry cites core `verity.ml` for its duplicated Definitions;
  - P1 reads `@composite` ids;
  - 18 scalar primitives move to core `verity.ml.scalar` under the same ids;
  - the E4M3 cast and the Hopper E4M3 dot move to core `verity.ml.prims`.
  All are digest-neutral: a primitive's encoding is its id, params and ret.
- **Gates at `5e21eead`:**
  - lints 45/45;
  - gate (b), same pod: 0 new failures or skips, 2 new tests;
  - gate (a) T0+T1 (`r20260925-105303-d711`): identical to a4's head, and 158/158 against a23b's base. Run record
    `art:6b5ef88e…`, preserved.
- **Evaluator equality before each move:** exhaustive (2^32) where feasible, 1–100 M samples elsewhere, 0 differences. The
  encodings of all 20 moved primitives, 36 Program digests, and 16,141 definition closures over all 12 program-bearing
  rows are identical at base and head. #101 head = base = record.
- **Code-identity pins move:** `registry_version` `beb5d5f7…` → `e183ae76…`, `ref_vocab_digest` `63c73b5e…` →
  `afb8df06…`, `REFERENCE_CPU_F32` `f955cb18…` → `a05926da…`. These are expected.
- **Evidence:** `vllm-rf-c2b/READY.md`, including the inventory of borderline Definitions left in the integration
  (item 2 of the owner's morning list), and c2's `evidence/`. Pods are terminated; about $11.4 of $25 spent.

## Coming next (not yet requested)
- c4ir `793f14af`, after c4irc's gate (a), expected about 10:15 AM PT.
- b5patb `4537961b` and b4b `5c05ff6d`, after their successors finish.
