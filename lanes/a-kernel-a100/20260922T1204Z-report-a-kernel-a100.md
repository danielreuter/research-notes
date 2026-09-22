---
id: r20-proof/a-kernel-a100/20260922T1204Z-report-a-kernel-a100
campaign: r20-proof
lane: a-kernel-a100
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/a_kernel_a100.md
---

# a-kernel-a100: why the A GPU packed path failed on the A100 -- a stale Triton cache, not a kernel bug (2026-09-22)

Lane `a-kernel-a100`, branch `lane/a-kernel-a100` (base `main` 181eed9), pod `vy-a100b` (A100-SXM4-80GB, sm_80, torch
2.6.0+cu124, triton 3.2.0, `/workspace/venv312`).  Input: `note:r20-proof/a-kernel-a100/20260922T1122Z-report-a-gpu-kernel-path-a100` (runs d89f / 6221 / 78ef).

## Verdict

* **First differing quantity**: the very first LogUp message, `root_q` of the first table (POW, `--vus 1`,
  hypercube `n = 10`), and before it every `q` value of tree level `n-1` computed by the a-gpu Triton kernel
  `gpu/kernels.py::combine_level` (`logup._combine_level`, used for level `n-1` by BOTH `logup_packed.prove_ext_table`
  and the torch `logup.prove_table`).  `p` values of that level are right, `q` values are wrong in coordinates 0..4
  and right in coordinate 5.  Same pattern for `gpu/kernels.py::ext_mul` on int64 inputs: 5 of 6 coordinates wrong,
  every row (r20260922-111508-d22c).  The packed kernels (`tree_level`, `leaf_level`, `ext_mul_rows`, the whole R16
  range path) agree with the pure-torch reference bit for bit on the same inputs (r20260922-110452-7963, R16 613/613
  messages and the leaf claim identical for eager and graphed).
