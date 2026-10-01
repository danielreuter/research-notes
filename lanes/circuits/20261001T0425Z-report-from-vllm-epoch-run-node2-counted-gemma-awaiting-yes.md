---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-10-01T04:25Z · on your 03:52Z handoff

- **The node-2 records count now.** n082, n083, n084 and g091 are relabelled without the held wording. They keep `ov.node 2` and are in my headline
  counts from here on. The feeder no longer adds the held wording.
- **Gemma-2's 33:** staged, not yet released. I can't read Slack from here, so please relay the advisor's yes (or post it in `lanes/vllm-epoch-run/`).
  Then I'll release them below B8 first, with your research question. Packed B8 rows will carry `ov.mps_packed` if the pack takes them.
- **EOS:** g160, n105 and g092 stay labelled fail with the cause, and I'll rerun them when the commit-tokens record lands.
- **TP2 so far (13 released, 2 at a time):**
  - **Pass:** p092, p024, p036, p104 and p047 at B1.
  - **p069**, OLMoE B1: fails closed on TP-12. Its attention all-gathers have no replay stratum.
  - **p051**, Qwen3-4B B8: fails in bounded staging. The warm-up step's plan wasn't pre-learned and exceeds the 4 GiB host budget.
  - Both are with the TP2 lane: `lanes/vllm-tp2-gpuless-build/20261001T0405Z-…-olmoe-tp2-allgather-tp12.md` and
    `20261001T0425Z-…-qwen3-4b-tp2-b8-staging.md`.
  - p081 (Qwen3-30B B1) and p028 (Phi-3-mini B8) are in flight, and the remaining 4 B8 rows follow.
- **#503:** it's merged with main, for your grant, at `7b58692ad` (`20261001T0413Z-report-…-503-merged-with-main-for-grant.md`).
