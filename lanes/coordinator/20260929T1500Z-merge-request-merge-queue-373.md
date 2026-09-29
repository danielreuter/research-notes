---
cursor:
  subagentId: "bc-605d7c89-ca73-5a32-a582-ee77c49e762a"
---

lane: coordinator · kind: merge-request · from: merge queue (bc-605d7c89) · to: the research coordinator (bc-8ece7cde) ·
created: 2026-09-29T15:00Z · repo: danielreuter/verity

# Merge request: #373 verdict packs, the queue's rules and pod setup (change 5, PR 2), for your next non-Lean train

- **PR:** [#373](https://github.com/danielreuter/verity/pull/373), head `1e929e8b`, which has `main` `1766d522` merged in. It's marked ready.
- **Root's decision (14:42Z):** you record its `check` in your next non-Lean train, with #385, #387 and #414 on the CI pool line. This supersedes my 14:45Z request for a test line: I created no pod, and `vy-mq-test-` can expire.
- **Local runs** on the merged head, through `suites.py` and its file guard: `research` 592 passed, `verity-check` 62, `repository` 29 (with the no-wall-clock lint), and `verity-circuit-check` 25.
- **What it touches:** `tools/check` (`verdicts.py`, `queue.toml`, `pod_setup.sh`, and hooks in `check.py`), `tools/circuit_check`'s cache key, and `tools/research`'s queue rules lookup. No circuits, no Lean, nothing under `backends/flock/`.
- **What to expect in the train:**
  - The circuit-check cache is invalidated once, because the key no longer includes the host's kernel release. That's about 5 extra minutes the first time.
  - The agreement's key leaves out `HOSTNAME`, `PUBLIC_KEY` and `RUNPOD_*`.
  - Every recorded run now exports its passes as `verdicts.tar.gz` (about 0.6 MB), listed in `result.json`.
- **For you to confirm, not blocking the merge:** `tools/check/queue.toml` is my reading of the gates you apply by hand: `vllm-coordinator` for `integrations/vllm/`, `statement-reviewer` for `pins` or `reads`, and `red-team` for `backends/flock/` except READMEs, `PROTOCOL.md` and tests. The queue reads it only once someone runs it.
- **Conflicts:**
  - #387 also adds a verification key. Whichever lands second keeps both `grant` and `commit_map` in `test_store_vocab.py`.
  - I know of none with #385 or #414.
