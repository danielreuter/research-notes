---
lane: vllm-rf-b1c
kind: report
created: 2026-09-25T16:23Z
status: open
---

CHECKPOINT none (17:09Z) [open] #67 head Commit OOM-killed 16:47Z in sampled replay fork (shmem 86 + anon 81 GiB at the 175 GiB limit; admission predicted short 11.7 GiB); base Commit r20260925-170559-fe8e launched on g2 to tell pod shape from regression; gate(b) b4b9 running
CHECKPOINT ec6219f5 (17:03Z) [open] head ec6219f5 (P10 commit.main cap 1913->1912 after the merge); re-gate r20260925-170048-b4b9 running on b5pat-cpu (first try b7a7 killed: that lint); #67 head Commit running
CHECKPOINT 8f94cb48 (16:57Z) [open] re-gate r20260925-165541-b7a7 on vyv-rf-b5pat-cpu (handed over by b5patc): lints + gate(b) head 8f94cb48 then base 38a8d35d; #67 head Commit on g2 running
CHECKPOINT 8f94cb48 (16:51Z) [open] merged origin/main 38a8d35d -> 8f94cb48 (pushed; import/allowlist conflicts only, static import scan clean); re-gate head 8f94cb48 vs base 38a8d35d next on b5pat-cpu; #67 head Commit running
CHECKPOINT 0e954bf0 (16:47Z) [open] #67 head Commit on g2 still running (since 16:03Z); waiting on b5patc cpu handoff for re-gate
CHECKPOINT 0e954bf0 (16:33Z) [open] branch lane/vllm-rf-b1c @0e954bf0 (rebased on main 239c0e28, pushed); #70 done 32/32 = record (R2 preserved), tp2 terminated; #67 head Commit running on g2; STATE.md up
CHECKPOINT 80b19e59 (16:24Z) [open] b1c up (bc-e079e6ee), succeeds b1b @8c0bec08; adopting pods vyv-rf-b1-g2 (#67) and vyv-rf-b1-tp2 (#70); rebase next
