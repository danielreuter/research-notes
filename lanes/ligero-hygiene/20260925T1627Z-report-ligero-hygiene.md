---
lane: ligero-hygiene
kind: report
created: 2026-09-25T16:27Z
status: final
---

CHECKPOINT 46e0c494 (17:16Z) [final] tip 46e0c494: items 1-4 done; BV-D1 fixed (config_for at k=l+1), live_test green, conformance negs 3/3 PASS (sha256 901 s, 47 proofs), 3 tile follow-ups + tests; pod terminated 17:11Z, <$0.10; merge-ready handoff to coordinator
CHECKPOINT 46e0c494 (16:54Z) [open] item3 run r20260925-164906-1069 on vy-ligero-hygiene: dummy PASS, poseidon2 PASS (~2 min each), sha256 running. VM sweep of ligero/ (sans conformance negs): 418 pass, 10 fail all env (no bench-instances arrays; timing_guard fails on main too). git push auth failing since 16:45Z, retrying
CHECKPOINT cd71b615 (16:45Z) [open] pod vy-ligero-hygiene = hb8gfpinlwovt7 (cpu3c 4 vCPU; 8 vCPU stock exhausted). bootstrapping for item3 (conformance committed-operand negatives, --exclusive)
CHECKPOINT cd71b615 (16:39Z) [open] item2 fixed @7c655f86: BV-D1 (config_for sized t at k=l, calculator k=l+1); prover now sizes at k=l+1 (non-ZK small l only). item4 @cd71b615: float seed, sharing label, missing .hproof, 3 tests green. next: item3 pod
CHECKPOINT 239c0e28 (16:27Z) [open] item1 green on VM @239c0e28: pytest hashauth+reverify+steps_pin 63 passed 0 skip (LIGERO_VERIFY set); cargo test --release 69 passed 0 failed. next: item2 live_test [None] 2^-99.86
CHECKPOINT 80b19e59 (16:19Z) [open] started; env set up; fetching main 239c0e28, branch lane/ligero-hygiene; item 1 (combined-tree tests) next, on VM; no pods yet

## Results (lane/ligero-hygiene @ 46e0c494, base main 239c0e28)

Read: coordinator/20260925T1505Z-handoff-from-reverify-tile-2, reverify-tile-2/20260925T1455Z-handoff-from-red-team-standard-hash-2,
coordinator/20260925T0935Z-handoff-from-ligero-steps-pin. Handoffs received: none (inbox empty throughout).

1. **Combined tree on main 239c0e28** (VM, 4 cores, CPU torch, LIGERO_VERIFY = the release build): `cargo test --release`
   in backends/ligero-verify 69 passed / 0 failed (3 suites); `pytest hashauth_test reverify_test steps_pin_test` 63 passed,
   0 skipped. Nothing broken by the combination. At the tip, those three + live_test: 79 passed.
2. **live_test shared pair [None] (2^-99.86 vs 2^-100)**: the calculator is right; the parameters were too weak. It is BV-D1
   (ligero-verify DISCREPANCIES.md): `config_for` sized `t` with `k = l`, while `soundness()` and ligero-verify evaluate the
   bound at the conservative stand-in `k = l + 1` (so e is one smaller). G at l = 512, t = 149: irs_query 2^-100.86 per proof,
   x2 (the pair) = 2^-99.86. Fix (7c655f86): `config_for` sizes `t` and `D` at `k_acc = l + 1` for non-ZK. Grid (evidence/
   config_grid.py: both modes, ZK or not, -80/-100/-128, 1..50 sub-batches, l = 2^6..2^15): 108 of 595 configs missed
   their per-proof target before, 0 after. Parameters change only for small-l non-ZK configs (171 of 952 in a wider grid);
   ZK and every l >= 8192 config are unchanged, so the decision workload and the Table 2 cells are untouched. The test's own
   target was not changed. BV-D1 is marked resolved, and PROTOCOL.md section 6 says so (46e0c494).
3. **Conformance committed-operand negatives** (r20260925-164906-1069 on vy-ligero-hygiene, cpu3c 4 vCPU, --exclusive,
   run_record art:020560e11fdb6de173a1ce65b5cc72680bc2fbfae2fa00385112d3890b3ab912, PRESERVED): dummy PASS 69 s,
   poseidon2 PASS 111 s, sha256 PASS 901 s. Host load was about 320 (a shared EPYC host; the pod itself was idle). sha256
   is slow by construction, not a hang: hashed_negatives runs 47 full CPU proofs (1 honest + 46 witness-row negatives) at
   about 17 s each, because the sha256 leaf is 41,918 rows/unit (37,410 hash rows, 56,578 quadratic constraints) against
   6,210 for poseidon2. cProfile: 802 of 903 s is in prove_vus; the top self-time is the NTT butterfly
   (field._butterfly_eager, 193 s), then witness._bool_row (151 s). A 1800 s timeout on a load-500 host is too short for it.
4. **Red-team tile follow-ups** (cd71b615, tests in hashauth_test.py):
   - a float `set.tile` seed is refused in `tile_shape` (a FAIL with a reason; it no longer reaches `default_rng` as a TypeError);
   - `set.sharing` (when present) and the result fingerprint's `sharing` (what the tables render; `verify_tree(fingerprint=...)`,
     which `reverify()` passes) must equal `tile<nx>x<nw>` / `none` for the recomputed tile, else FAIL;
   - a pair dump (manifest `system_h_file`) must have one `.hproof` per `.proof` (R4), else FAIL. A missing `.hproof` that
     the manifest lists stays an ERROR "incomplete dump", and Rust batch refuses the sub-batch too (the test asserts both).

VM sweep of backends/direct/ligero at 7c655f86 (conformance negatives and blake3 deselected): 418 passed, 10 failed, all
environmental. 9 need the built bench-instances/v1 arrays (the build needs downloads, which failed on DNS here), and
timing_guard_test fails the same way on 239c0e28 in this environment (KeyError 'contention').

Pod: vy-ligero-hygiene (hb8gfpinlwovt7) created about 16:45Z, terminated 17:11Z, under $0.10. Merge-ready handoff:
`lanes/coordinator/20260925T1715Z-handoff-from-ligero-hygiene.md`.

## FINAL

~~~text
tip: lane/ligero-hygiene @ 46e0c494 (base main@239c0e28)        merge-with: none
known-failures: timing_guard_test (KeyError 'contention', fails on 239c0e28 in this env); 9 privsel/pubsel tests need built bench-instances/v1 arrays
pod: terminated 17:11Z; <$0.10
artifacts: art:020560e11fdb6de173a1ce65b5cc72680bc2fbfae2fa00385112d3890b3ab912
~~~

Commits: 7c655f86 (config_for at k = l + 1, BV-D1 resolved), cd71b615 (reverify tile follow-ups + tests), 46e0c494
(PROTOCOL.md section 6). reverify now accepts less, so the brief's red-team spot-check applies.
