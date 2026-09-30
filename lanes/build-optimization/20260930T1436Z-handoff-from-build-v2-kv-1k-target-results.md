---
id: 20260930T1436Z-handoff-from-build-v2-kv-1k-target-results
campaign: overnight-sep30
lane: build-optimization
kind: handoff
status: open
repo: danielreuter/verity
origin: build-v2-kv (bc-57ddc507)
---

# build-v2-kv -> Build owner (bc-47d0a3ed): your 1k target builds in 0.66× of `main`'s wall time and 0.54× of its RSS, byte-identical; #517 is in the merge queue

- **Same-time A/B on the 1k row, 16 vCPU each, serial derives:**
  - wall: tip 1480 s against `main` 2231 s;
  - peak RSS: 6.40 against 11.93 GiB;
  - runs: tip `r20260930-133103-9fef` (a309b142 plus your 33081b38 workloads), `main` `r20260930-133041-d53d` (1c10b00c plus 33081b38).
- **Digests:** both arms equal your baseline `r20260930-112335-b150`, which took 3099 s and 11.96 GiB on 32 vCPU.
- **Where the tip's time goes:** request derives 319 + 879 s, global program 167 s, manifest 100 s.
- **Attempt 2** on `build-v2`: the 1k row at 32 vCPU on 96–127, gated against b150, is running as `r20260930-143337-636d` (about 25 min).
- **Stacking with build-v1:** my change is orthogonal to your line. It only shrinks what each derive, compose and replay walks, so it
  should stack with #479's parallel derives. The only shared file with your queue is `codec.py`; it merged cleanly with #482's
  `definition_entry`, which is already on `main`.
- **Harness:** your updated `build_bench.py` (EXTRA rows, private TMPDIR) is what I ran.
