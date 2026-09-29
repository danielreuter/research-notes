---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T02:05Z
---

# M0's cells: the attention input set re-registered, and the GEMM cell's `commit.seconds` recorded

For `internal/lanes/flock-netlist/20260928T0145Z-handoff-from-coordinator.md`. CPU only; no pod was used, so it cost $0.

## 1. The attention cell's input set

- **New id: `art:d4f9b1d68c316d1d875f97349377f445031081822198515ea1bba883a8529877`**, an `input-set/v1` preserved on the
  remote. It holds the same tree as `art:9551ba66`, byte for byte (fetched, `check_files` clean).
- **How:** registered through `bench.input_sets`' path (`InputSet.meta()`, then `research data put --kind input-set/v1 --tree
  … --preserve`).
- **Meta:**
  - `content_digest` `80ee77a62efa95aa7dbdc472bf3042e5ef8c71f4b30c797a492450b95b38cd80`;
  - `subcircuit` `attention-head/d64-bn128/sm80-fa2-bf16`, template `attention-head`;
  - `n` 16;
  - `manifest_sha256` `fde1442ab8f77c1c4a97d58520906390b1313790eebe1f3c95bde21adfeae8ad`;
  - `set`, `source` (synthetic), `schema`, `parameters`, `relation`, `seed` 101;
  - `key_counts` [129, 129];
  - `subset_of`: instances [0, 16) of the t129-256 set `art:82c591d1…` (content `48c2119d…`).
- **The cell's stamp matches:** `art:e352f2ad` names this content digest and `manifest_sha256`, so the renderer's lookup
  by digest finds the new set.
- **Label:** `art:9551ba66` is labelled `superseded_by` the new id (`--by flock-netlist`).

## 2. The GEMM cell's commitment time

- **New cell: `art:a1e58e3309f854c48454d96bc0ccf4d74a1975fc670446798399fae19b0cce34`**, a `bench-result/v1`, preserved.
  It supersedes `art:a83371c2`, which is labelled `superseded_by` it.
- **What changed:** the new document is `art:a83371c2`'s, byte for byte, apart from:
  - `commit.*` added;
  - `e2e.*` recomputed as `commit.seconds` plus the runs' `t.total`;
  - `derived_from.commit_run` added;
  - the registration text.

  `contract.validate` finds no problems.
- **Refs:** `run_files`, `input_set` (`art:123dc234`), `commit_result`, `commit_run_files`.

**The measurement:**

- **The work:** the serving hook (`verity_vllm.commit.serving_rows.commit`, `frame-v3-sha512` with `hm96-sha512/row/v1` row
  leaves, M0's format) commits the cell's own committed values afresh. That is the first 1,024 instances of `art:123dc234`:
  one x row and one w row per instance (2,048 rows of 4 KiB), and 1,024 output words.
- **The run:** `r20260928-015803-9be1`, tool `serving_commit_cost` at `33f057ec`, campaign `boolean-escape-hatch`,
  validation passed.
  - It ran on a 4-vCPU CPU VM, idle, with 4 workers.
  - The validation recomputes two rows per port against core's `hm96` commit string.

**The numbers:**

- `commit.seconds` **0.043 s**: the median of 5 warm calls;
- `commit.cold_seconds` 0.061 s (salts 0.003 s, leaves and trees 0.040 s);
- `e2e.seconds` 16.362 → 16.405 s, so 62.58 → 62.42 VU/s.

**The tool** is [PR #198](https://github.com/danielreuter/verity/pull/198), `benchmarks/commitments/serving_commit_cost.py`
plus its registry entry, into `main`.

## 3. The attention cell had no `commit.seconds` either: re-recorded (added 02:22Z)

`art:e352f2ad`'s measurements carried only the proof's `t.encoding_commitment`. With the input set fixed, the renderer's next
check ("commitment not timed") would have rejected it.

- **New cell: `art:c176e9c857ac959b1caebaea83f75081bff03b3696da289af0558ed0772e6093`**, a `bench-result/v1`, preserved. It
  supersedes `art:e352f2ad`, which is labelled `superseded_by` it.
- **What changed:** the document is `art:e352f2ad`'s, apart from:
  - `commit.*` added and `e2e.*` recomputed;
  - the stamp's input set `art` is now `art:d4f9b1d6`, with the content digest and `manifest_sha256` unchanged;
  - `derived_from.commit_run` added;
  - the registration text.

  `contract.validate` finds no problems.
- **Refs:** `run_files`, `input_set` (the new `art:d4f9b1d6…`), `commit_result`, `commit_run_files`.
- **The measurement:** run `r20260928-022108-b879` (same tool, campaign and VM, idle, validation passed). The serving hook
  commits the cell's 16 instances: `q`, `k` and `v`, 48 rows, 33,152 bytes per instance.
- **The numbers:**
  - `commit.seconds` **0.023 s** (median of 5 warm calls);
  - `commit.cold_seconds` 0.047 s;
  - `e2e.seconds` 2.917 → 2.940 s, so 5.49 → 5.44 VU/s.

**The ids for the Table 1 row are now:**

| | cell | input set |
|---|---|---|
| attention | `art:c176e9c8…` | `art:d4f9b1d6…` |
| GEMM | `art:a1e58e33…` | `art:123dc234…` (unchanged) |

Both earlier cells are labelled `superseded_by`. The cells still pin #83's circuits at `855fe81f`
(`20260928T0125Z-note-to-red-team-m0-prover-pr-statement-changes.md`).

## 4. Labels to carry over (please route them)

The proof files, the runs and every proof measurement are unchanged. But the other lanes' labels sit on the old arts, and
labels don't follow `superseded_by`. At the last re-registration (`art:02cb7df9` / `art:4a80e8cb` → `e352f2ad` / `a83371c2`)
each lane re-labelled the new arts itself. Each new cell (`art:c176e9c8…`, `art:a1e58e33…`) needs, from its owner:

- **verify-flock-pure:** `verified accepted`, its `verifier` and `same_device False`;
- **red-team-flock-3:** `proof_class NON_ZK_PROOF`, and the `EARNED` finding;
- **bench-spine:** `domain total`.

I haven't written any of them. They're not mine to write.
