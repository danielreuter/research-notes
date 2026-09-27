---
cursor:
  subagentId: "bc-12c2f2d9-e73e-510f-ac89-bdda4c1f57d5"
---
# Merge-ready: the MufuEx2Ftz shift clamp, PR #137 (`cursor/vllm-fa2-model-ex2-shift-57d5` @ `7d8a11e4`, base main `928790af`)

lane: vllm-coordinator · kind: handoff · from: vllm-rf-normtap (bc-12c2f2d9) · created: 2026-09-27T09:02Z

This answers `20260927T0810Z-handoff-from-vllm-coordinator.md` and `20260927T0842Z-handoff-from-vllm-coordinator.md`.
[PR #137](https://github.com/danielreuter/verity/pull/137) is a draft. All pods are terminated (about $0.54 in all). The L40S
hardware check was added at 09:22Z, as item 3.

## The fix

A right shift of 24 or more now gives 0. `mant` has 24 bits, so K = floor(|x|·2^23) exactly, and every 0 < |x| < 2^-23 reads
T[0] = 1.0 at n = 0, for either sign.

- **Two more copies than the finding named.** The IR prim `MufuEx2Ftz` does not have its own copy: it calls the same
  `mufu_ex2_words`. Four implementations copied the wrap, and all change in #137:
  - the numpy twin `derived_rows.mufu_ex2_ftz`, which wrapped with `(-unb) & 63` on purpose;
  - the SP1 table gate `backends/sp1/common/src/ftz.rs` `ex2_reduce`, which used `wrapping_shr`, and whose unit test pinned
    ex2(2^-64) = 2.0;
  - flock's tail verifier `backends/flock/live/src/ir_tail.rs` `mufu_ex2`: a plain `>>`, which panics in debug builds and wraps
    in release builds;
  - `mufu_probe.cu`'s device model.
- **Please route this to the owners.** flock-ir-lowering, who reported the bug, and the SP1 backend should know that their files
  move in #137.
- **Why the clamp is the verified rule.** The exhaustive sm_89 verification ran `model_ex2` on the device against the hardware.
  The device clamps the shift, so the 0-mismatch result pinned the clamped rule, not the host's mod-64 wrap.
  Confirmed on the L40S (item 3): main's undefined-shift build also verifies with 0 mismatches.
- **Other constraints.**
  - `derived_rows.py` stays at its P10 cap of 944 lines.
  - The id stays `MufuEx2Ftz_v1`, because the prim is defined as the measured instruction. If you want a `_v2`, that is a
    mechanical follow-up.

## Evidence against the 08:10Z list (runs `r20260927-083954-0e10`, `-083926-9946` head, `-083933-6d1c` base)

1. **Every exponent class.**
   - The new test `test_ex2_every_exponent_class_equals_the_exact_rule` checks 8,192 words: 256 exponent classes × 2 signs × 8 edge
     and 8 seeded mantissas, NaN and inf included. The compiled rule, the IR reference `verity.evaluation.evaluate(P.MufuEx2Ftz)`
     and the numpy twin all equal the rule evaluated in exact arithmetic (`Fraction`). Every 0 < |x| < 2^-23 gives 1.0, and so do
     6.5e-22 and ±2^-64.
   - Exhaustive over all 2^32 words: the fixed C++ equals the fixed numpy twin, with 0 mismatches, and all 1,728,053,248 words
     with biased exponent 1..103 give 1.0.
   - SP1 `mufu_ex2_tab` and flock `mufu_ex2`, compiled standalone, are chunk-sha256-equal to the C++ over all 2^32 words.
   - `cargo test --release -p veritor-zk-common`: 136 passed, 0 failed.
2. **Edge vectors in the self-check.**
   - The new test `test_attention_kernels_on_scores_below_two_to_the_minus_63` uses scores near ±2^-66, which put the P and rescale
     ex2 inputs at 2^-87 ≤ |x| < 2^-63. `self_check` of the Attention_v3 twin and of its row kernel equals the reference, and the
     reference equals the q = 0 instance.
   - Both new tests fail on main's code. The attention output there is 15940 against 15938 in the first word.
   - `packages/verity/tests/evaluation`: 36 passed.
3. **L40S hardware check (approved 09:08Z): the hardware equals the fixed rule on all 2^32 inputs.** Run `r20260927-091756-2451`
   on an L40S (sm_89, driver 580.126.09, nvcc 12.4).
   - `mufu_probe.cu` `verify` (FRAC_MODE 4) against the **pinned** tables gives 0 ex2 and 0 rcp mismatches over all
     4,294,967,296 inputs. That holds for #137's device model, with the explicit clamp, and for main's, with the undefined shift.
   - So the device does clamp the shift, which is why September's verification passed, and the fixed host rule now matches the
     hardware.
   - The L40S's own measured ex2 and rcp tables equal the pinned ones: 0 differing entries, u32 sha256 `b2a42c4a…` and `c4083814…`.
   - `probe` landmarks, hardware = model:
     - 1.0 for 6.5e-22, ±2^-64, ±2^-87 (biased exponent 40), ±(2−2^-23)·2^-64, biased exponents 39 and 64, and ±2^-24. The old
       host rule gave 1.0083, 2.0 and 0.5, and 0x3f800001.
     - 2^-23 gives 0x3f800001 and −2^-23 gives 0x3f7ffffe.
   - The first attempt, `r20260927-091119-53cc` on `vyv-rf-normtap-g6`, proved nothing: nvcc was not on the run's PATH. The
     script now finds `CUDA_HOME` as `pod_fa2_tap.sh` does.
   - Evidence: `lanes/vllm-rf-normtap/evidence/ex2-shift/l40s/`.
4. **No recorded replay changes.**
   - **What changes.** Main and the fix differ on exactly 402,653,184 words: every word with biased exponent 40..63, both signs, so
     2^-87 ≤ |x| < 2^-63. For exponents 1..39 the wrapped count was still 24 or more.
   - **No stored operands.** #101's stored record keeps no attention operands. The capture's `values/` holds 100 files of 4–8 bytes,
     and the sampled replay keeps verdicts only.
   - **The bound.** An FA2 P input in (0, 2^-63) needs |max_scaled| < 2^-15, which at D = 64 is a |row max| below 1.7e-4, or else a
     row max of exactly 0 together with tiny scores. The argument is by granularity: the exact product s·scale_log2 is a multiple of
     2^(E_s+E_l−46). A rescale input there needs both running maxima below about 2^-37.
   - **The samplers.** Top-p's `tl_exp` feeds ex2 t = x·log2e, where x is a difference of f32 logits, so t is either 0 or at
     least about one ulp of those logits. MoE's `NvExpf` feeds ex2 its reduced fraction x·log2e − j. That is tiny only when
     |x| < ~2^-62, or when x·log2e falls within 2^-63 of a nonzero integer. I have not swept that second case; no MoE row is
     #101's.
   - **The data: #101's committed layer-0 FA2 streams from the #102 L40S run `0f64`.**

     | Step | Visited blocks | Min \|row max\| | Min \|max_scaled\| | Zero maxima | Rescale inputs in exponents 1..63 | Smallest nonzero rescale input |
     |---|---|---|---|---|---|---|
     | 0 (prefill) | 12,288 | 0.433 | 0.078 | 0 | 0 of 4,096 | 5.3e-4 |
     | 1 (decode) | 96 | 1.73 | 0.313 | 0 | 0 of 64 | 0.053 |

     No ex2 input of those rows changes. The data covers layer 0 only; the other layers rest on the bound.
   - The record's sampled replay has 0 mismatches. That is consistent with the above: at an affected input, the old model would
     have disagreed with the hardware.
5. **Gate (b) on CPU.** Base `928790af` against head `7d8a11e4`:
   - The head adds the two new tests, both passing.
   - 0 outcome changes, 0 new failures, 0 new skips.
   - 50 failures and errors on both sides, the same set: the CPU pod's missing CUDA device and the real-HF model tests.
   - Lints rc 0 on both.

## Where things are

- **Evidence:** `lanes/vllm-rf-normtap/evidence/ex2-shift/` (`summary.json`, `sweep.json`, `census.json`, the new-test logs on the
  fix and on main, the SP1 test log, `jdiff-928790af-vs-7d8a11e4.txt`, `test-diff-928790af-7d8a11e4.patch`).
- **Pod scripts:** `evidence/pod-scripts/ex2_fix.sh`, `ex2_sweep.py`, `ex2_census.py`.
- **Spend:** about $0.54, every pod terminated:
  - CPU `vyv-rf-normtap-c4` (`c4pymranf1lyv7`), 08:38Z–09:00:08Z, about $0.35;
  - L40S `vyv-rf-normtap-g6` (`l2a814o1cnjeqs`), 09:10:52Z–09:16:15Z, about $0.10;
  - L40S `vyv-rf-normtap-g7` (`0tddzjvfzpeq2s`), 09:17:10Z–09:21:57Z, about $0.09.
  The L40S total, about $0.19, is inside the approved $0.30 (cap $0.60). Estimates come to you before any further pod.

## Appendix: the test diff (`git diff 928790af 7d8a11e4 -- integrations/vllm/tests backends/sp1/common/src/ftz.rs`)

~~~diff
diff --git a/backends/sp1/common/src/ftz.rs b/backends/sp1/common/src/ftz.rs
index 7c0dfcb3..79d73762 100644
--- a/backends/sp1/common/src/ftz.rs
+++ b/backends/sp1/common/src/ftz.rs
@@ -182,11 +182,11 @@ fn table_word(row: u64, expected_index: u64) -> Option<u64> {
 /// `(n, j)` with `ex2(x) = T[j] * 2^n`.  `None` for the words the C rule answers before
 /// touching the table (`e == 0xFF`, `e == 0`, `unb >= 30`).
 ///
-/// `mant >> (-unb)` in the C model is a variable 64-bit shift; both x86-64 and AArch64
-/// take the amount mod 64, and the exhaustive sm_89 verification (all 2^32 inputs, 0
-/// mismatches, attention-model.md §3.1) pinned exactly the compiled behaviour, so the
-/// mod-64 shift *is* the registered semantics (`derived_rows.mufu_ex2_ftz` replicates
-/// it, `wrapping_shr` here).
+/// `K = floor(|x| 2^23)` exactly: `mant < 2^24`, so every right shift of 24 or more is
+/// `0` and each `|x| < 2^-23` reads row 0 at `n = 0` (`ex2 = 1.0`, either sign).  The C
+/// model clamps the shift (a count >= 64 is undefined there), `checked_shr` here: the
+/// exhaustive sm_89 verification (all 2^32 inputs, 0 mismatches, attention-model.md §3.1)
+/// ran the model on the device, where the shift clamps.
 fn ex2_reduce(x: u64) -> Option<(i64, u64)> {
     let ax = x & 0x7FFF_FFFF;
     let e = (ax >> 23) as i64;
@@ -201,7 +201,7 @@ fn ex2_reduce(x: u64) -> Option<(i64, u64)> {
     let k: u64 = if unb >= 0 {
         mant << unb
     } else {
-        mant.wrapping_shr((-unb) as u32)
+        mant.checked_shr((-unb) as u32).unwrap_or(0)
     };
     let fixed: i64 = if x & SIGN == 0 {
         k as i64
@@ -381,9 +381,21 @@ mod tests {
         assert_eq!(ex2_reduce(f(-1.0)), Some((-1, 0)));
         // x = -0.5: K = 0x400000, fixed = -K - 1 -> n = -1, j = 2^23 - 1 - 0x400000
         assert_eq!(ex2_reduce(f(-0.5)), Some((-1, 0x3F_FFFF)));
-        // x = 2^-64: shift 64 mod 64 = 0 -> K = mant -> n = 1, j = 0 (the pinned compiled behaviour)
-        assert_eq!(ex2_reduce(f(2f32.powi(-64))), Some((1, 0)));
+        // x = +-2^-64 (a shift by 64) and every other |x| < 2^-23 (biased exponent 1..=103): K = 0 -> n = 0,
+        // j = 0, so ex2 = T[0] = 1.0 for either sign
+        assert_eq!(ex2_reduce(f(2f32.powi(-64))), Some((0, 0)));
         assert_eq!(ex2_reduce(f(2f32.powi(-63))), Some((0, 0)));
+        for e in 1u64..=103 {
+            for m in [0, 1, 0x40_0000, MANT] {
+                for s in [0, SIGN] {
+                    let x = s | e << 23 | m;
+                    assert_eq!(ex2_reduce(x), Some((0, 0)), "{x:#010x}");
+                    assert_eq!(mufu_ex2_tab(x, F32_ONE), Some(F32_ONE), "{x:#010x}");
+                }
+            }
+        }
+        assert_eq!(ex2_reduce(f(2f32.powi(-23))), Some((0, 1)));
+        assert_eq!(ex2_reduce(f(-(2f32.powi(-23)))), Some((-1, MANT - 1)));
         assert_eq!(ex2_reduce(0), None);
         assert_eq!(ex2_reduce(EXP), None);
         assert_eq!(ex2_reduce(f(2f32.powi(30))), None);
diff --git a/integrations/vllm/tests/program/test_derived_rows.py b/integrations/vllm/tests/program/test_derived_rows.py
index d10d6db2..c7e1b299 100644
--- a/integrations/vllm/tests/program/test_derived_rows.py
+++ b/integrations/vllm/tests/program/test_derived_rows.py
@@ -8,7 +8,9 @@ tables load from the committed sweep artifacts); skipped when unavailable."""
 
 from __future__ import annotations
 
+import math
 import sys
+from fractions import Fraction
 from pathlib import Path
 
 import numpy as np
@@ -88,6 +90,54 @@ def test_unary_kernels_match_prims(fn_np, prim):
     assert not bad, (prim, len(bad), bad[:5])
 
 
+def _ex2_exact(w: int, T: np.ndarray) -> int:
+    """`ex2.approx.ftz.f32` of the word `w` from the rule's statement, in exact arithmetic on the input's value:
+    K = floor(|x| 2^23), q = K div 2^23, r = K mod 2^23; x >= 0 reads T[r] * 2^q, x < 0 the ones' complement of the
+    fraction, T[2^23-1-r] * 2^-(q+1), carried to T[0] * 2^-q when r = 0; +inf from 2^128, +0 below 2^-126."""
+    x = float(np.uint32(w).view(np.float32))
+    if x != x:
+        return 0x7FFFFFFF
+    if w & 0x7F800000 == 0:                                        # ftz: +-0 and every subnormal read as 0
+        return 0x3F800000
+    if math.isinf(x):
+        return 0 if x < 0 else 0x7F800000
+    q, r = divmod(math.floor(abs(Fraction(x)) * 2 ** 23), 2 ** 23)
+    n, j = (q, r) if x > 0 else ((-q, 0) if r == 0 else (-q - 1, 2 ** 23 - 1 - r))
+    if abs(n) > 300:
+        return 0x7F800000 if n > 0 else 0
+    v = Fraction(float(np.uint32(T[j]).view(np.float32))) * Fraction(2) ** n
+    if v >= 2 ** 128:
+        return 0x7F800000
+    if v < Fraction(2) ** -126:
+        return 0
+    return int(np.float32(float(v)).view(np.uint32))
+
+
+def test_ex2_every_exponent_class_equals_the_exact_rule():
+    """`MufuEx2Ftz` on every exponent class of both signs (edge and seeded mantissas; NaN and inf at 255): the compiled rule
+    (`fa2_model.mufu_ex2`), the IR reference (`verity.evaluation.evaluate`) and the numpy twin equal the rule evaluated
+    exactly, and every 0 < |x| < 2^-23 gives T[0] = 1.0.  That includes |x| < 2^-63, where the C shift count reached 64 or
+    more (undefined; x86-64 took it mod 64: ex2(6.5e-22) was 1.0083, ex2(2^-64) 2.0 and ex2(-2^-64) 0.5)."""
+    D = _derived()
+    from verity.evaluation import evaluate
+    from verity_vllm.program.kernels import fa2_model as FA
+    from verity_vllm.program.registry import prims as P
+    tabs = D._fa2_tables()
+    mants = np.concatenate([[0, 1, 2, 0x3FFFFF, 0x400000, 0x400001, 0x7FFFFE, 0x7FFFFF],
+                            np.random.default_rng(64).integers(0, 1 << 23, 8)]).astype(np.uint32)
+    e = np.arange(256, dtype=np.uint32)
+    xs = ((np.arange(2, dtype=np.uint32)[:, None, None] << 31) | (e[None, :, None] << 23) | mants[None, None, :]).reshape(-1)
+    want = np.array([_ex2_exact(int(w), tabs.ex2) for w in xs], dtype=np.uint32)
+    assert np.array_equal(FA.mufu_ex2(xs.view(np.float32), tabs).view(np.uint32), want)
+    assert np.array_equal(D.mufu_ex2_ftz(xs), want)
+    assert [evaluate(P.MufuEx2Ftz, int(w))[0] for w in xs] == want.tolist()
+    ex = (xs >> 23) & 0xFF
+    tiny = (ex >= 1) & (ex <= 103)
+    assert int(tiny.sum()) == 2 * 103 * mants.size and (want[tiny] == 0x3F800000).all()
+    words = np.array([np.float32(6.5e-22).view(np.uint32), 0x1F800000, 0x9F800000], dtype=np.uint32)  # 6.5e-22, +-2^-64
+    assert D.mufu_ex2_ftz(words).tolist() == [0x3F800000] * 3
+
+
 def test_binary_kernels_match_prims():
     """NaN-operand pairs are excluded from the plain add/sub/mul comparisons: the registered prims
     evaluate those through host scalar arithmetic, whose NaN *payload propagation* is host-defined
diff --git a/integrations/vllm/tests/program/test_kernel_self_check.py b/integrations/vllm/tests/program/test_kernel_self_check.py
index 5378b6c0..da854ff6 100644
--- a/integrations/vllm/tests/program/test_kernel_self_check.py
+++ b/integrations/vllm/tests/program/test_kernel_self_check.py
@@ -33,3 +33,37 @@ def test_kernel_matches_the_reference(key, kernel):
         sc = self_check(t, kernel=kernel, n=N, seed=0)
         assert sc.ok, str(sc)
         assert sc.declined < sc.n, f"{t.id}: {kernel} declined all {sc.n} instances"
+
+
+def test_attention_kernels_on_scores_below_two_to_the_minus_63(monkeypatch):
+    """Edge vectors for the attention kernels' self-check: scores near +-2^-66 put the P and rescale ex2 inputs at
+    2^-87 <= |x| < 2^-63, where the C rule's shift count reached 64 (undefined; the host took it mod 64) and MUFU.EX2 reads
+    T[0] = 1.0.  The twin and the row kernel equal the reference there, and the reference equals the same instance with
+    q = 0, whose every ex2 input is 0."""
+    from verity.evaluation import evaluate
+    from verity.ir.defs import bind
+    from verity_vllm.program.kernels import derived_rows as DR
+    from verity_vllm.program.registry import b1
+
+    statics = {"T": 20, "NH": 2, "KVH": 1, "D": 16, "BN": 16}
+    target = bind(b1.AttentionV3, **statics)
+    bf16 = lambda a: (np.asarray(a, dtype=np.float32).view(np.uint32) >> 16).astype(np.uint16).reshape(-1)  # noqa: E731
+    k, q = np.zeros((20, 16)), np.zeros((2, 16))
+    k[:, 0] = 2.0 ** -33 * (1 + np.arange(19, -1, -1) / 64)   # head 0's max is in block 0, visited last: a tiny rescale input
+    q[:, 0] = [2.0 ** -33, -(2.0 ** -33)]
+    v = np.random.default_rng(3).standard_normal((20, 16))
+    tiny, zero = [bf16(q), bf16(k), bf16(v)], [bf16(0 * q), bf16(k), bf16(v)]
+
+    seen: list[np.ndarray] = []
+    ex2 = DR.mufu_ex2_ftz
+    monkeypatch.setattr(DR, "mufu_ex2_ftz", lambda x, table=None: seen.append(np.asarray(x).reshape(-1)) or ex2(x, table))
+    got = rows.ROWS["Attention_v3"].fn(statics, tiny)["out"]
+    monkeypatch.undo()
+    xe = (np.concatenate(seen) >> 23) & 0xFF
+    assert np.count_nonzero((xe >= 40) & (xe <= 63)) > 0 and not np.any((xe >= 104) & (xe < 255))
+
+    ref = [evaluate(target, *(a.tolist() for a in inst)) for inst in (tiny, zero)]
+    assert ref[0] == ref[1] and got.tolist() == list(ref[0])
+    for kernel in (twins.KERNEL, rows.KERNEL):
+        sc = self_check(target, kernel=kernel, inputs=[np.stack(pair) for pair in zip(tiny, zero)])
+        assert sc.ok and sc.declined == 0, str(sc)
~~~
