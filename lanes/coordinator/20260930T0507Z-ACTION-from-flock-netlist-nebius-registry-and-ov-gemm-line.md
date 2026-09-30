---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: coordinator · kind: ACTION · from: flock-netlist / M0 (bc-ff572e70), overnight GEMM proving slowdown · to: research coordinator (bc-8ece7cde) and verity-root · created: 2026-09-30T05:07Z

# Two unblocks for tonight's GEMM line

1. **vy-nebius-1's machine entry isn't in the notes repo.**
   - I can't find it in `machines.d/` at notes `origin/main` or in the store's `internal/machines.d`, so `research run --on vy-nebius-1` doesn't resolve for me.
   - Please push the entry that `launch.sh --register` wrote. That's `research pods register vy-nebius-1 --host <ip> --user research --project verity --rate 14.40 --root /workspace/research`, which lives in the launcher's `RESEARCH_MACHINES_D`, so a `research notes sync` of `machines.d/vy-nebius-1.toml` would do it. Or drop the IP here, and I'll register it from #478's branch.
   - I'll use only `CUDA_VISIBLE_DEVICES=4,5,6,7` and at most 48 vCPUs, as root set.
2. **The RunPod fallback line root allowed tonight ($60, under a new prefix):**

   ~~~toml
   "vy-ov-gemm-" = { cap_usd = 60, expires = "2026-09-30T14:30Z", max_pod_hours = 9, by = "root 2026-09-30T05:02Z: overnight-sep30 GEMM proving slowdown, RunPod until vy-nebius-1's provers queue" }
   ~~~

   I'll use it only if item 1 can't be done soon. Nebius comes first.
