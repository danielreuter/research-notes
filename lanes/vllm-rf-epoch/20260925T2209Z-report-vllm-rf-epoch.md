---
lane: vllm-rf-epoch
kind: report
created: 2026-09-25T22:09Z
status: open
---

CHECKPOINT 80b19e59 (02:19Z) [open] WAIT moe67 30ef, tp70 4b0e, tp70b 0ccc (small-file copies of recording runs whose custody upload failed) check-back 02:55Z agent bc-e66a058f-2557-506e-93e3-3889bb86af5f: rebaseline write DONE 14b321ad (#101,#67 digest checks) + golden 101e8917; moe68 terminated; exit-143 rebase runs were mine (superseded by 015749-*, all PRESERVED)
CHECKPOINT 80b19e59 (00:50Z) [open] WAIT moe67 (#4 Commit, #23 next; rebase 9d5e), moe68 55a8 (#60 Commit override; rebase ec89), tp70 (#67 Commit; rebase d097), tp70b (#70 Commit; rebase 20d1) check-back 01:40Z agent bc-e66a058f-2557-506e-93e3-3889bb86af5f: status handoff sent 0055Z; big terminated (#68 dropped: time)
CHECKPOINT 80b19e59 (23:47Z) [open] WAIT tp70b 4602 (#70 Commit), moe68 9e59 (#57 Commit then #60), tp70 42c8 (#67 after B/M), big 8ece (#68 after B/M), moe67 c7c4 (#4/#23 after #23 B/M) check-back 00:30Z agent bc-e66a058f-2557-506e-93e3-3889bb86af5f: tp75+h100 terminated (#75 build timeout, #73 commit OOM 251GB); status handoff 01:30Z
CHECKPOINT 80b19e59 (23:45Z) [open] WAIT tp70b 4602 (#70 Commit), moe68 9e59 (#57 Commit then #60), tp70 42c8 (#67 after B/M), big 8ece (#68 after B/M), moe67 c7c4 (#4/#23 after #23 B/M) check-back 00:30Z agent bc-e66a058f-2557-506e-93e3-3889bb86af5f: tp75+h100 terminated (#75 build timeout, #73 commit OOM 251GB); status handoff 01:30Z
CHECKPOINT 80b19e59 (23:43Z) [open] WAIT tp70b 4602 (#70 Commit), moe68 9e59 (#57 Commit then #60), tp70 42c8 (#67 after B/M), big 8ece (#68 after B/M), moe67 c7c4 (#4/#23 after #23 B/M) check-back 00:30Z agent bc-e66a058f-2557-506e-93e3-3889bb86af5f: tp75+h100 terminated (#75 build timeout, #73 commit OOM 251GB); status handoff 01:30Z
CHECKPOINT 80b19e59 (22:15Z) [open] WAIT commit re-runs r20260925-221340-* (tree ad8050e9 = m32 271a0952 cherry-pick, pre-gate) queued behind each pod's Build/Match; #74 dropped (time) check-back 23:15Z agent bc-e66a058f-2557-506e-93e3-3889bb86af5f: first Commits (#4 after #23 B/M on moe67; #57 after #60 on moe68)
CHECKPOINT 80b19e59 (22:09Z) [open] WAIT all 7 pods, Builds/Matches continuing; every Commit held (holdcommit r20260925-220648-*) until m32's sha: #4 and #57 Commits hit M>2^32; check-back 23:00Z agent bc-e66a058f-2557-506e-93e3-3889bb86af5f: then cherry-pick m32 + Commit-only re-runs
