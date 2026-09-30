---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: handoff (merge request) · from: vllm-coordinator · created: 2026-09-30T16:15Z

# Granted: [#569](https://github.com/danielreuter/verity/pull/569) and [#568](https://github.com/danielreuter/verity/pull/568). Together they get Gemma-2 on sm_120 past the Build

| PR | Head | What |
|---|---|---|
| #569 | `9194732666709c624551cc54f68c652f3b78b435` | `AttentionSoftcap_v2` replay row evaluator (#551's follow-up); exact on 8,368 rows on the PRO 6000, with the 14 non-finite rows declined to the reference |
| #568 | `0ba8865b009480a4b490e788bb50acbaff9457c6` | call boundaries: a body may read a weight-only Call of another step; Gemma-2 goes from 727/8,805 to 8,805/8,805 covered |

- Both are `integrations/vllm/` only, clean on main `6a815cc7` and with each other. The lints, the dead-module check and their tests pass locally. No digest moves.
- **Still queued and granted:** #561, #562, #563 and #499 (TVK and after), #228 and #250.
