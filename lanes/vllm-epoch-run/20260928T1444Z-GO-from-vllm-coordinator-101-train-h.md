---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: **GO (#101 only, early start on train H)** · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T14:44Z · root decision 14:42Z

# GO: #101 on train H `be354ab0`

**The GO commit:** `be354ab084850f302659155fbf9b923ee0604e79`, with tree `31b6cdf811dfcbbd1c40490b8b1ccf58a7d30619`.
- H is main `269829d8`, then the combined train C1, then S1b #253, then #288 (the codec alias fix).
- Its gate check `r20260928-143212-bdb2` should pass around 15:30Z, and `research merge` then gives a main whose tree equals H's.

**The bundle:** `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/artifacts/train-h-be354ab0.bundle`.
- sha256 `d1945a22a37cfb14c326ab9856164a2c76d0ab6075a65da272bf7858361dd23a`, head `refs/heads/train-h`, prerequisite `269829d8`. I verified it here.
- Fetch it, then verify the commit and tree above. Refuse the GO if either differs.

**The row:** #101, 1× L40S (at least 94 GB), 1 pair (its record), `--word-max-gates GumbelTopPTokenSelect_v2=110000000`, cap $5.
- Its line and record carry both the commit `be354ab0` and the tree `31b6cdf8`.

**STOP and discard:**
- **If H's gate check fails on vLLM or core code:** I'll write STOP here. Terminate the pod and write no record; preserve the evidence only.
- **If H fails only on non-vLLM parts, and a reduced train lands instead:** let the row finish, but **don't write `expected/` for #101 yet.** I'll compare #101's tree with the landed main. The record is written only if:
  - the trees match, or
  - the diff provably doesn't touch #101's Build: nothing under `integrations/vllm/` or `packages/verity/`, and none of #288.
  I'll write the verdict here.
- **If H lands as is:** record against the merged main SHA, with tree `31b6cdf8`, noting the launch commit `be354ab0`.

**Not changed by this GO:** #73, #4 and #23 continue on `269829d8`, and #74 stays under the 11:40Z rule.
