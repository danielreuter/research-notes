---
id: 20260930T0457Z-ACTION-budget-line-pouw-rtxpro
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# ACTION (RC, cc verity-root): `vy-pouw-rtxpro-`, $25 overnight, PoUW on RunPod RTX PRO 6000 until Daniel's server is reachable

**Approval:** daniel via pous root 04:51Z: a $25 overnight fallback for PoUW on sm_120 until his 8× RTX PRO 6000 server is reachable (the pous root has asked him whether to raise it). Requested by the sm_120 PoUW coordinator (bc-2aa33ad8).

**The line to add to `budgets.toml`:**

~~~toml
"vy-pouw-rtxpro-" = { cap_usd = 25, expires = "2026-09-30T18:00Z", max_pod_hours = 4, by = "daniel via pous root 04:51Z: PoUW sm_120 on RunPod RTX PRO 6000, fallback until his server is reachable" }
~~~

- **Hardware:** 1× RTX PRO 6000 Blackwell Server Edition per pod, RunPod SECURE on-demand, $2.09/h, the same SKU the vLLM port uses. $25 is about 12 pod-hours.
- **The prefix is distinct from `vy-sm120-`** (the vLLM port's $60 line), so neither line draws on the other.
- **Every pod:** `research pods create --max-hours` at or under 4, the bootstrap checks (driver ≥ 575, cc 12.0, 188 SMs) before any work, and runs through `research run`. Clocks are recorded but not locked (a RunPod container can't lock them).

**Planned use** (the guard enforces the $25; the split is the coordinator's plan):

| Pod | Owner | Runs | Expected |
|---|---|---|---|
| `vy-pouw-rtxpro-bench-1` | bc-0de2d624 (harness) | the card's identity and rates; autotuned cuBLASLt and CUTLASS baselines at 8,192³ and m = 32 (BF16, FP8, block-scaled FP8, NVFP4, MXFP4, int8); hash rates | 1.5 h, $3.10 |
| `vy-pouw-rtxpro-fp8cap-1` | bc-e6a46970 | what Pearl-C needs beyond the vLLM lane's FP8 capture: long chains, the FP8 → BF16 mixed chain, the E4M3 cast, the floor, `mxf8f6f4`, W1 prices | 1.0 h, $2.10 |
| `vy-pouw-rtxpro-fp4cap-1` | bc-36186951 | the RTX 5090's NVFP4/MXFP4 models rechecked on the RTX PRO; unscaled E2M1 | 1.0 h, $2.10 |
| `vy-pouw-rtxpro-pearlc-1` | bc-18346d9c | Pearl-C on sm_120: device gates, then kernel attempts at 8,192³ and m = 32 | 3.0 h, $6.30 |
| `vy-pouw-rtxpro-redteam-1` | bc-8b6cc7d8 (independent red team) | GPU attacks on the PoUW lines' assumptions | 3.0 h, $6.30 |
| reserve | coordinator | fix-ups; hashing and attacker timings | $5.10 |

**On Daniel's server,** once it's reachable, the work moves there and this line stops being drawn on.
