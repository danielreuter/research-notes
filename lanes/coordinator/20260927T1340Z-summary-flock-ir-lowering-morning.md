---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

**flock-ir-lowering, morning:** Every gateless primitive on the 13 rows is now lowered bit-exact except the MoE expert gathers: #101's top-p keep word (1.45e11 ANDs, 0 mismatches against `topp_keep` on 492 rows incl. 12 at V=128256), the H100 FP8 k-step, Gemma's tanh family and the scalars. Nine rows' headlines are exact; the export was republished 13:00Z (report `internal/lanes/flock-ir-lowering/20260927T1330Z-report-gateless-primitives.md`, docs-site note `20260927T1335Z-note-to-docs-site-boolean-export.md` here).
**Heads and what's left:** #104 `f5531113` ← #125 `a3c1d675` ← #140 `6d168e5a` (stacked, pushed, circuit-check 0 new failures and pins updated on each). Left: your call on whether `GatherBf16x64`/`x128` (rows #67, #68, #70, #75; 66–80% of their headlines as circuits) is a commitment opening like the embedding. A `topp_split` partiality finding for the vLLM coordinator is at `private/flock-ir-lowering-topp-split-half-divergence.md`.
