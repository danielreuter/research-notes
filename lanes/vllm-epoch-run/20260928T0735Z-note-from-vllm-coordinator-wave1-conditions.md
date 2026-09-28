---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: note (NOT GO) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T07:35Z

# The wave-1 GO conditions, and one pre-Commit check

**This is not a GO.** Create no pods yet.

**When GO comes:** I'll write it here once #197, #221, #223, #231, S2 (#233), S3 (#242), S4 (#246) and S1 (#232) are on main, naming the exact main SHA.
- Wave 1 is the 10 clean rows: #101, #4, #23, #60, #67, #68, #70, #75, #73 and #11.
- It does **not** wait for S1b (#253).

**Wave 2 (#74, #57, #39):** a separate GO, after S1b's per-request fix and #244 are on main.

**The pre-Commit check, on every wave-1 row:** after `manifest build`, read the manifest's `query.required_families`.
- If it contains `call_boundaries`, don't run the Commit. Stop the row and write me a one-line note.
- The row then moves to wave 2, and its old record stays.
- This matters most for #11. Its Program has never been checked for Call boundaries (0.9 GB, too big for the VM), though it's expected to be 0 like #23 and #101.
- The prep lane measured the other nine at 0 extra values.

**#101:** `--word-max-gates GumbelTopPTokenSelect_v2=110000000`, on a pod with at least 60 GB of RAM (the sampler cut).
