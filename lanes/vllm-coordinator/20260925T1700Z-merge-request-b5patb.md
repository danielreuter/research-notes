---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Merge request: b5patb, split `observe/fold/patterns.py` (B5, pure structure), from vLLM coordinator bc-ecac3029, 17:00Z

- **Merge:** `lane/vllm-rf-b5patb` @ **`4537961b`**, `--no-ff`. Two commits on `33e4d8d1`: `695bd4c2` splits the module;
  `4537961b` adds fp8 and the TP collectives to the package. Successor b5patc made no commits.
- **Main since:** `2603dfcc` (PR #27) touches only `backends/numerical`, so the check below holds at `2603dfcc` too.
- **Recheck against main `38a8d35d`** (b2vb, b5gmb and c2b already merged): no conflict. The allowlists (p08, p09, p10,
  p11) and the README auto-merge. On the merged tree, every ratchet lint runnable without pytest passes (37/37).
  b5patb shares no code file with main since its base.
- **Gates:**
  - lints: 45 passed at head `ba852261`, at base `10996616` and at rebased `4537961b`;
  - gate (b), same pod: `ba852261` against `10996616`, 4001 = 4001, 0 changes (`r20260925-122258-1b8d`);
  - rebased `4537961b` (`r20260925-142622-edbe`): one flip, `tests.commit.test_roundtrip::test_transient_storage_is_released`.
    Isolated reruns pass 5/5 at head and 5/5 at base (`r20260925-163223-81eb`), so it's unstable. It's in c1's area, and
    b1 saw the same flip;
  - gate (a) T0+T1 at `ba852261` (`r20260925-122214-cc3f`): 73 passed / 85 skipped, 158 = 158 against a23b's base, with no
    outcome change. The only flags are the two known skip rewordings. Custody `art:f1229b6c…`.
- **Acceptance:** the #101 re-fold (`r20260925-141717-7caf`) gives fold digest `cc48449d…` at head = base = record.
  `program.json` and `instances.jsonl` are byte-identical head against base.
- **Invariants:** no Program, manifest, commitment root, leaf id or verdict change. `code_identity` moves from
  `3809d208…` to `e82dbc8b…` (allowed). The P10 entries drop from 76 to 75; no allowlist grew.
- **Evidence:** `lanes/vllm-rf-b5patc/READY.md`, `lanes/vllm-rf-b5patb/` and the handoff
  `lanes/vllm-coordinator/20260925T1642Z-handoff-from-vllm-rf-b5patc.md`. The big pod is terminated; the cpu pod went to b1c.
