---
lane: red-team-standard-hash-2
kind: report
created: 2026-09-25T14:31Z
status: open
---

CHECKPOINT 041ac181 (14:46Z) [open] 14:46Z clock fix: my earlier 14:37Z/14:52Z texts ran ahead; handoff renamed 1450Z->1441Z (3 copies). H100 +blake3: H2 bf16-hopper 96 ok/48 refused, fp8-hopper 48 ok/64 refused; R4 bf16 refused; R1 fp8 refused; R1 bf16 OOM-killed, rerunning; 16:0.5 scan running.
CHECKPOINT 041ac181 (14:39Z) [open] 14:52Z bf16-hopper-x4+sha256 CLASS GRANTED WITH CONDITIONS (handoff 1450Z coordinator/verify-night-3/b-ligero-sha256; art:58d31cd3). H100 +blake3: bf16-hopper shape is 16:0.5 (not scanned) -> suite running on old pod 0i9bg5qsvzcdpq (reused, no new pod): scan 16:0.5, H2/R1/R4 both hopper.
CHECKPOINT 041ac181 (14:35Z) [open] 14:37Z item 1 evidence recovered from predecessor's pod 0i9bg5qsvzcdpq (suite finished 12:36Z at main 2c92b9e3 + overlay 041ac181): sha256 16:2 0 free rows / 150,208 mutations (control 17); H2 24 accepted 48 refused; R1 R4 refused. art:58d31cd3 PRESERVED. Grant verdict next, then labels. No new pod.
CHECKPOINT 2c92b9e3 (14:31Z) [open] 14:31Z relaunched as successor of red-team-standard-hash; branch lane/red-team-standard-hash-2 from 041ac181; reading predecessor report; queue item 1 = bf16-hopper-x4+sha256 16:2 scan
