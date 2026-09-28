---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff (decision needed) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T18:57Z

# #23's Commit was refused by host admission (F-dA-15): 483 GiB predicted, the pod allows 343 GiB. Retry with the override, or defer?

- **Where #23 got to:** Build PASS 17:36Z; Match PASS 18:22Z (46 min, GM-01 PASS, concurrency 64, tokens equal); fast word check PASS
  (64 of 64 lines, manifest `004a5bdab…`). The Commit rebuilt the manifest (#298's bug, 27 min), then **refused at 18:51Z** with `rc=3` and
  verdict NOT_RUN:
  `F-dA-15 ADMISSION (native_collect_v2b): scheduled raw 146835 MiB over 129 steps (peak step 0 = 125475 MiB) -> predicted host 494484 MiB vs limit 359535 MiB: REFUSED`.
- **The pod:** `vyv-rf-epoch-23`, 2× RTX 6000 Ada, 376 GB host (a 351 GiB cgroup). Last epoch #23's Commit OOMed at 251 GB, while
  the bound then predicted 183 GB, so the bound has run low before on this row, not high.
- **The main run** is finishing its store: records and Match go out with its own key, which is valid to 19:59Z. The Build is already
  side-stored (`art:7a30ced1…`). I'm keeping the pod up until you decide.

**Options:**
1. **Retry the Commit alone on this pod** with `VERITY_ADMIT_OVER_BOUND=1`, as a side run over the existing Build and Match. It takes about
   90 min: 27 min of manifest rebuild, about 60 min for 1 pair, then verify. That's about $2.5, ending about 20:45Z. The risk is an OOM at
   the 351 GiB cgroup, which gives NOT_RUN, never a FAIL record.
2. **Defer #23** to the follow-up epoch on a host with at least 512 GB, keeping its old record. It costs nothing more: the pod is
   terminated once its custody completes.

**My recommendation is option 2.** Last epoch's OOM at 251 GB, and a prediction above this pod's limit, both make an OOM likely.
**Default if I hear nothing by 19:20Z:** option 2.
