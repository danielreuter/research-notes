---
id: 20261001T0225Z-handoff-from-proofs-verify-overlap
campaign: verity
lane: flock-netlist
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-verify-overlap (bc-96b9bb72), worker of @proofs (bc-8416bc72)
---

# The loopback verifier off the GPU's critical path: 8.0x fewer GPU-held seconds per coordinate at K=2048, same bytes

**Result (BF16 `GemmCoordinate_v2{K=2048}`, node 1, RTX PRO 6000, m = 35, 2048 coordinates per statement):**

| run | config | GPU-held s/VU | GPU util (steady) | cores |
|---|---|---|---|---|
| `r20260930-235547-335a` | baseline: serial verdicts | 0.003356 | 9% | 48, shared |
| `r20261001-010211-c85b` | `FC_VERIFY_AHEAD=10`, one verifier process | 0.001368 (2.5x) | 22% | 48, `cpu-slice-shared` (others 27) |
| `r20261001-020954-a474` | `FC_VERIFY_AHEAD=10`, `FC_VERIFY_SERVERS=11` | **0.000419 (8.0x)** | **72%** | 16, locked slice 160-175, others 0.16 |

- Prove-only is 0.000343 s/VU, so the overlap leaves 22% above the prove. That remainder is the last session's verdict
  (about 3.4 s) spread over 24 timed sessions. In steady state the LIVE stamps are 0.69 to 0.79 s apart, one prove each
  (`e2e_s` 0.709 s against `prove_total_s` 0.695 s). A longer stream approaches 0.000346 s/VU.
- **Byte identity:** the gate passed on the GPU in every run: `gpu_paths_agree`, `gpu_proofs_match_cpu` and
  `verify_ahead_matches_serial`. The last now runs its overlapped sessions against two servers taking turns, and their
  proofs and transcripts equal the serial run's. The statement digest `7f39853935e48dec…` is the baseline's. Coins stay
  `os-seed-prf`.
- **Serial comparator on a 16-core slice:** `r20261001-023653-0e36` (`FC_VERIFY_AHEAD=0`, one verifier, RUNS=12): 1.99e-3
  GPU-held s/VU, steady utilization 0.12, verify 3.35 s per session. So on equal cores the overlap is 4.75× faster. That run
  is flagged `cpu-slice-shared` (other jobs averaged 2.8 of its 16 cores), so read it as an upper bound on the serial cost.

**Why one process didn't scale (C2):** 11 concurrent verifies in one `serve` took 20 to 38 s each, on 7 busy cores of 48.
As 11 processes on 16 cores they take 3.4 to 5.9 s. proofs-arch found the cause in the code
(`note:20261001T0212Z-handoff-from-proofs-arch-session-verifier`): upstream's verifier core runs on a process-wide
one-thread pool, so sessions in one process verify one at a time. More processes help; more sessions per process don't.

**What changed (branch `cursor/proofs-verify-overlap-95d4`, scheduling and process layout only):**
- `FC_VERIFY_AHEAD=N` (prover, default 0): up to N proved sessions send their proofs and await their verdicts on threads
  while the next one proves. `serve --concurrency C` serves C sessions at once (15101bcfa).
- `FC_VERIFY_SERVERS=S` (`class_statement`, default 1): S `serve` processes. Session k goes to the (k mod S)th, through
  `prove --verifier a,b,…`, and each serves ceil((1 + N) / S) sessions at once (d35ea8d05, cdcebde62). `serve` prints the
  address it bound, and appends each index line in one write.
- `FC_COINS=os` (opt-in): the strict per-round OS-coin mode for non-ZK sessions. The default and its statement digest are
  unchanged (804be92b4).
- `STAGE_ONLY=1` (`74-gemm-hill.sh`, `class_statement --stage-only`): builds and stages in a 0-GPU job, so the GPU job proves
  from `FLOCK_STAGE_CACHE`. It saved 7 minutes of GPU per point here. A point that staged on its GPU is flagged
  `staged-on-gpu` (556e40e39).
- `hold_slices` now refuses a `CPUSET` outside the job's own cpuset. Before, `CPUSET=96-111` on a provers pod (affinity
  128-175) pinned unlocked cores beside another job's (424611433).
- `FC_PIPELINE_DEPTH` and `FC_HOST_PREPIN` are unchanged.

**`--session-tables` above 1 (the 0034Z question): it adds about nothing on top of the overlap.** With verdicts off the
critical path, each session holds the GPU for `e2e_s` 0.709 s, and 0.695 s of that is the prove. The round trips and the
link exchange that J tables would share are the other 14 ms (2%, 287 round trips at loopback). Verification cost scales
with J (one verify per table and rep), so J doesn't lower the verifier's CPU either. The next levers are the prove itself
and the statement layout: bf16-hill's 4x4 tile is 4x fewer s/VU at its prove-only. The overlap applies to it unchanged.

**Friction:**
- `hold_slices` in any-free mode lets a multi-slice job starve behind one-slice jobs.
- A job deleted while waiting for a slice still held its GPU while it waited. Waiting happens inside the job, after Kueue
  admits it, so with three slices for three GPU jobs, one slice per job (`CPUS=16`) is the only wait-free shape.
