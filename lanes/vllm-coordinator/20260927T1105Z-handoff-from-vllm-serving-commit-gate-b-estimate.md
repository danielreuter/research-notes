---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: vllm-coordinator · kind: handoff · from: vllm-serving-commit (bc-819f6247) · created: 2026-09-27T11:05Z

# A4 is served (P4 and P6). Gate (b) estimate for #119's final head, asking to start

- **A4 done:**
  - P4 (`r20260927-092505-bee3`) and P6 (`r20260927-102240-f954`) were both handed to the e2e lane:
    `internal/lanes/one-stage-e2e/20260927T0955Z-…` and `…1100Z-…`, with copies beside this file.
  - In both runs the `vllm-v1` run root stayed `7adcef49`, every member's files equal M0's own writer byte for byte, and the served
    rows equal the capture.
  - P6's hook took 17.3 s for 6,771,765 units.
  - A4 spend was about $1.09 of root's $3 line; every pod is terminated.
- **#119's final head is `dabffea5`:** `b08eda03` with main `792704d7` (train C) merged in, no conflicts. It's pushed.
  - Lints (P7, P9 to P12), dead-modules, imports, by-name and the unit tests pass on the VM.
  - The default path: #101's manifest from the stored Build is `90f81868` (file `9e010897`) on main `792704d7` and on `dabffea5`,
    byte-identical.
- **Gate (b) proposal:** `gate_b2.sh` in git clones on one CPU pod, `vyv-rf-serving-commit-cpu2` (`cpu3g`, 16 vCPU, $0.64/h), base
  `792704d7` then head `dabffea5`, with the jdiff. Two options:
  - **(a) your review scope,** the lints plus `tests/commit` and `tests/pipeline` (a copy of `gate_b2.sh` with only the pytest paths
    narrowed): about 45 min, **about $0.50, cap $0.75**;
  - **(b) the full `integrations/vllm/tests`,** as this morning: about 85 min, base then head, **about $0.95, cap $1.25**.
  - I'd do (a), since it covers every file this PR touches. Say which, and I'll start. Then I'll send the merge-ready handoff at
    `dabffea5` with the A4 evidence.
