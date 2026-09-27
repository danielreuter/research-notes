---
cursor:
  subagentId: "bc-f382702c-2731-5be2-bba6-570cfb945abe"
---

# Handoff from terminology: merge request for #43, then #45 (a labelled Table 2 header change; re-record the parity baseline after it)

lane: terminology · kind: handoff (merge request) · from: terminology (agent bc-f382702c) · to: research coordinator (bc-8ece7cde) · created: 2026-09-26T02:25Z · supersedes `20260926T0145Z-handoff-from-terminology.md`

## Merge, in this order

1. **[#43](https://github.com/danielreuter/verity/pull/43)**, `cursor/terminology-glossary-5abe` @ `122758b3`. It contains origin/main `a57628fc` (#44 and #41 included) and merges cleanly.
   - The README Glossary and the `AGENTS.md` rule.
   - The prose rollout: A-GKR/B-Ligero; backend, statement; subcircuit; input and input set.
   - `verity.ir.Subcircuit` → `GateSelection` with no alias, including `Circuit.gate_selection()` and sampled_proofs' `Obligation.selection`. The Obligation JSON key `subcircuit` and the typed-obligation `Subcircuit` are serialized, so they stay.
   - Follow-ups for the files that #36 and #41 merged. `backends/gkr/PROTOCOL.md` is now titled "A-GKR".
   - No behaviour change.
2. **[#45](https://github.com/danielreuter/verity/pull/45)**, `cursor/table2-family-headers-5abe` @ `d9c77bb6`, stacked on #43 (its base is #43's branch, so retarget it to `main` after #43 merges). It also merges cleanly onto `a57628fc`.
   - It is a **labelled change to published renders**. Table 2's headers, Table 3's cell labels and Table 1's family rows print A-GKR, B-Ligero, C-Flock and D-SP1.
   - The entities' `column_labels` and `backend_families[].column` follow.
   - Column ids stay `SP1`/`Flock`, so `--parity` and `--format json` are unchanged. A test pins both halves, and there's a CHANGELOG entry.
   - **After merging it:** render `views --published`, which should differ only in those headers and labels. Re-record the parity baseline with `views --root $ST --parity --take-snapshot --record`, then label the render as the header change.

## Tests

- **#43:** the full suite at `b800d5a9` has the 9 failures `main` already has (`test_repository` ×2, `test_pythonpath` ×3, the evaluation kernel list, `test_pods_connect`, `test_store_honing`, `test_telemetry`), with 2,145 passed. At the head `122758b3`, the numerical, core, protocols, Flock and `tests/` suites give 1,664 passed, with only 3 of those 9 failing there. The vLLM tests the rename touches also pass.
- **#45:** the bench suite plus `tests/` give 346 passed, with only the two `test_repository` size-cap failures.
- On a cloud VM, set `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false`, or `test_notes_sync` hangs on the VM's commit signer.

## Settled since 01:45Z (Daniel's answers)

- `instance_set(s)` in the census and entities: #44 renamed them, and it has merged. The Glossary no longer lists them as kept.
- The Table 2 headers are #45.
- `verity.ir.Subcircuit` is now `GateSelection` (in #43).

## Left, with the reason

- **#30 and #34 both merged at earlier heads, but their branches have kept moving.** #30 has 8 new commits and #34 has 14, touching 20 Flock files between them: `live/src/{gpu,lib,pure_block}.rs`, `bin/flock-pure*.rs`, `verity_flock/{backend,bench,instances,register,negatives}.py`, `pod/22-pure-gpu.sh`, `pod/30-cell.sh` and `tests/test_backend.py`. I left those files, so as not to conflict with that live work; they need the same follow-up once those commits land.
- **#42 (the vLLM exporter)** is still open. I'm subscribed to it.
- **The pinned Flock lowering sources stay unedited permanently**, because `verity_flock/backend.py` hashes their bytes: `verity_flock/{lowering,unit,unit_fp4,gf2}.py` and `verity_unit.rs`. The same goes for `backends/gkr/verifier/pins.txt`.
- **`views.py` on `main` has gained new prose that uses "configuration"**, from #41's `a57628fc` ("Flock over vllm-v1 is its own configuration"). From now on, the `AGENTS.md` rule is how lanes keep new prose in the Glossary's terms.
- **The owner notes** are in `20260926T0022Z-handoff-from-terminology-pr-owner-notes.md` in this folder (updated 01:40Z). Please forward them to #42's owner, and to #30's and #34's for their live commits.

## Update 02:40Z

- **#43 is merged** (`ee6510c4`), and so is #42.
- **[#45](https://github.com/danielreuter/verity/pull/45) is retargeted to `main`**, at `8d9d21f7`. It contains `c79005af` and merges cleanly.
  - Since `26dfb753` retired the markdown tables, what #45 changes for readers is two fields of the published entities: `table2.column_labels` and `backend_families[].column`. Both are now C-Flock and D-SP1.
  - Label the next `<stamp>-tables.json` as that change. The parity gate is unaffected.
- **New: [#50](https://github.com/danielreuter/verity/pull/50)**, `cursor/terminology-vu-export-5abe` @ `e79fecd2`. It's the follow-up for #42's exporter: prose only ("input sets"), plus the `vllm-vu-set/v1` kind's description. Please merge it too.
- **Still left:** the Flock files with unmerged commits on #30 and #34.
