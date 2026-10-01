---
id: 20261001T1214Z-reply-from-c62f9726-served-window-1-timed-result
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726)
---

To compute accounting, cc bc-c066b30c. **Served window 1 (b737755b, timed 4:30:15–4:34:44 AM PDT): decode 3.097×, prefill 1.630× over graphed stock FP8.** Window 8 was 3.194×. Every gate and validation passed, and both verify passes repeat their timed commitments (r20261001-104607-343a, PRESERVED).
- Run 2's 3.000× came from a slower baseline. Pearl-C's decode step is faster here (22.98 against 23.48 ms), but graphed FP8 is 7.42 against 7.83 ms. The timed 3.097× is the number to use.
- Verify: prefill ACCEPT (13 tiles), control REJECT (128), control-leaves REJECT (5): art:e35958df1d7b83b50ed0bee9ed9ba9c752569a705a727fe468c28aecaa7d6403. Decode is verifying in fill (`served-verify-r20261001-104607-343a.sh`, 32 processes, since 12:08Z). I expect about 6:30 AM PDT, before the 7:50 checkpoint. The three verified passes' data is pruned (disk 46%).
- 2.9× isn't reachable tonight. With hashing off, Pearl-C's step is already 16.5 ms against graphed FP8's 7.4 ms, and that gap is mostly the call's forming, GEMM and clean-up in #610's pinned kernels. Hashing adds 6.5 ms, about 5.9 of it in ship kernels. Run 5's Python-side cut (256 fewer kernels) should save about 0.2 ms.
- Plan: run 5 (bdedc145) starts at 12:20Z on my GPU, and its passes then verify in fill. Next on that GPU comes the 70B per-shape diagnostic: run.py, -h2, at 70B's four GEMMs and 8B's, m = 32 and 8192, plus vLLM's CUTLASS FP8 call as the m = 32 baseline, since run.py has none below m = 128.
- Window 2 (14:00Z) repeats b737755b as a second timed sample, the verified build. Window 3 (15:30Z) carries bdedc145 if run 5's gates pass and its verify lands by 15:10Z. READY lines at 13:40Z and 15:10Z.
