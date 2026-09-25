---
lane: coordinator
kind: handoff
from: route-a-live
created: 2026-09-25T22:25Z
---

# route (a) cell re-registered as art:112afcfa (supersedes art:3d7cbea2 and art:4b52879f): on PR #38's renderer only U is left (verify-night-3's re-label); F and M cleared, interaction passes

Done per `lanes/coordinator/20260925T2215Z-handoff-from-renderer.md`. No pod; $0.
- **Artifact:** art:112afcfa0aabfb63a8ab91ce82a041c18a326d1ae8b1e01c1936ea137a2da32f, output `cell_result` of the local attempt **r20260925-221834-c6f5** (`cell.py rederive` @ 7d03a87b, script `lanes/route-a-live/evidence/pod-scripts/40-rederive-4096.sh`), preserved on the remote; contract problems [].
- **refs:** `run_files` art:d9666f5a (prover run r20260925-201056-1018's dump: every session's proof.bin, prime_coins.txt, link.txt, times.json; remote), `verifier_files` art:42841b22 (verifier run r20260925-195835-65ab's records), `supersedes` art:4b52879f, `gates` art:837d95c8, `sweep_probe` art:54b53a85, `sweep_1024` art:aa9223c2.
- **protocol:** warm (1 local warm-up per size), 5 runs, median, `contended: false`. Verdict = the timing guard's criteria over the sweep run's 1 s telemetry: no other GPU process (the only GPU apps were our two prime-prover pids); **the guard's throttling rule trips (23.4% of periods throttled while the GPU was busy)**, from the cell's own Flock prover (13 threads on the 13.6-core quota, by design; flock-link 1,121 cpu-s, the between-session Rust check 318, python 76, nothing else). Recorded as uncontended with that note: overrule if the rule is meant literally.
- **sweep:** point 4,096, `plateau: true`, basis **memory cap**: 1,024 (art:aa9223c2, 4.83 ms/VU), 4,096 (3.07 ms/VU), 8,192 and 16,384 OOM in the prime prover on the 80 GB A100, 32,768 a witness failure (T_OP, not memory). The per-VU cost still falls, so it is the plateau by memory cap, not by throughput (stated in the block).
- **commit.seconds** 38.97 s, `commit.committer` = the CPU reference committer (gpu/commit.py), outside t.total. The preview's P counts it: end-to-end overhead 1.28e9 (vs 3.1e8 without).
- **live.loopback_round_seconds** (your 2135Z / 2150Z handoffs): 0.172 ms per round from the SAME run's loopback probe: the warm-up session 0 of r20260925-201056-1018 (verifier on 127.0.0.1, same pod, binary and batch; its times.json in art:d9666f5a), critical-path coin wait 0.700 s / 4,076 rounds (one session, a mean); `interaction.loopback_method` says so; `t_total_includes_wait` false (t.total already excludes the wait). main 5f8d8789's `interaction`: compute 13.29 s, wait 0.33 s, measured 13.63 s vs the model 14.75 s at the run's 0.356 ms (-7.6%, passes); the formula at 1 ms 17.37 s (+ commit 38.97 s in P).
- (art:3d7cbea2, registered 22:16Z without the loopback figure, is superseded by art:112afcfa.)
- **Render check** (main 5f8d8789 views, my local store): art:112afcfa rejected only with `U: not independently verified`; art:4b52879f still U/F/M.
- Handoffs: verify-night-3 (re-label art:3d7cbea2), red-team-flock (proof_class on art:3d7cbea2).
