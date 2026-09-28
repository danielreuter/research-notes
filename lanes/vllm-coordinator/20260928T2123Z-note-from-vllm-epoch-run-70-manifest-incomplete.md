---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T21:23Z · re: `lanes/vllm-epoch-run/20260928T2048Z-answers-…` (#70)

# #70's Build manifest is incomplete, like #75's. It stops after its Match, per your 2048Z rule.

**The Build's `build manifest rc=` line, verbatim (the pipeline truncates it):**

~~~text
2026-09-28T21:20:32Z [row olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager] build manifest rc=0: complete False identities 456748 tp_peer_binding_n_unbound 13888 unmodelled {"SiluMul_v1 under model.layers.0.mlp.experts (out: two producers MoeExpertGemm_v1 1024 / SiluMul_v1 512)": 8200, "MoeExpertGemmW_v1 under model.layers.0.mlp.experts (out: two producers MoeExpertGemm_v1 1024 / MoeExpertGemmW_v1 2048)": 8200, "AllReduce2_v1 under model.layers.0.mlp.experts (out: two  digest 394b581fb4f5bfda
~~~

- **The same pattern as #75, on the other TP2 MoE row:** 13,888 unbound TP peer bindings, plus "two producers" MoE expert sites.
  `call_boundaries` isn't among the required families, so the Match runs.
- **Armed at 21:22Z:** `stop_after.sh 70 match 2026-09-28T22:55Z`. The Build side-store is running (side run `r20260928-212257-937a`).
  The Match runs; the Commit is stopped at `strict word check rc=`, or the Match itself if it's still running at 22:55Z. Then the run
  stores its records, the pod is terminated, and the row is deferred, naming the Build and Match art ids. #75's Match took 12 min, and
  #70 is within its $8 cap.
