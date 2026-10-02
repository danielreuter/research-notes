---
id: 20261002T1059Z-reply-from-red-team-proofs-554-pr814-pr815
campaign: e2e-guarantees
lane: proofs
kind: handoff
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# red-team-proofs-554 → proofs: #814 (k_log ≤ 27) GRANT at b6b4bf029, #815 (glibc guard) GRANT at df9682f34

Both are granted. #814 has three findings, none blocking: the PR's peak-memory margin doesn't add up (F1), the table
misses two k_log-dependent allocations (F2), and the harness's MAX_ANDS default re-keys the stage cache for every K (F3).
#815 has no findings.

How I reviewed: read-only, from `/workspace`'s objects; a detached scratch worktree at `b6b4bf029`, and my own clone of Flock
b684b12 with the generated tree built as `pod/60-circuit.sh` builds it (the link, gpu-link, sha512, glue, zk and vtime
patches, then `cuda_chunk_patch.py`, `cuda_circuit_patch.py` and `cuda_sha512_patch.py`). No build, GPU or pod. Both scratch
trees are removed.

## #814 at `b6b4bf0290a71c5a9d6397bbe35a60abb8c54f72`: GRANT

### CUDA audit (pasteable into the PR body)

> **CUDA audit** (red-team-proofs-554, at `b6b4bf029`; `note:proofs/20261002T1059Z-reply-from-red-team-proofs-554-pr814-pr815`).
> A second agent read the generated tree (Flock b684b12 with the patches `pod/60-circuit.sh` applies) for every use of
> k_log, `1 << k_log`, `K` and `type_log` in `prove_circuit.cuh`, the `prove_chunk.cuh` helpers it calls, upstream
> `lincheck.cuh`, `induce_sumcheck.cuh` and `prove_ffi.cu`, and `live/src/gpu_circuit.rs`. Each of the 14 entries has the
> stated types and holds at 2^27.
>
> Entry 6 is exact. Its only launch is `launch_linear_check_compressed_column_fold`, with 32 threads a column and
> `LC_TPB` = 256 a block (nothing in the tree redefines it). At 2^27 columns that is 2^24 blocks, and the largest unsigned
> index is (2^24 − 1)·256 + 255 = 2^32 − 1. A 2^28-column type needs `type_log` 28, which `range_in_block`
> (`slot_log ≤ k_log`) and `fc_bad_shape` refuse. A net's slot is its unit (`circuit.rs` refuses `unit_log ≠ slot_log`), so
> `fc_fold`'s upload of `2^type_log + 1` column pointers matches the host CSC.
>
> The table misses two k_log-dependent allocations, both harmless:
> - `chunk_quirky_eq_device`'s scratch: 2^(k_log−6) words (32 MiB at 27), taken from the arena's 64 MiB slack and freed
>   at once.
> - `fc_fold`'s per-type CSC cache: a `cudaMalloc` outside the arena, held for the process, of (2^type_log + 1) column
>   pointers plus the nonzeros for each matrix. This is the part of "outside the arena" that grows with k_log.
>
> Every allocation failure refuses the proof:
> - `device_arena.begin` (one `cudaMalloc`) and `ffi_malloc` (a sub-allocation, `cudaErrorMemoryAllocation` when nothing
>   fits) both return through `CK`, as code 100.
> - The CSC caches keep their error, and `CK` returns it.
> - Ligerito's arena allocations go through `LFCK`.
> - `gpu_circuit::prove_circuit` asserts `rc == 0` before it decodes anything.
>
> The only unchecked `cudaMalloc`s (`induce_setup_device`) are reached only from a test. `build_eq_device`'s unchecked
> one-word `cudaMemcpy` is surfaced by the next `CK(cudaGetLastError())`.
>
> Peak memory: the arena is 92,224 MiB (formula checked). Outside it, 2,013–2,743 MiB was measured at k_log 26.
> - If nothing outside grows, the peak is 94,237–94,967 MiB, leaving 2.9–3.6 GiB.
> - If all of it doubled, the peak is 96,250–97,710 MiB, leaving 1.6 GiB down to 0.2 GiB.
>
> It fits either way. The first k_log-27 run's peak settles where in that range it lands.

### Findings (non-blocking)

- **F1. The peak-memory paragraph contradicts itself.** It projects "about 94.2–95.5 GiB, out of … 95.6 GiB" and then says
  "leaves about 1–3 GiB". 95.6 − 94.2 = 1.4 and 95.6 − 95.5 = 0.1, so the projection leaves 0.1–1.4 GiB. The numbers look
  like thousands of MiB written as GiB: 94,200–95,500 MiB would leave 2.3–3.6 GiB. The audit paragraph has the range from
  the formula. Suggested fix: replace those two lines with that range.
  - It doesn't change the verdict. If the outside part grew more than projected, `begin` or a CSC `cudaMalloc` fails and
    the proof is refused.
- **F2. The table misses two k_log-dependent allocations**: the quirky-eq scratch and the out-of-arena CSC cache, both
  covered in the audit paragraph. Two more things in the code read k_log but don't depend on the block:
  - `subs = 1 << (k_log − sub_log)` is computed in `flock_cuda_prove_circuit` and never used. `gpu_circuit.rs` fixes
    `sub_log` at 14, so `KS`, `d_comb_sub` and the `chunk_matrix_once` upload don't depend on k_log.
  - `fc_comp_scatter` is never launched, as the PR says.
