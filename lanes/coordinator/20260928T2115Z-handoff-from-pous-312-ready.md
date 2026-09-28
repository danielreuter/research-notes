---
id: 20260928T2115Z-handoff-from-pous-312-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# #312 (the POUS vLLM protocol option) is ready on #311's final head: please land it right after #311

Follow-up to `20260928T1950Z-handoff-from-pous-311-ready`. From bc-13eada34, the POUS lane.

- **PR:** https://github.com/danielreuter/verity/pull/312, branch `cursor/vllm-pous-option-c934`, head `7f888b0e`, marked
  ready for review. It is stacked on #311: its base is `cursor/vllm-protocol-composition-9924`.
- **#311's final head `69153d43` is merged in** (`cda724e9`), with no conflicts.
- **It also carries #208** (`85912edd`, `verity_pous.protocol` and `schemes`), merged in until #208 lands. Land #208
  first or together; #208 is green on `main` and ready, per `20260928T1715Z-handoff-from-pous-208-ready`.
- **Its own change over #311 and #208** is under `integrations/vllm/`: `verity_vllm/protocol_options/pous.py`,
  `tests/protocol_options/test_pous_option.py`, and the `verity-pous` dependency in `pyproject.toml` and the root
  `uv.lock` (two lines). It adds no circuits, no Definitions and no Lean.
- **check:** `r20260928-202058-deb4` on `7f888b0e`, PASSED: pytest, circuit-check, lean-build, lean-unit-cut and lean-audit;
  lean-agreement is skipped because no bundle was sent. The attempt before it on this head, `r20260928-194952-6d3c`,
  failed only on the clock-dependent `tools/research/tests/test_notes.py` relaunch test, which #322 fixes.
- **The vLLM tests:** `check` doesn't collect them. On the CPU, `tests/protocol_options` (43, #311's included),
  `tests/lint`, the by-name, dead-module and import checks and `tests/engine/test_hooks.py` pass. POUS's adapter tests
  need no torch, since they use a toy model.
- **Default path:** unchanged. With no protocols enabled, `pous.py` is never imported.
- **Placeholder security:** linears only; the reference codec on the CPU; an in-process responder; TP refused. Whether
  the embedding and tied head are encoded too is open question 5 for Daniel. A Commit with `pous` on writes
  `of_record = false`.
- **Merge:** `research merge cursor/vllm-pous-option-c934` after #311.
- **Statement reviewer:** none needed.
- **After the vLLM verdict (21:15Z, GO with conditions):** #311 will be rebased over D3′ and gain the default-path CPU test; #312 then merges #311's new head and re-runs `check`, and a follow-up note gives the new head and run id. Please merge only after that.
