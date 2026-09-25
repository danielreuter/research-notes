---
lane: coordinator
kind: handoff
from: b-ligero-sha256
---

# +sha256 cell ids sent to verify-night-2 (1150Z, 1202Z); please cherry-pick b009fdc8 (bf16-hopper-x4+sha256 PINS row)

1. **Cells, all run at or after da74b03e:**
   - fp8-hopper-x4+sha256: 32768 VUs, 6162 VU/s. e592, art:4aa258ee (proofs art:61842848), at da74b03e.
   - bf16-hopper-x4+sha256: 8192 VUs, 3062 VU/s. 5a5f, art:fcd6a623 (proofs art:c25cac59), at b009fdc8, with
     `software.allocator` recorded.
   - Both PRESERVED on R2.
   - Details and the list of what doesn't count are in the two verify-night-2 handoffs.
2. **Merge-ready: b009fdc8.** It adds one `backends/ligero-verify/src/leaf.rs` PINS row for bf16-hopper-x4+sha256 (sys a02f283d…,
   table 1b879d1a…) and nothing else. Gate: r20260925-104053-b438, 13 honest + 86 negatives, 0 failures.
   - Without it, main's pinned ligero-verify refuses the bf16 dump ("system not pinned").
   - It applies cleanly on 767115db (its parent is 98d878ca).
3. **Custody finding (every lane on `--custody-r2`):**
   - Both of my big runs' runner pushes failed with `RemoteDisconnected`, even though the objects had reached R2.
   - The runner's store is `/workspace/research/store`. From the pod, `data push RUN --store /workspace/research/store
     --verify head` with a freshly minted key finishes it in about 1 min.
   - Don't use `custody --publish` into the default `~/.research/store`: it re-ingests the whole run and stalled on R2 GETs
     that stopped partway (about 24 MB, 0 B/s).
   - Script: `lanes/b-ligero-sha256/evidence/pod-scripts/62-repush.sh`, run as its own `--custody-r2` run so it has a key.
4. **Next:** fp8-ada-x4+sha256 gate + sweep at b009fdc8 (887e, running).
   - Spend so far is about $12.5 (H100 since 08:41Z, 4090 $0.75).
   - I'll drain before 15:30Z.
