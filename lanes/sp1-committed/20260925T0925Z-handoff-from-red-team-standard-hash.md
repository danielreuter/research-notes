---
lane: sp1-committed
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T09:25Z
---

# red-team SH: sp1-committed R3 fix b54e42ed: FAIL (open) on the `--instances` path and whenever `committed-verify` runs without `--batch`; the `--batch` path is correct by code review

This is a code review of b54e42ed; I ran nothing e2e. The `--batch` path is right. `instance_check` re-commits the rows
natively from the batch file and compares them with the statement's trees. `vector_run` requires `instance_roots is True`
and runs the prover-chosen-roots negative. Two gaps leave R3 open.

1. **`committed-verify` fails open without `--batch`.** In `committed_cmd.rs` (around lines 541-549), with no `--batch`,
   `instance_reason` is `None`, so `instance_roots` is `None` and `ok = ... && instance_roots != Some(false)` is true. The
   verifier emits `"ok": true` with `"instance_roots": null` for a statement whose roots are prover-chosen, which is
   exactly the art:b11bc6ee statement. `vk_pinned != Some(false)` fails open the same way when `--expect-vk` is absent.
2. **`vector_run --instances` (the bf16-ampere frozen set) never recomputes the roots.**
   - `instance_args = ["--batch", ...] if a.batch else []`, so the `--instances` source verifies without `--batch`.
   - The final `ok` accepts `instance_roots is True or not instance_args`.
   - The prover-chosen-roots negative runs only `if nrep and instance_args`.

   On that path an SP1 proof over prover-chosen roots is accepted end to end, and the negative that would show it is
   skipped.

**Fix:**
- `committed-verify` should report `ok` only when the roots were recomputed: require `instance_roots == Some(true)`, or
  make `--batch` (or an `--instances DIR --manifest-sha256` equivalent) mandatory.
- `vector_run --instances` should format the batch file it already derives from the frozen set, pass it to every verify,
  and run the prover-chosen-roots negative on both sources.
- The same pattern applies to `--expect-vk`.

**Consequence:** a Table 2 SP1 committed cell counts only if its `verify.json` shows `instance_roots: true` for every rep,
or a non-producer recomputation of the three roots matches the statement. A cell from an `--instances` run (bf16-ampere)
does not count as it stands.
