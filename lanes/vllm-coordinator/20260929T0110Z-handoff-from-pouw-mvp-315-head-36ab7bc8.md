---
id: 20260929T0110Z-handoff-from-pouw-mvp-315-head-36ab7bc8
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-mvp
---

# #315's head is now `36ab7bc8`: merged with #311's `1cbc750a`, and **its default changed since your GO on `58c3bc49`**

From the PoUW MVP owner (bc-dd22acf8). See https://github.com/danielreuter/verity/pull/315.

- **Default changed:** `weight_operands` is now `per-forward`. `resident`, a weight-derived copy of 3 B per weight
  (about 205 GB at 70B), is an opt-in. That's Daniel's rule: no extra weight copy is ever a default. With the new default,
  `keeps_weight_copy` is False, so `pous` composes with PoUW as it ships.
- **Formation in blocks:** operands are formed 256 MiB of rows at a time. At 8192×8192 the transient peak drops from
  4.7 GiB to 146 MiB, and the output is bit-identical.
- **Not auditable yet:** this is stated in #315's description, its README and `info()`. There is no epoch rotation, the
  rows are never persisted, there is no opener, and `leaves` grows without bound. The check is
  `internal/pouw-mvp/deployment-audit-315-check.md` in the research store. Whether to hold #315 until an audit path
  exists is Daniel's call.
- **The merge:** `1cbc750a` is merged in, and `outside_program=` is dropped from `pouw.py` and `test_pouw.py`.
  - `pouw` beside sampled proofs stays refused (`traced_as` returns None) until its modeled circuit lands.
  - The branch also carries the `protocols/pouw` and `benchmarks/pouw` suite tables for #320's layout (the same
    change as `a3fe82ff`).
- **Tests on `36ab7bc8`:**
  - protocol options: 51 passed;
  - root suite: 16 passed;
  - `protocols/pouw`: 45 passed;
  - `benchmarks/pouw`: 7 passed.
- **Check:** not re-recorded yet. That happens once, on the head that merges #311's D3′ rebase. The merge status is
  untouched.
