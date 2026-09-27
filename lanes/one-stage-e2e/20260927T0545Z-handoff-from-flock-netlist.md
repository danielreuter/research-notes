---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: one-stage-e2e · kind: handoff · from: flock-netlist · created: 2026-09-27T05:45Z · status: final · repo: danielreuter/verity ·
origin: PR #83 @ e51e2b86 (in the store bundle `artifacts/pr83-e51e2b86.bundle` until the root pushes it)

# M0's four e2e bindings are in (`e51e2b86`): your stage 5

The statement format is otherwise the one in `lanes/flock-verifier/20260927T0445Z-handoff-from-flock-netlist-format.md`.

## What you pass, and where it lands

`python -m verity_flock.circuit --input-set DIR --n N --out DIR --partition H --program H --unit-indices FILE`

| # | binding | how you pass it | where it lands |
|---|---|---|---|
| 1 | partition | `--partition H`: your `verity/partition/v1` SHA-512 (128 lowercase hex) | META `partition = {"rule": "verity/partition/v1", "digest": H}`, under the circuit pin, the statement digest and Σ. Without it, the provisional `flock-circuit/unit-cover/v0` is used. |
| 2 | program | `--program H`: the Program's SHA-512, the one the partition object names | META `program_sha512 = H`. Without it: SHA-512 of the subcircuit's canonical descriptor (the bytes core's `program_digest` hashes). For RoPE d64 that is `57fab977…`. For a 1,024-Call population Program, pass the population's. |
| 3 | global unit indices | `--unit-indices FILE`: a JSON list with one entry per staged instance, ascending | the header's `units.indices` (and `units.blocks`, in chunks of `vus_per_block`). The draw is over positions `[0, N)` of the staged population; instance `i` of a drawn statement is unit `indices[units[i]]`. |
| 4 | each instance's class | read it with `python -m verity_flock.circuit --input-set DIR --class-only` (prints `class_sha512`) | the header's `units.classes[i]`. The class is SHA-512 of the circuit file with META's bindings (`partition`, `program_sha512`, `program_digests`) removed, so it doesn't depend on the partition that names it. It depends only on the template, so it's the same for every instance. |

The live verifier checks `classes` against its own computation.

## Checks

- **CPU check.** RoPE staged with a test partition digest and indices `[3, 17, 40, 1001]`: the honest session and
  `unit_draw_session` pass.
- **GPU selftests** at `eb90718f`, the same statement without these fields: RMSNorm fused 34 of 34, RMSNorm Triton 34 of 34,
  RoPE 30 of 30, SiLU 31 of 31 (the SiLU block is 2^26).

## Your Run A1

- **Order.** Build the partition over your Program with `--class-only`'s digest as the class, then stage with `--partition`,
  `--program` and `--unit-indices`. After that, `serve --draw subset:K` and `prove`.
- **Registration.** `Register` is still a bare signal. The population is the staged public file (roots over all N, every
  `b ‖ c`, the outputs), and your `registration.json` checked against it is the right place for the registration record.
- **The Lean verifier's catch-up** for this format (stage 7) is the flock-verifier lane's.
