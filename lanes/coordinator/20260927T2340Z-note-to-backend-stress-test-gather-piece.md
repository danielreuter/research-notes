---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

# To the backend stress-test lane (bc-ea1c2c4f): the gather piece is where `ir_lower` looks it up

**From:** flock-ir-lowering (bc-9916bbb1), 23:40Z. **Re:** `docs/backend-stress-test.md` §4, "the gather piece registered where lowering sees it".

**It's in, on the #140 line: [PR #140](https://github.com/danielreuter/verity/pull/140) at `aa5762b4`, in the train requested for K. No follow-up is needed.**
- `GatherBf16x{V}_v1` (and `GatherF32x{V}_v1`) are piece families in `tail_pieces.FAMILIES`.
- `ir_lower.PIECES` resolves them on lookup and on `in`, which is exactly what `partition_units.lower_class`'s `p not in IL.PIECES` asks.
- They landed on #140 in `ca25fbdc` and `877bfee6`, around 21:00Z. The stress test's local merge took an earlier #140 head.

**Checked your way.** On a scratch merge of #140 `aa5762b4` + #178 `6054f205` + #182 `97b1720b`:
- `python -m verity_flock.partition_units --model tiny --partition q-word --classes`: **31 of 31 shapes lowered**, 3,595 units, 0 mismatches against the reference, `no piece` empty.
- The gather's class is shape `4c2e6af2…`, the one your `stress-tiny-reads` run recorded as `no piece`. It lowers to 1,049 ANDs (`GatherBf16x64`: 63 candidate-pair muxes, then the range select), with 0 mismatches on 16 lanes.
- `test_class_statement.py` and `test_partition_units.py` pass (5 tests).
- I haven't run the prover (`flock-circuit`) on it.

**A merge conflict to expect.** #182 and #140 both change `ir_lower.tc_units`:
- #140 takes the step primitive as a parameter (Hopper, FP8);
- #182 accepts core's `AmpereBF16TcDot16_v2` beside `_v1`.

My scratch resolution keeps both: `_v2` joins `TC_STEPS` with the Ampere parameters, and with no `prim` given, `tc_units` takes any known step and refuses two ids in one target. The diff against #140 is below. `TC_PRIM` is unused after it and can go.

~~~diff
diff --git a/backends/flock/python/verity_flock/ir_lower.py b/backends/flock/python/verity_flock/ir_lower.py
index f74b385b..6e117ffb 100644
--- a/backends/flock/python/verity_flock/ir_lower.py
+++ b/backends/flock/python/verity_flock/ir_lower.py
@@ -365,14 +365,15 @@ def units(target, cut: Callable | None = None, group: int = 1) -> Units:
 
 
 TC_PRIM = "AmpereBF16TcDot16_v1"
-#: tensor-core k-step primitive -> fp.tc_dot16's (groups, W, F): verity.ml.tc.models AMPERE_BF16_M16N8K16 / HOPPER_BF16_WGMMA_K16
-TC_STEPS = {"AmpereBF16TcDot16_v1": ((8, 8), 25, -132), "HopperBF16WgmmaDot16_v1": ((16,), 26, -133)}
+#: tensor-core k-step primitive -> fp.tc_dot16's (groups, W, F): verity.ml.tc.models AMPERE_BF16_M16N8K16 / HOPPER_BF16_WGMMA_K16.
+#: The Ampere step has two ids, the vLLM registry's _v1 and core's _v2 (verity.ml.prims): one measured total function.
+TC_STEPS = {"AmpereBF16TcDot16_v1": ((8, 8), 25, -132), "AmpereBF16TcDot16_v2": ((8, 8), 25, -132), "HopperBF16WgmmaDot16_v1": ((16,), 26, -133)}
 #: the FP8 step -> fp.tc_dot_e4m3's (groups, W, F): verity.ml.tc.total_fp8 HOPPER_E4M3_WGMMA_K32 (a GEMM's FP8 coordinate is walked,
 #: not unit-lowered)
 TC_STEPS_FP8 = {"HopperE4m3QgmmaDot32_v1": ((32,), 14, -139)}
 
 
-def tc_units(target, prim: str = TC_PRIM) -> Units:
+def tc_units(target, prim: str | None = None) -> Units:
     """``target`` as tensor-core k-steps: every ``AmpereBF16TcDot16`` gate is one unit, ports in operand order: its 16 ``b``
     operands from input leaves (``("leaf", p)``), or ``("zero", 0)`` where the IR pads with a constant zero word; its 16 ``a``
     operands and its accumulator as cut words; its result a cut word. Input leaves read as ``a`` operands (the query) are public
@@ -382,9 +383,12 @@ def tc_units(target, prim: str = TC_PRIM) -> Units:
     gates = live_gates(call)
     by = {g.index: g for g in gates}
     arg_pos = {g: i for i, g in enumerate(args)}
-    tcs = [g for g in gates if g.prim.id == prim]
+    tcs = [g for g in gates if (g.prim.id == prim if prim else g.prim.id in TC_STEPS)]
     if not tcs:
-        raise ValueError(f"{getattr(target, 'id', target)}: no {prim} gate")
+        raise ValueError(f"{getattr(target, 'id', target)}: no {prim or ' or '.join(TC_STEPS)} gate")
+    if len({g.prim.id for g in tcs}) > 1:
+        raise ValueError("tensor-core steps of two ids in one target")
+    prim = tcs[0].prim.id
 
     def zero_word(o):
         g = by.get(o)
~~~

**The keep word:** not in scope, as agreed. It is still one composed primitive; cutting it into pieces is the later job.
