---
id: 20261008T0150Z-report-from-vllm-config-run-tp2-gaps-superseded-in-main
campaign: overnight-sep30
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: vllm-config-run-tp2 (bc-35ab914e), follows note:20261001T0915Z-report-from-vllm-config-run-tp2-p081-moe-gap-fixed
---

# @circuits: this lane's TP2 gaps have landed in main through other commits; I recommend standing it down

I've had no reply to my 1 Oct reports. Checking `origin/main` (`88d50358de0`), it already has this lane's work:

- **Staging (p051, p108, p040):** `408982c0830`, "a TP Commit's warm-up is bounded staging's learn-only pass on every rank".
- **Qwen3-MoE sites (p081, p085):** `0452f816427`, "a mid-module collective site counts only the calls its instance's flags allow".
- **OLMoE q/k gathers (p069, p073):** `f6697c66e2e`, the predict build all-gathers q and k under TP, and its message says cov-p069 and cov-p073-3 equal the traced Builds.
- **Gemma-2 TP2 (p058):** the softcap moved to boolean rows (`53a46a7639b`, `b844c2a69b6`). Nothing I found names p058's two producers of `out`, so whether it passes is still unconfirmed.

`cursor/tp2-gaps-3847` (`bf14650c8`, no PR) is superseded, and nobody needs to merge it.

**Recommendation:** stand this lane down. If you want p058 confirmed, send me that one row and I'll run it on current main. Until you answer, I'm slowing this lane's inbox check from every 20 minutes to every 2 hours, because each check sends you and Daniel a message.
