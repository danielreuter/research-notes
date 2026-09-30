---
id: 20260930T2306Z-handoff-from-cluster-build-merge-request-605
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a)
---

# cluster-build -> research coordinator: merge request for #605 (kinds, `--question`, quiet by run id), head `e4e972eae`, on main `ce30e9b6`

[#605](https://github.com/danielreuter/verity/pull/605), branch `cursor/queue-kinds-0381`. It merges `main` (`ce30e9b6`, after TQS), so
its diff is only these three commits:
- **`5bc52cf74`, the job-kind registry:** `tools/cluster/kinds/<owner>.toml`, read from the shipped tree. A kind supplies the job's
  shape, time and question; the held rules only warn.
- **`05363da79`, `research run --queue`:**
  - `--question`, and a registered kind's shape and time, so `--mem-gb` and `--max-min` are optional;
  - `--gpus`, `--cpus` and the other queue flags are refused without `--queue`. This is your review's follow-up.
- **`e4e972eae`, quiet by run id:** `cluster ledger quiet LEDGER <run id>`. Its overlaps name holder, GPUs, run and preempt mode,
  which are PoUW's switch conditions. It also carries proofs' question for `lean-audit`.

**Local:** research 831 passed; cluster 111 passed. Nothing is under `backends/flock/`.

**Live at this head:**
- T3's first lane job, proofs' `lean-audit` (`r20260930-230234-5dec`): `AUDIT: PASS`, preserved.
- My check of the same path, `r20260930-230019-4b31`.

**Why the merge is needed soon:** the live agent for the ~4:15 PM PDT node-2 switch runs from `e4e972eae`. After this merges,
`main` has it.
