---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: coordinator · kind: merge-request · from: vllm-epoch-run (bc-75fd4007) · to: research coordinator (bc-8ece7cde); cc vllm-coordinator (bc-ecac3029) · created: 2026-09-30T02:25Z · repo: danielreuter/verity · about:
- [#439](https://github.com/danielreuter/verity/pull/439) `cursor/lift-expected-class-label-2622` at **`df3859135109166f080ee28bdeead976060aa5c2`**, on main `62ce91fa`.

# Merge request: lift_expected takes a row's class from its newest `class` label by daniel, else INDEX.json (#439)

**Why:** in the follow-up epoch, Daniel reclassified #4 (SmolLM2-135M B16) from FAIL to GREEN (2026-09-29T20:12Z, via root). `lift_expected.py` regenerates `fixtures.toml`'s class from the vault's INDEX.json, so a regeneration would set #4 back to FAIL. As the vLLM coordinator asked (`lanes/vllm-epoch-run/20260929T2033Z-answers-from-vllm-coordinator-67-68-and-4-label.md`), the decision is a store label: `art:7b437ce1…`, #4's record of record, carries `class=GREEN` by `daniel`, ref `r20260929-194627-4b5f`, on the remote. The generator now reads that label. The expected write that set the class by hand is `45b9125c`, on `cursor/followup-epoch-expected-2622`.

**What changes:**
- `integrations/vllm/tests/regression/store_io.py`: `class_label(row)`, the newest `class` label by `daniel` on the row's `fixture/v1` trees with meta `role=record` and `row_id=<row>`. It reads the remote's assertions too (`labels --remote`), and falls back to local.
- `integrations/vllm/tests/regression/lift_expected.py`: `build_fixtures(class_labels=…)`. A label's value wins over the index, and every row states `class_source` (the label, `INDEX.json`, or `carried`). `class_labels_for` uses `reachable(need_remote=False)`, because a label is read from a local store too; main's `reachable()` now wants a remote by default.
- `integrations/vllm/tests/regression/test_class_label.py` (new) uses a stand-in vault with #4 as FAIL, in a tmp store with no remote and an empty `HOME`, with `CHECK_STORE_CUSTODY` dropped. A label by daniel gives GREEN; no label, or a label by anyone else, gives FAIL. Passes under `VERITY_STORE_REQUIRED=1` too.
- `research.store.vocab`: a new key, `class` (verification, enum GREEN | FAIL), and the store README's list and `test_store_vocab.py` to match.

**Check:** recorded as **`r20260930-001826-f228`** on `vy-coord-t1` (an existing train pod, not a new one), at `df385913`. It **passed** in 6,746 s: pytest (4,233 passed, 318 skipped, 22 xfailed, 3 xpassed), circuit-check, flock-circuit-build, lean-build, lean-unit-cut, lean-audit and lean-suites; lean-agreement skipped, since nothing under `backends/flock/` changed. Custody is preserved; the run record is `art:3f2d8b47…`.

Most of the 1 h 52 min pytest wall is `integrations/vllm`'s `test_the_stored_tp2_moe_builds`, which is on main. Its qwen3-30b-a3b rank builds took about an hour per case at one core.

**Main moved:** main is now `2de43718`, 42 commits past the `62ce91fa` this was checked on, so `research merge` of this exact head will refuse. `git merge-tree` onto `2de43718` is clean (no conflicts; main touched the store README and some `expected/` files). This fits any train. Tell me if you want me to merge main and record again instead.

**Order:** independent of the other open PRs. It touches only the four vLLM regression files above and the three `research.store` vocabulary files.
