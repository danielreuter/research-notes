---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: vllm-coordinator · kind: handoff · from: vllm-serving-commit (bc-819f6247) · created: 2026-09-27T09:27Z

# LAUNCH: A4 run 1 (P4) on `vyv-rf-serving-commit-g3`, about 25 min, about $0.45 (root's line: $3 for P4, P6 and a fix-up)

- **Pod and run:** `vyv-rf-serving-commit-g3` (`mz0r7yvldlz5bt`, 1× L40S secure, $1.09/h, guard 90), run `r20260927-092505-bee3`.
  Expected end about 09:55Z.
- **What it runs:**
  - #101 with `SERVING_ROWS` = P4's partition file (`46f80472…`, scope `model.layers.0.`). That commits every layer-0 unit of RMSNorm
    Triton (287), RoPE (11,480), RMSNorm fused (287) and SiLU·mul (287): N = 12,341.
  - On the pod, `sc_members.py served`: the served rows equal the captured instances in scope, and each member's `m<k>-pub/inst`
    equals M0 `68ae79f2`'s own `write()`.
- **Conditions met before launch:**
  - the e2e lane's layouts (0905Z, 0913Z);
  - P4 rebuilt with the same digest, bases and ports;
  - on CPU, all four members' files are byte-identical to M0 `68ae79f2`'s `write()`;
  - the default path is byte-identical (`90f81868`, file `9e010897`, on head and on main `928790af`);
  - lints and unit tests pass.
- **#119's tip moved.** The code is `7d4f4b7e` on `lane/vllm-serving-commit`, which is #119's branch, so the merge-ready handoff at
  `5581920f` needs a gate (b) rerun on the final head. I'll rerun it after P6 (M0's shared-row writer landed at `967b8d06`), then
  re-send merge-ready.
