---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: vllm-coordinator · kind: handoff · from: vllm-serving-commit (bc-819f6247) · created: 2026-09-27T07:20Z

# Status: the GPU plan is done, the e2e lane has its files, the pod is terminated; about $1.02 spent. One ask: gate (b) for merge-ready

## Done
- **#101, scheme off:** equals the record: verdict PASS, program `ccc21347`, manifest `90f81868`, run root `7adcef49`.
- **#101, scheme on:** verdict PASS with the same program, manifest and **`vllm-v1` run root `7adcef49`**. All 183,680 RoPE heads are
  committed in M0's format.
- **Byte-match:**
  - the served rows at the 1,024 captured heads equal the capture;
  - M0's `write()` over all 183,680 served heads equals serving's `pub`/`inst` files byte for byte, headers included;
  - the circuit pin is as agreed.
- **Overhead:**
  - time: the hook took 14.6 s (9.6 s reading through openings, 4.7 s hashing), against a Commit stage of 190 s on and 193 s off;
  - bytes: it hashes 70.5 MB of values, against about 908 MB for `vllm-v1`; it keeps 70.5 MB public and 117.6 MB private.
  - `vllm-v1`'s own committer timing wasn't captured: it's in the pod's sweep directory, which isn't in custody.
- **Records:**
  - runs `r20260927-061338-8809` (`art:4474915c…`) and `r20260927-065834-9db4` (`art:107b97ee…`), both PRESERVED;
  - bundle `art:fcc4e542…`, holding the v1 registration (the e2e lane's `R.check` returns ok), the index, the window and the match
    record.
- **Handoffs:**
  - to the e2e lane: `internal/lanes/one-stage-e2e/20260927T0715Z-handoff-from-vllm-serving-commit.md`, with a copy beside this file;
  - to flock-netlist: a performance finding. M0's `write()` is quadratic in n for the prover file.
- **PR:** [#119](https://github.com/danielreuter/verity/pull/119) (draft, `lane/vllm-serving-commit` @ `efec3ad1`), updated with the
  results and the salts note (R2 custody is fine for this demo; in production the prover's file never leaves the prover side).
- **Pod and spend:** `vyv-rf-serving-commit-g1` (`xie2bspsdvc0vz`) ran 06:13–07:09Z and is terminated. About $1.02 of the $40.

## Open: gate (b) for merge-ready (estimate, asking to start)
- **What:** the test-suite jdiff of head `efec3ad1` against base `8515c79e`, in git clones on one pod, with `gate_b2.sh`, including
  `tests/commit`.
- **Pod:** one CPU pod (`cpu3g`, 16 vCPU, about $0.64/h) for about 45 min, **about $0.50, cap $1**.
- **Nothing else pending.** Reply with an ack and I'll run it, then send the merge-ready handoff.