- **F3. Harness.**
  - `74-gemm-hill.sh` sets `MAX_ANDS=2^25` for every K, not only 32768. `--max-ands` is part of `_stage_cache`'s key
    (`class_statement.py`), so the next K ≤ 16384 hill run re-keys `FLOCK_STAGE_CACHE` and restages once. That costs time
    only.
  - K = 32768 has no `CASE_MIB` entry (line 96), so the preflight's three GPU selftest cases run one at a time. That is
    the safe default, just slower.
  - `INSTANCES[32768] = 256` = 2^(35 − 27), and 2^25 = 33,554,432 > 16,860,955 ANDs. Both are right.

Suggestion, optional: make the CSC `as u32` casts in `gpu_circuit.rs` checked (`u32::try_from(..).expect(..)`), and have
`launch_linear_check_compressed_column_fold` refuse `n_cols > 2^27`. Then entry 6's missing headroom and the 2^32-nonzero
bound are enforced at the kernel rather than only by the shape guards upstream. A wrap there gives a proof the verifiers
refuse, so this is about robustness, not soundness.

### Guards (c): they all move together

| Guard | At 27 |
|---|---|
| Rust `IN_RANGE_K_LOG = 27` (`block_in_range`, and the composite's `(7..=IN_RANGE_K_LOG)`) | accepts |
| CUDA `fc_bad_shape`, `k_log ∈ [20, 27]` | accepts |
| Python `K_MAX = 27` (`circuit.py`; `typed_statement.py` reads it) | accepts |
| Lean `checkInRange` and the pinned `checkInRange_ok` | accepts |
| Lean schedule guards (`Statement.lean`, `HmRow.lean`), `kLog > 27 \|\| m > 35` | accept |
| soundness `Stmt.InRange` (`kLog ≤ 27`, unchanged) | covers |

The guards that must still refuse 27 do: `flock_cuda_prove_chunk` (20–22) and `ir_frame.py`'s `K_MIN, K_MAX = 20, 22`.
`transcript_check.py` takes k_log from the lincheck's round count, and its `vec` cap of 2^26 bounds only lengths that don't
grow with k_log (the lincheck has 21 rounds at 27). `fc_bad_shape`'s int sum `r_pos0 + r_count` can't overflow:
`range_in_block` keeps it at most 2^20.

On the zk side, M1's device code (`fc_commit_l0_zk`, the lane phase) reads `log_n` and `initial_k`, not k_log. The only
k_log input is the lincheck's comb, folded to 64 words. zkaudit at 27 remains the design owner's separate condition.

### Carry

The tip is now `cedf5ceae`, a merge of main `5f08b1ab2` onto `b6b4bf029`. It changes nothing under `backends/flock/cuda/` and
leaves `live/src/gpu_circuit.rs` alone, so the CUDA audit carries as it is. The carry needs three reads:
- main's `circuit.rs` and `circuit.py` changes, for new k_log paths;
- the conflict resolution in `pod/74-gemm-hill.sh` and `pod/gemm_hill.py`;
- that the branch's 13-file diff over main is unchanged.

Resume me for it.

## #815 at `df9682f34cb192b618e9f14581b67559c60d54ec`: GRANT

The new check is `[[ $(ldd $BIN/flock-circuit $BIN/flock-circuit-selftest 2>&1) == *"not found"* ]]`, then
`rm -rf $BIN || { echo …; exit 1; }`.

- **It catches a binary built against another glibc**, under the script's own `set -uxo pipefail` and under
  `set -euo pipefail`. The old pipe `ldd … | grep -q` missed it whenever `ldd` exited nonzero, because pipefail takes the
  pipeline's status from `ldd` (and `grep -q` exiting early can SIGPIPE `ldd`). The new check has no pipe. Inside an `if`,
  errexit doesn't apply, so a failing `ldd` doesn't stop the script under `-e`.
  - I replayed both guards with a stand-in `ldd` (results below). Under `-euo pipefail`: a mismatch removes the directory, a
    binary that loads is kept, and a failing `ldd` with no match leaves the script running.
- **Stopping when the stale copy can't be removed is right.** The build key covers the build inputs, not glibc, so a stale
  directory that stays would be reused by the next step. Exit 1 fails the run loudly, and it is recorded as a failed
  Attempt. The alternatives are worse: a binary that can't load fails later and less clearly, and a build into a directory
  that can't be emptied isn't safe.

| Case (stand-in `ldd`) | Old guard | New guard |
|---|---|---|
| glibc mismatch, `ldd` rc=1 | missed | fired |
| glibc mismatch, `ldd` rc=0 | fired | fired |
| missing library, rc=1 | missed | fired |
| loads fine, rc=0 | not fired | not fired |
| selftest binary absent ("No such file"), rc=1 | not fired | not fired |
| no `ldd` on PATH | not fired | fired (a rebuild) |
| `rm -rf` on a directory it can't empty | — | took the exit-1 branch |

Remarks, none needing a change:
- Without `ldd` the job rebuilds every run, which fails safe.
- A localized `ldd` message could miss the match, but the binary would then fail loudly when it runs.
- glibc isn't in the build key, so jobs alternating between environments may rebuild back and forth. That costs time only.
