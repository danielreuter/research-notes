---
id: 20261001T1137Z-handoff-from-circuits-build-speed-671-ready
campaign: circuits-build-speed
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-build-speed (bc-d2d56312-a75e-56c6-a829-45a5135a3752)
---

4:37 AM PDT: [#671](https://github.com/danielreuter/verity/pull/671) (`cursor/build-speed-word-groups-3752` @ b9e061877) is ready (`research queue ready 671`) and needs the vLLM grant. It changes only `query/word.py`, plus a new test: `call_groups`' check that every read of a Call is committed or a literal's output becomes a numpy pass over the columnar read columns. The Python expression stays as the fallback.

- **B1 4096/512 manifest, on top of #665, warm rules:** wall 1,170.5 s to 875.4 s, CPU 700.9 s to 562.5 s; `manifest.json` is byte-identical (r20261001-111223-2652 vs r20261001-111241-0acc).
- **Reference row:** digests, `manifest.json` and `strict_word.json` are byte-identical; there's no wall difference under load (r20261001-095723-c452 vs r20261001-095728-e13d).
- **The unit-rule cache:** editing `word.py` changes the cache key, so each host re-cuts its unit rules once (4k row: 2,849.7 s). 68 commits to `main` in the past week did the same.
- **Tests:** the new test file has 12 cases; merged with `main`, it and two other query test files give 53 passed. The full suite failed only the Qwen TP2 row of `test_tp_moe_members`, which the VM OOM-killed; its OLMoE row passed. I didn't run the Qwen row alone (the VM is shared), so `check` will run it.

It merges cleanly with `main`, #658 and #665, and touches no file they touch. It's independent of both. If there's no train room before 7:50 AM, close it and keep the branch.
