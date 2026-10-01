---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-10-01T05:30Z · on your 05:09Z handoff (cg04 word check)

# cg04's word-check fail is the submitted env, not a Definition limit: the grid cell raises that Call's MAX_GATES, and n031 passes with it

- **Same failure, three rows:** cg02 (B1 1k top-p), cg03 (B1 1k Gumbel) and cg04 (B1 256 Gumbel) all fail the Build's word check the same way:
  `GumbelTopPTokenSelect_v2{V=256000,S=32}: too-large` under Q_word_v1 W=32. The top-p row uses the same Call.
- **Why it's the env, not the Definition:**
  - Every Gemma-2 stochastic cell in the grid sets `VERITY_QWORD_MAX_GATES` and `VERITY_QWORD_MAX_GATES_ALLOWED` to
    `GumbelTopPTokenSelect_v2=225000000`, plus `BUILD_TIMEOUT=14400`. Its note tail is "sampler Call one unit (MAX_GATES raised to 225000000)".
  - The cg items were submitted with m003-3's env. m003 is greedy and has neither setting.
  - n031, the same B1 sampler Call (Gemma-2 B1 256/32 top-p) submitted with the cell's env, passes 460/460 (`r20261001-024546-40ec`).
  - B8 and up build without the raise: cg08 passes, cg14 builds. So only the B1 stochastic rows are hit.
- **Labelled:** n032 (cg04), n033 (cg02) and n034 (cg03) are labelled `fail`, "sweep configuration, not the deployment", with this cause, not the
  Definition one.
- **Ask:** may I rerun those three with the cell's env? They're CPU Builds of about 25 min each, and their Commits go through release.py as
  usual. Until you say so, I'm holding them, as your 05:09Z handoff says.
- **The Gemma-2 TP2 canary fails at the Build.** p058 (`r20261001-051040-a589`) has an incomplete manifest at TP2. Under `logits_processor`, the
  softcap scaling after the vocab all-gather gives one output two producers (AllGather2_v1 and Bf16MulScalar_v1, both 256000 wide). The other 10
  Gemma-2 TP2 rows stay held. Sent to the TP2 lane, cc vllm-coverage-defs.
- **Passes since 05:00Z:** n036 (cg08, B8 256 Gumbel) and n043 (B32 256 top-p, the watchdog rerun: wall ×932, 460/460).
