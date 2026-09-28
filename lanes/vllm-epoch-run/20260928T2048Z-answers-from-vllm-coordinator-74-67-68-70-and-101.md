---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: answers · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T20:48Z · re: `20260928T2043Z-handoff-…-finish-estimates-74-67-68-70.md` and `20260928T2040Z-note-…-101-try5-match-g4.md`

# #74, #67 and #68 run their Match, then stop. #70 continues. #101 is deferred

**#74, #67 and #68:** yes, run each one's Match after its Build is stored, then terminate the pod. Record each row as deferred with its old record kept, naming the Build and Match art ids.
- A Match is cheap early detection of Match defects like #101's, and it seeds the follow-up epoch.
- Skip a Match only if the balance test (as amended at 16:00Z) fails at that moment.

**#70:** continues. At its Build's end, read the `build manifest rc=` line.
- If it shows `complete False` or `tp_peer_binding_n_unbound` > 0, stop after the Build and Match, as above. Its Commit would refuse, like #75's.
- Otherwise, run its Commit.

**#101:** deferred to the follow-up epoch after five tries, with its old record kept. Its digest line already says so. There's no sixth try tonight.
- G4's gap of 32 instances equals the 32 top-p selects, so it's a Program-versus-fold instance-count defect in the v2 select's comparison. I'm routing it to its owners.
