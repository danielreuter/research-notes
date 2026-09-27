lane: vllm-serving-commit · kind: handoff · from: one-stage-e2e · created: 2026-09-27T06:32Z · status: open ·
repo: danielreuter/verity · origin: PR #116 (`cursor/one-stage-e2e-6014`) @ 43122fa5

# Run A2: pin `43122fa5` for the registration; the v1 record is in

Follow-up to `20260927T0601Z-handoff-from-one-stage-e2e.md`. Nothing about the committed bytes changes.

- **Pin `verity_one_stage` at `43122fa5`.** `registration.py` has been `verity/registration/v1` since `dd205c2e` and is
  unchanged through `43122fa5`. `partition.py` gives the same N = 183,680 digests as before.
- **Build `registration.json` after serving** with:

```python
from verity_one_stage import partition as P, registration as R
prog = P.population_program(<RoPEHead_v1{D=64} definition>, 183680)
q = P.template_instance_query("RoPEHead_v1{D=64}")
part = P.partition(prog, q); pd = P.digest(part)
roots = [{"port": p, "root": <root hex>, "leaves": n,
          "domain": R.served_domain(part["program"], pd, p, schema, n, run)}
         for p, schema, n in (("x", "hm96-sha512/row/v1", 183680), ("cs", "hm96-sha512/row/v1", 183680),
                              ("out", "u16", 183680 * 64))]
rec = R.record(prog, q, {"law": "subset", "k": 256}, "frame-v3-sha512/hm96-sha512", roots,
               {"kind": "served", "row": 101, "run": run, "committer": {...}, "served_program": ..., "served_program_digest": ...,
                "vllm_v1_run_root": ..., "index": <SHA-512 of index.json>, "order": "verity-vllm/serving-rows/order/v0"},
               leaf_layer=<SHA-512 of pub-183680.bin>)
```

  - `R.served_domain` is the agreed rule, byte for byte: `identity_digest` of `verity/one-stage/served-domain/v0`, then
    `CommitmentDomain(..., -1, RangeIndexedDomain(0, leaves), hash="sha512")`.
  - `run` is the same research run id you bind into the domains at launch.
- **The public file's header** is exactly what M0's `write()` at `e51e2b86` produces for the bound circuit (pin
  `cdcbd876…`), as you planned.
- **My check** is `R.check(rec, prog, q, law, scheme, ports, leaf_layer=...)`. It recomputes every domain with
  `served_domain` from the record's own program, partition and `window.run`, so a mismatch shows up as `R3-domain`.
- **Hand-off location.** Put the four files, and their art id if you store them, in a handoff here. I'll run A2 on my CPU
  pod when they land.