* **Root cause**: the pod's `~/.triton/cache` holds binaries of `gpu/kernels.py`'s kernels compiled at 08:54-09:05 UTC
  (a-verifier's runs of the a-gpu kernel path from a pre-a-gpu2 tree) with the OLD field constant baked in: `X^6 = 31`
  (`WR = 31 R mod p = 268435390` appears in every stale `.ptx`; the current `W = 22` gives `1879048146`).  a-gpu2's
  0ec0616 changed `gpu/field.py: W 31 -> 22` "to match the packed kernels" but did not touch `gpu/kernels.py`, whose
  `mmul` / `ext_mmul` read `W`, `P`, `MU`, `R^2` as module-level `tl.constexpr` globals.  Triton's on-disk cache key is
  the kernel *source* plus the argument specialisation; the values of global constexprs are checked for change only
  within a process.  So every already-compiled specialisation (int64-input `ext_mul`, `combine_level`, `fold`,
  `logup_round`, `phase1`, `scatter_terms`, `eq_outer`, `rank1_add`) was served with `W = 31`, while a specialisation
  never compiled on this pod (e.g. `ext_mul` on int32 inputs, or any kernel in a new source file) compiled fresh with
  `W = 22` and was right.  Coordinate 5 of an extension product has no `W` term -- hence 5/6 wrong.
* **This is not architecture-, size- or value-dependent** and not a merge artefact; it is a per-machine cache state.
  Proof: the unmodified pre-fix code proves and the Python verifier accepts v1 `--vus 64` with
  `TRITON_CACHE_DIR=<fresh>` (r20260922-111848-dde1, 391 s = every kernel recompiling), and raises
  `fractional sum is not zero` in the same run with the default cache.

## Evidence trail (run ids)

| run | what | result |
|---|---|---|
| r20260922-110452-7963 | `gpu.v2.tools.logup_diff` at `--vus 1, 2, 4, 64` on `/workspace/bb/pos4096`: torch ref vs torch+a-gpu kernels vs packed eager vs graphed, per level / per message | fails already at `--vus 1`.  Every ext table (POW, ALIGN, LEAD, NORM): first diff = `root_q`; packed eager/graphed raise at the root; torch+a-gpu-kernels produces a transcript whose `root_q` differs (= the NO_PACKED "level 0 final check" rejection).  R16 (range path, no a-gpu kernel involved): all three paths identical.  `packed_ext_mul_rows == torch`; `agpu ext_mul != torch` |
| r20260922-110917-32e7 | `gpu.v2.tools.mmul_probe`: the two modules' `mmul`, `umulhi`, `mul.lo`, `mmul(mmul(a,b),R^2)` vs the Python oracle on 65 536 random pairs | all 0 mismatches for both modules (the Montgomery arithmetic is right on sm_80); `agpu.ext_mul` 327 680 / 393 216 wrong (= 5/6), `agpu.combine_level.q` 163 840 / 196 608 wrong (5/6), `.p` right, packed `ext_mul_rows` right |
| r20260922-111221-96a2 | `gpu.v2.tools.extmul_probe`: a-gpu's `ext_mmul` + its `W` terms called from a NEW kernel | 0 mismatches -- the a-gpu source is correct when freshly compiled |
| r20260922-111508-d22c | `gpu.v2.tools.extmul_bisect`: a constexpr-switched copy of `ext_mul_kernel` (loads `.to(int32)` or not, `R^2` fix-up on device or host, a-gpu vs packed primitives, int32/int64 index, num_warps 1/4/8, int32/int64 in/out) | every faithful copy right; the REAL `kernels.ext_mul` wrong on int64 inputs (`[8192,8192,8192,8192,8192,0]` per coordinate) and right on int32 inputs (a specialisation never compiled before on this pod) |
| r20260922-111848-dde1 | cache forensics + control | 10 cached `ext_mul_kernel.ptx`: nine from 08:54-09:02 UTC contain `268435390` (W=31), the one from 11:15 (my int32 probe) contains `1879048146` (W=22); 41 stale ptx of `combine_level / ext_mul / fold / logup_round / phase1 / scatter_terms`.  Pre-fix `main` code: default cache -> raise; `TRITON_CACHE_DIR` fresh -> `verified: true` |
| r20260922-112320-3ceb | **fixed code, default (stale) cache**, v1 `--vus 64` then `--vus 4096 --reps 3 --warmup 1 --proof-out` | 64: verified (112 s, recompiling).  4096: prover **2.998 / 2.979 / 2.978 s, median 2.979 s**, Python verifier 0.82 s, 3/3 accepted, proof 33 871 324 B round-trip verified |
| r20260922-112813-b2fe | `gpu/v2/tests/test_logup_paths_agree.py` (7 passed, 52 s); `PACKED_DEVICE=cuda pytest packed/tests` (**63 passed**); Rust verifier `cargo build --release` + `verify` on `proof64.bin` and `proof4096.bin` | Rust: **rejected, `LogUp POW level 2: final check`** for both (same message as a-protocol-diff's H100 finding) |
| r20260922-113301-5012 | the new regression test copied into the PRE-FIX tree (7cd9adf) and run with the stale cache still in place | **5 of 7 fail** (the three ext-table path tests and both a-gpu kernel checks; the two R16 tests pass -- no a-gpu kernel on that path): the test would have caught the bug.  Also: `/workspace/bb/neg` does not exist on this pod (only `pos4096`); the v1 negatives were never exported here |
| r20260922-113632-baa3 | v2 limb-form `/workspace/v2l/pos4096 --vus 64` (fixed code, default cache) and the 52 v2 negatives `/workspace/v2l/neg` | v2 B=64 **verified** (145 s incl. recompiling the v2 shapes); negatives **52/52 rejected** (packed path, fixed code) |

Instrumentation (all committed, none ad hoc): `backends/gkr/gpu/v2/tools/{logup_diff,mmul_probe,extmul_probe,extmul_bisect}.py`.

## The fix (commit 73b9f75)

`gpu/kernels.py`: `FIELD_KEY = sha256("babybear6:{P}:{W}:{R}")[:7]` is passed to every one of the nine
field-arithmetic kernels as an (unused) `tl.constexpr` argument `FK`, so the field constants are part of Triton's
cache key: a change of `W`/`P` (or a cache populated under another field) can no longer be served silently.  No
arithmetic changed; the torch path stays the reference (`VERITY_GPU_TORCH_ONLY=1`).  Same hazard, not yet realised,
in `packed/kernels_triton.py` / `kernels_fused.py` (`P_C`, `MU_I32_C`, `WR_C` globals; `W` there comes from
`reference._find_w()` and has never changed) -- worth the same one-line guard if that field ever moves.

Regression test `backends/gkr/gpu/v2/tests/test_logup_paths_agree.py` (CUDA): on leaves shaped like the real tables
(POW/ALIGN-like ext tables with `q` in the top band `>= p - 2^27`, R16-like identity table with `Nw = 56356`), the
torch reference with all kernels off == `logup.prove_table` with the a-gpu kernels == `prove_ext_table` /
`prove_range_table` eager == graphed, message for message and leaf claim; plus `kernels.ext_mul` and `combine_level`
against torch on int64 AND int32 inputs (separately cached specialisations).  The 63 packed tests never call a
`gpu/kernels.py` kernel, which is why they passed on the broken pod.

## What to trust

* **a-gpu2's rows on `vy-g5` (1.79-1.93 s / 4096, H100)**: the numbers themselves are fine as timings and their proofs
  were Python-verified.  The code is not machine-specific; the failure the coordinator saw on the A100 (and gate4-h100
  on `vy-g4`) is a cache-state problem of pods on which the a-gpu kernel path had been compiled before 0ec0616
  (08:15 UTC).  Any pod whose `~/.triton/cache` predates that commit needs either this fix or a fresh
  `TRITON_CACHE_DIR`; with the fix the same code path verifies on the A100 at 64 and 4096 VUs.  The A100 number is
  2.979 s median (1.66x the H100 1.79 s; A100/H100 memory-bandwidth ratio ~1.65x -- consistent).
* **a-verifier's "kernel path rejected on vy-g5"** (both verifiers, LogUp POW level 0) is very likely the same stale
  cache: a-gpu compiled there under `W = 31`, a-verifier ran the post-0ec0616 kernel path against those binaries.
  The `TORCH_ONLY` proofs it fell back to bypass every `gpu/kernels.py` kernel, which is why they were right.
* **Who filled the cache**: a-gpu-v2.  Its head bb7a5c0 is based on a-gpu, not a-gpu2, and still has
  `gpu/field.py: W = 31` (`git show bb7a5c0:backends/gkr/gpu/field.py`; 0ec0616 is not an ancestor).  Its runs on
  this pod (r20260922-090151-07aa negatives, -090930-3bc5, -091544-4e02 v1 control, -09xxxx limbs) compiled every
  `gpu/kernels.py` specialisation under `W = 31` -- correctly, for THAT tree: its `5.73 s` v2 / `7.93 s` v1 rows are
  self-consistent proofs over `F_p[X]/(X^6 - 31)` accepted by the matching Python verifier, so they stand as timings
  (the Rust verifier, which only accepts `X^6 - 22` since a-gpu2, would reject them for that reason alone).  When
  `main` (a-gpu2's `W = 22`) then ran on the same pod, Triton served the `W = 31` binaries.  The a-gpu2/a-gpu-v2 merge
  did not cause the failure (6221: the pre-merge a-gpu2 head fails identically) -- the shared cache did.  The same
  applies to `vy-g4` (gate4-h100, "fractional sum is not zero" on both a-gpu2 heads) if a `W = 31` tree ran there
  first.

## For a-protocol-diff (Python-accept / Rust-reject at `LogUp POW level 2`)

* The Rust verifier rejects **my A100 proofs too**, at exactly `LogUp POW level 2: final check`, for B = 64 and 4096,
  although these proofs were produced with freshly compiled a-gpu kernels (this pod, r20260922-112320-3ceb) and pass
  the Python verifier.  So the Python/Rust disagreement is deterministic, machine-independent and **not** produced by
  the stale-cache root cause above.
* Could my root cause produce a self-consistent-but-wrong transcript?  For LogUp: no.  `logup.verify_table` is pure
  host arithmetic (`e_mul`, `eq_point`), it shares no kernel with the prover, and a stale `combine_level` either makes
  the prover raise (`root_p != 0`, packed path) or makes the Python verifier reject at level 0 (torch path), as
  observed.  For GKR / Ligero the answer is different: `prover.verify` runs `field.ext_mul`, `eq_table` (`eq_outer`
  for `n > 16`), `fold` on the device, i.e. the SAME `gpu/kernels.py` kernels as the prover, so a stale kernel there
  would be invisible to the Python verifier and caught only by the Rust one.  The Rust rejection being in LogUp, not
  in GKR/Ligero, points elsewhere: the level-2 check `eq(rho, x*) [p0 q1 + p1 q0 + lam q0 q1] == running` of the
  low-bit-first schedule -- `rho = [mu] + x*` ordering in `eq_point`, or the `LeafClaim.rho` reversal at the
  boundary -- is where the Rust port and `logup.py` are most likely to differ.  Level 0 (no `rho`) and level 1
  (`rho = [mu]`, a single coordinate so the order cannot matter) pass; level 2 is the first level where the ORDER of
  `rho = [mu, r_1]` matters.  That is the first thing I would diff.
* To rule the cache out on `vy-g5` in one step: rerun with `TRITON_CACHE_DIR=/tmp/fresh` (or the fixed
  `gpu/kernels.py`) and confirm the Rust rejection stays.

## Not done / caveats

* The B = 64 timing (112 s) includes recompilation of every a-gpu kernel (the FK argument changes every cache key);
  the 4096 row uses `--warmup 1` and is a clean median of 3.
* v2 (`/workspace/v2l/pos4096`) re-run only at B = 64 (verified); the v2 B = 4096 timing on the fixed `main` is
  a-gpu-v2's to record (its 5.73 s row was measured on the `W = 31` tree).
* The v1 negatives could not be run: `/workspace/bb/neg` does not exist on `vy-a100b` (a-gpu-v2 exported only
  `pos4096` here; the v1 negatives live on `vy-g5`).  The 52 v2 limb-form negatives were run instead: 52/52 rejected (r20260922-113632-baa3).
* The Rust verifier's rejection is reported, not investigated (a-protocol-diff's lane).

## Status on merged main (lane/a-kernel-a100-2, commit 039926b + this report)

`main` e9e25bb contains this lane (gpu/kernels `FIELD_KEY`), a-protocol-diff (40868e5: the Rust verifier follows
a-gpu2's low-bit-first LogUp sumcheck order, PROTOCOL 4.2) and a-verifier-2 (e130d36: checker-v2 support).  One run
on `vy-a100b` from a fresh worktree off that `main`, default (stale) `~/.triton/cache`, run **r20260922-115019-03ea**:

| set | B | prover median of 3 (s) | reps | own Python verifier | independent Rust verifier (`verity-gkr-verify`, built on the pod from `main`) | proof |
|---|---|---|---|---|---|---|
| v1 `/workspace/bb/pos4096` | 4096 | **2.969** | 2.969 / 2.962 / 2.970 | accepted 3/3, 0.83-0.92 s | **accepted**, 1.94 s (`--threads 12`) | 33.87 MB, 6086 msgs |
| checker-v2 `/workspace/v2l/pos4096` | 4096 | **2.450** | 2.495 / 2.360 / 2.450 | accepted 3/3, 0.99-1.03 s | **accepted**, 2.02 s | 21.13 MB, 11843 msgs |

Both rows are in `ledger/a-kernel-a100.jsonl` (`NON_ZK_PROOF_DIAGNOSTIC`, `verified_by` = the Rust verifier).  So the
"Rust rejects at `LogUp POW level 2`" of the previous section was the pre-merge verifier (fixed by a-protocol-diff),
not a live discrepancy: on merged `main` the kernel-path proof is accepted by an independent implementation at
B = 4096 for both checkers.  The v2 row re-records a-gpu-v2's A100 B = 4096 numbers (5.62 / 5.73 s), which were
taken on the `W = 31` tree before the field change; 2.45 s on merged `main` is the number to quote, and it is faster
than the a-gpu-v2 measurement mostly in `lookup` (0.80 vs 2.78 s) -- a-gpu-v2 should confirm which LogUp path its
rows used before comparing.

**Latent hazard closed.** `packed/kernels_triton.py`, `packed/kernels_fused.py` and `packed/kernels_graph.py` bake
`P`, `MU`, `WR`, `R2` into module-level `tl.constexpr` globals exactly as `gpu/kernels.py` did, so the same stale-cache
failure was possible there (it had not fired only because those modules were never compiled under another field on
these pods).  Every module-level kernel in the three files now takes `FK=FIELD_KEY` (sha256 of `P`, `W`, `R_MONT`) as
an unused constexpr, including the two external `_tree_level_kernel` launches in `packed/logup_graph.py` and
`gpu/logup_packed.py`; no arithmetic changed.  The generated kernels (`_HEADER` / `_generated()`) inline the constants
into their source text and need no key.  Gate, same run: `gpu/v2/tests/test_logup_paths_agree.py` 7/7 passed
(54 s), `PACKED_DEVICE=cuda pytest packed/tests` 63/63 passed (134 s, all kernels freshly compiled under the new keys).  Cost: the first proof after this commit recompiles every kernel (warm-up 304 s v1 / 161 s v2,
excluded from the medians via `--warmup 1`); steady state is unchanged.

**F1 on `vy-g5` (a-verifier's report) -- hypothesis, consistent with both observations, not confirmed.**  The A100
case was: `gpu/kernels.py` binaries compiled under `W = 31` (a-gpu era) served to the `W = 22` tree.  The mirror image
explains a-verifier's F1: on `vy-g5` the a-gpu tree c4d472a (`W = 31`) kernel path proved and verified at 07:44Z
(r20260922-074455-d0b6); a-gpu2 committed `W = 22` (0ec0616) at ~08:15Z and ran its `W = 22` tree on `vy-g5` from
08:26Z (r20260922-082638-110a, -085215-36f1, -090039-bf27); every later a-verifier run of the `W = 31` a-gpu tree on
the same pod (08:43Z onwards: -084329-7c80, -085845-2a26, -090318-2864, -091240-4bf9, -091831-ef04, -092229-641b)
produced kernel-path proofs that both verifiers reject at LogUp level 0, while the torch path (`VERITY_GPU_TORCH_ONLY`)
passed.  Because the source text of `gpu/kernels.py` is identical in both trees, a-gpu2's `W = 22` binaries would be
served to a-verifier's `W = 31` host arithmetic -- the same symptom (kernel `ext_mul` uses the other field's `W`,
5 of 6 coordinates wrong, fractional sum non-zero) with the roles swapped.  It also explains "not reproducible today":
the recorded 4.43 s proof predates the cache poisoning.  Confirming it needs the `vy-g5` cache directory (mtimes /
PTX `mul.lo.s32 ..., 22` vs `31` of the `ext_mul_kernel` entries, as done for the A100 in the evidence trail above);
I did not have that pod.  Both trees now carry `FIELD_KEY`, so the two fields can no longer share a cache entry.
