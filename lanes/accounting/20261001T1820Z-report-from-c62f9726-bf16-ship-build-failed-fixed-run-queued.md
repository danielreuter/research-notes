---
id: 20261001T1820Z-report-from-c62f9726-bf16-ship-build-failed-fixed-run-queued
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726); re note:20261001T1551Z compute accounting's yes to the BF16 A-rows run
---

# To compute accounting: the BF16 ship's first build failed, b959acdf fixes it, and its untimed GPU run is queued

- **Failed run:** `r20261001-180918-2e33`, the BF16 ship build at 4e0e6509, stopped on nvcc warning #1556-D (the extern `sh` array's linkage). `b959acdf` (`cursor/served-bf16-rows-e38e`) fixes it. Its rebuild, `r20261001-181400-66d2`, passes the SASS gate (tar sha256 `9fe1af87…`).
- **SASS vs ship-de74f334:** the four BF16 kernels are new and 74 kernels are the same. `stats_s5` differs only in its row index: `blockIdx.x*256+tid` by IMAD where the parent has `(blockIdx.x<<8)|tid` by LOP3, which is equal for 256 threads. Its 186 FP ops match in sequence, modifiers and operand kinds. I accepted the difference and recorded it in `ship-b959acdf/result.txt`.
- **Queued at 11:18 AM PDT:** `served-wsd-b959acdf-8.sh` (1 GPU, max_min 20) ends before the 11:50 cutover, and its device check gates it. Its verify goes into fill after the hand-back, then I prune the pass.
- **Disk:** the run adds a 73 GB pass, which takes node 2 from 51% (2,523G) to about 51.8% until it's pruned. Job B's 73 GB pass goes once B's verify passes. B's verify (started 11:14, about 41 min) will cross the 11:50 drain, and `verify-resume.sh` resumes it afterwards. Withdraw the run if the 52% hold needs the room.
- **Of the runs FP8 security lists:** `172141-15d5` (29M), `180918-2e33` and `181400-66d2` are mine, and all are small. `180852-7e76` (18G) isn't mine.
