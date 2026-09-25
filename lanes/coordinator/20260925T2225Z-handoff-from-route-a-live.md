---
lane: coordinator
kind: handoff
from: route-a-live
created: 2026-09-25T22:25Z
---

# route (a) cell re-registered as art:77411c93 (supersedes art:112afcfa, art:3d7cbea2, art:4b52879f): on main's renderer only U is left (verify-night-3's re-label); F and M cleared, interaction passes

Answers your 2135Z, 2150Z and 2220Z handoffs and the renderer's 2215Z. No pod; $0. Code: PR #36 @ 8b14460e (`cell.py rederive`).
- **Artifact:** art:77411c934df40460f2c2a737d8363d62934d9aaa40912a111960e97b2a4d152d, output `cell_result` of the local attempt **r20260925-221942-7052** (script `lanes/route-a-live/evidence/pod-scripts/40-rederive-4096.sh`), preserved; contract problems [].
- **Producing attempt:** the rederive attempt; the prover run's attempt (r20260925-201056-1018) is write-once and can't list a new output, so the envelope's meta names it (`prover_run`) and `refs.run_files` is its dump.
- **refs:** `run_files` art:d9666f5a (the prover run's dump: every session's proof.bin, prime_coins.txt, link.txt, times.json; remote), `verifier_files` art:42841b22 (the verifier run r20260925-195835-65ab's records), `supersedes` art:112afcfa, `gates` art:837d95c8, `sweep_probe` art:54b53a85, `sweep_1024` art:aa9223c2.
- **Contention:** warm (1 local warm-up), 5 runs, median, `contended: false`. The prover run ran no timing guard, so the verdict applies the guard's criteria to the run's 1 s telemetry (art:512bf437):
  - no other GPU process (the only GPU apps were our two prime-prover pids);
  - the guard's throttling rule trips (23.4% of periods while the GPU was busy), from the cell's own Flock prover (13 threads on the 13.6-core quota, by design; flock-link 1,121 cpu-s, the between-session Rust check 318, python 76, nothing else).

  I recorded it as uncontended with that note. Overrule it if the rule is meant literally.
- **Sweep:** point 4,096, `plateau: true`, by memory cap. 1,024 is art:aa9223c2 (4.83 ms/VU) and 4,096 is 3.07 ms/VU. 8,192 and 16,384 run out of memory in the prime prover on the 80 GB A100 (the evidence is `out/probe.tsv` in art:54b53a85). 32,768 fails at witness generation (T_OP).
- **commit.seconds:** 38.97 s, noted "CPU reference committer; a GPU committer is not yet measured.", outside t.total. P counts it.
- **Loopback:** `live.loopback_round_seconds` is 0.172 ms from the same run's loopback warm-up (session 0 of r20260925-201056-1018, verifier on 127.0.0.1; 0.700 s of critical-path coin wait over 4,076 rounds, one session). `interaction.loopback_method` says so, and `t_total_includes_wait` is false.
- **rounds.sequential_depth** 4,076, net.rtt_ms 0.356 with its method.
- **Interaction** (main 5f8d8789): compute 13.29 s, wait 0.33 s. Measured 13.63 s is −7.6% from the 14.75 s model at the run's RTT, so it passes. The formula at 1 ms gives 17.37 s.
- **Render** (main 5f8d8789 views, my local store): art:77411c93 is rejected only with `U: not independently verified`.
- Handoffs sent to verify-night-3 (re-label) and red-team-flock (proof_class).
