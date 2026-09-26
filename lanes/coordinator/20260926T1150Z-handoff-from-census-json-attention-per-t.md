---
cursor:
  subagentId: "bc-d763c580-ec6d-5c4f-bdc2-da5397f3574a"
---

# census-json: attention counted per key count, and one verifier-evaluated switch. Merge request (PR #73)

**To:** research coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628).

## Merge request
- **PR:** [PR #73](https://github.com/danielreuter/verity/pull/73), `cursor/attention-per-t-574a` into `main`, on top of `dcac8f23`.
- **Tests:** `backends/numerical` passes (966). CPU only.
- **Byte identity:** tables, raw JSON and parity are byte-identical. Only the headline section changes; the batch-1 rows' attention work is now exact, where it was an interval.

## Please check on the real cells
I could not read the store from this VM. The T matcher follows `ir_bench.result` on `cursor/flock-ir-lowering-c78f`: T sits in `software.backend.unit` (`.../d64-bn128/t<T>`), with `profile` and `K` null.

It also accepts T recorded in:
- `statics` or `variables`, on the fingerprint or the cell stamp;
- the instances ref;
- the set name (`-t<T>`);
- the registered set's parameters.

Two disagreeing records reject the cell X, with both values in the reason. After merging, please check:
- **On a render,** that art:308df7ad (T = 4) and art:327e9366 (T = 258) land on `attention-head/d64-bn128/sm80-fa2-bf16 · T = …` rows of the L40S line.
- **If a cell is rejected** with "records none", send me its fingerprint and I'll add the field.

## Drawn T
Drawn T come from registered input sets of that subcircuit whose meta records `row: 101`, reading T from the parameters, the relation statics, the set name, or a `T_values` list.
- **The captured set art:6312cb50** holds all 16 T in one set. The headline can list them only if its meta carries `T_values`, or if the per-T sets carry the row.
- **If neither,** the headline prints "drawn T = not recorded". Coverage is unaffected; only the covered-vs-drawn line is.

## Rules implemented
- **Per T:** a cell covers #101's attention units at its own T, weighted by `variable_counts` (T 1–287, 16 VUs each). The per-T counts come from the one request's positions and match every stratum's population by phase. Other T stay uncovered and nothing is extrapolated.
- **Verifier-evaluated parts:**
  - Attention's softmax (4–11% of a head's scalar ops, all of its exp2 and reciprocal work) is counted with a † footnote, citing red-team-flock-3's grant as 20260926T1115Z. That handoff was not in the coordinator folder when I looked; I took the condition from your message.
  - Sampling is not counted, pending Daniel. `--preview-count-omitted` counts it, and also every `omitted` label.
