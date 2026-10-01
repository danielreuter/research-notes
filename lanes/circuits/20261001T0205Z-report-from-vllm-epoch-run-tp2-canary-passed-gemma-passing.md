---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits, cc vllm-tp2-gpuless-build · created: 2026-10-01T02:05Z

- **The TP2 canary on the token-budget fix passed.** p047 (Qwen3-4B TP2 B1, head_dim 128) is `r20261001-015257-ea78`.
  - Its replay was 460/460, summed over both ranks.
  - Its Build digests equal those of the crashed attempt (step `dff20b55…`/`98620d04…`), so the fix moved nothing.
  - Its run root `bd0177d9495c44e6` equals the TP2 lane's run D, `r20261001-004454-795e`, from a different tree.
  - **The TP2 subset is out:** 13 deployments, B1 first, 2 at a time, paced by release.py. That's the reruns of p092, p024, p036 and p104, plus
    OLMoE, Qwen3-30B-A3B, Qwen3-4B, Phi-3-mini, Qwen2.5-1.5B/7B and Mistral-7B at B8.
  - All 5 TP2 deployments landed so far pass: p000, p012, p004, p016 and p047.
- **Gemma-2 passes on sm_120:** k06 (B1 256/15 greedy), m006 (B8 greedy) and n035 (B8 top-p) are each 460/460. m003, n031 and n043 are running.
  - Note the slowdown: wall ×75 (k06), ×184 (m006) and ×165 (n035), from host evaluation in the Commit.
  - In vllm-coverage-defs' run, m006's Commit held its GPU about 1,050 s. Worth knowing before the other 33 are released.
- **Gumbel subset:** 15 of 21 pass. 1 fails (g160, the EOS finding in `20261001T0145Z-finding-…-config-run-eos-fail-closed.md`), and 5 are running.
