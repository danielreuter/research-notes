---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

20260930T1856Z: vllm-staging-bug done: root cause = warm-up dropped per-request seed -> plans lacked seed tail; fix #594 @6a7ff652 opened + granted (135M Gumbel B1 460/460; 360M root identical). RC merge request (top priority). Epoch-run: cherry-pick, accept on 2 failing B8 from 2 models, then release the 130.
