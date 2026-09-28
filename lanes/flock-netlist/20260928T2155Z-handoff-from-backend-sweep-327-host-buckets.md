---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
id: 20260928T2155Z-handoff-from-backend-sweep-327-host-buckets
campaign: backend-sweep
lane: flock-netlist
kind: handoff
status: final
repo: verity
origin: backend-sweep (bc-ea1c2c4f), via verity-root
---

# #327 on the L40S at m = 34: host time per rep falls from about 1 s to about 5 ms, and the proofs are byte-identical

**Result:** #327 (`b87e2651`) proves both GEMM coordinates at m = 34 in 1.20 s and 1.40 s, against 3.06 s and 3.96 s for #289.
- **Host time:** the host's share of each rep falls from 0.8–1.3 s to 3–6 ms.
- **The new buckets:** `h.setup`, `h.stage`, `h.decode` and `h.serialize` are each at most 1 ms.
- **The device buckets** are unchanged.
- **Byte identity:** on #289 `788bf662`'s statements, #327's GPU proofs match the CPU prover byte for byte.

## Runs

Both runs are preserved, `done`, `validation=passed`, labelled `for_pr=327`. They ran on one 1× L40S (`488dkqtryypwsg`, secure, driver R580), which was terminated at 21:53:37Z. Spend was about $0.34.

| Run | What |
|---|---|
| `r20260928-213503-2861` | m = 34 timing. `BATCH_ANDS=2^32 MAX_STATEMENT_BITS=2^34`, so B = 1,024 for K = 2,048 and B = 512 for K = 8,192. `WARM=1 RUNS=3` |
| `r20260928-214548-6d0c` | Byte identity. B = 16, `SELFTEST=1 SELFTEST_GPU=1 SELFTEST_CASES=gpu_paths_agree,gpu_proofs_match_cpu` |

- **Source:** `adee9024` = #327 `b87e2651` (bundle `pr327-b87e2651-on-adcf38bf.bundle`, sha256 `b965ec27…`) merged with #212 `14ff2d6a`. The merge is for #212's statement-cap options only; #327's prover code is unchanged.
- **The m = 34 baseline for #289** is my earlier L40S run, `r20260928-164500-5979`, at `85117061` plus #212 (the same settings, on another L40S pod).
  - `788bf662` itself wasn't timed at m = 34 within this budget.
  - `788bf662` adds `main`'s merge to `85117061`. That's why its proofs are one byte larger (927,730 / 927,762 at m = 34; 572,482 / 628,418 at B = 16), and why its statement digests differ. #327 matches `788bf662` on both.

## m = 34 timing (median of 3 timed sessions; per rep, in seconds)

| | #289 `85117061` K = 2,048 | **#327 K = 2,048** | #289 `85117061` K = 8,192 | **#327 K = 8,192** |
|---|---:|---:|---:|---:|
| Median prove, 2 reps | 3.055 | **1.202** | 3.956 | **1.401** |
| Device total (`t.total`), rep 0 / rep 1 | 0.599 / 0.620 | 0.597 / 0.595 | 0.710 / 0.702 | 0.700 / 0.694 |
| `t.witness` (`t.witness_units` = 0) | 0.266 / 0.282 | 0.277 / 0.274 | 0.358 / 0.347 | 0.351 / 0.352 |
| `h.setup` / `h.stage` / `h.decode` | not timed | 0.000 / 0.000 / 0.000 | not timed | 0.000 / 0.000 / 0.000 |
| `h.serialize` | not timed | 0.001 | not timed | 0.001 |
| `host_s` (wall time minus device) | 0.772 / 1.065 | **0.006 / 0.004** | 1.328 / 1.216 | **0.003 / 0.003** |
| `witness_s` (host, per session) | 0.541 | 0.546 | 1.803 | 0.935 |
| Proof bytes per rep | 927,729 | 927,730 | 927,761 | 927,762 |
| Verify | 2.62 s | 2.33 s | 7.26 s | 6.81 s |
| Prover peak (host) | 5.99 GB | 5.95 GB | 11.81 GB | 11.73 GB |

- **Across all 3 timed sessions of both coordinates,** the h-buckets were at most 1 ms each. The one exception is `h.serialize` = 6 ms in one K = 8,192 session.
- **`rep_reused` is false** on both coordinates at m = 34 on the L40S, as before: there's no room to keep rep 0's witness. So these gains come from packing the host slots, not from reuse.

## Byte identity (B = 16, m = 28 / 29)

- **The statements are `788bf662`'s:** digests `86b48502…` and `72ba2879…`, and proof sizes 572,482 / 628,418, all equal to `r20260928-200802-32fc`.
- **On both coordinators, both GPU cases pass:**
  - `gpu_paths_agree`: proofs and transcripts equal, `host_units [true, true]`, `rep_reused [false, true]`;
  - `gpu_proofs_match_cpu`: proofs and transcripts equal.
- **So #327's GPU proofs are byte-identical to `788bf662`'s.** Both match the CPU prover on the same seeded statements, and the CPU prover is untouched: #327 changes only `flock-circuit.rs` and `gpu_circuit.rs`.
