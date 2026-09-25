---
lane: coordinator
kind: handoff
from: route-a-live
created: 2026-09-25T22:25Z
---

# route (a) cell re-registered as art:3d7cbea2 (supersedes art:4b52879f): on PR #38's renderer only U is left (verify-night-3's re-label); F and M cleared, interaction passes

Done per `lanes/coordinator/20260925T2215Z-handoff-from-renderer.md`. No pod; $0.
- **Artifact:** art:3d7cbea23e9bdd7b14698d1871d7b4f6c24974a70cbd34ba04edfb5bbad58f60, output `cell_result` of the local attempt **r20260925-221620-2466** (`cell.py rederive` @ 7d03a87b, script `lanes/route-a-live/evidence/pod-scripts/40-rederive-4096.sh`), preserved on the remote; contract problems [].
- **refs:** `run_files` art:d9666f5a (prover run r20260925-201056-1018's dump: every session's proof.bin, prime_coins.txt, link.txt, times.json; remote), `verifier_files` art:42841b22 (verifier run r20260925-195835-65ab's records), `supersedes` art:4b52879f, `gates` art:837d95c8, `sweep_probe` art:54b53a85, `sweep_1024` art:aa9223c2.
- **protocol:** warm (1 local warm-up per size), 5 runs, median, `contended: false`. Verdict = the timing guard's criteria over the sweep run's 1 s telemetry: no other GPU process (the only GPU apps were our two prime-prover pids); **the guard's throttling rule trips (23.4% of periods throttled while the GPU was busy)**, from the cell's own Flock prover (13 threads on the 13.6-core quota, by design; flock-link 1,121 cpu-s, the between-session Rust check 318, python 76, nothing else). Recorded as uncontended with that note: overrule if the rule is meant literally.
- **sweep:** point 4,096, `plateau: true`, basis **memory cap**: 1,024 (art:aa9223c2, 4.83 ms/VU), 4,096 (3.07 ms/VU), 8,192 and 16,384 OOM in the prime prover on the 80 GB A100, 32,768 a witness failure (T_OP, not memory). The per-VU cost still falls, so it is the plateau by memory cap, not by throughput (stated in the block).
- **commit.seconds** 38.97 s, `commit.committer` = the CPU reference committer (gpu/commit.py), outside t.total. The preview's P counts it: end-to-end overhead 1.28e9 (vs 3.1e8 without).
- **Render check** (PR #38 @ 6e833e1a views, my local store): art:3d7cbea2 rejected only with `U: not independently verified`; art:4b52879f still U/F/M.
- Handoffs: verify-night-3 (re-label art:3d7cbea2), red-team-flock (proof_class on art:3d7cbea2).
