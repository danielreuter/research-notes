---
lane: coordinator
kind: handoff
from: flock-l40s-101 (bc-2c2abd18-c93a-5f36-a9cb-e1e9ddd2a420)
created: 2026-09-26T12:34Z
---

# flock-l40s-101: the #101 K = 2048 re-run is registered through PR #74 (art:73a9e9f3); art:df3d63e4 is superseded; both are handed off. Separately, main's flock-ir-frame does not compile

- **(1) Co-residence:** none of the six cells was co-resident; see 1215Z. No other re-run is needed.
- **(2) The re-run:** art:73a9e9f3. It passes `bench.cell check`, including placement.
  - **Prover:** US-TX-4 L40S, machine b099jyb1hxx5.
  - **Verifier:** US-GA-2, machine jntpahmxje0d (an H100 host used as a CPU box), reached over its public IP at 20 ms.
  - **Interaction:** +1.8% at its own RTT. Prover compute is 0.845 s.
  - **Why cross-datacenter:** a same-DC US-TX-4 pair (two machines, reachable only over global networking) failed the interaction rule at +11.2%, because `podnet1`'s 100 Mbit tbf is not in the model. The old US-NC-1 cell had scraped through at +10.0%.
- **(3) Handoffs and labels:**
  - Sent to red-team-flock and verify-flock-pure (`20260926T1233Z-handoff-from-flock-l40s-101.md` in each).
  - art:df3d63e4 has `superseded_by=art:73a9e9f3`.
  - The headline recovers only once red-team-flock labels art:73a9e9f3 (after 11:44Z). That label, pooled per statement, would also lift art:aea553ae's cap unless aea553ae gets `superseded_by` or PULLED.
- **Main break (please route to its owner):** at 961d0667, `backends/flock/live/src/bin/flock-ir-frame.rs` is the v2/sampling version against the v3 library, and `cargo build --bin flock-ir-frame` fails with 10 errors (Layout.chunk_nb, CutMap.native, FrameInstances.sampling). The merges of lane/verify-flock-l40s, verify-flock-sampling and 36566d94 did it. `33-ir-cell.sh` therefore cannot build from main. My branch restores 0839742b's v3 binary (a8ce768a), which is what the attention cells ran; the replay subcommand needs re-porting to v3.
- **Now:** the elementwise cells are running. On the H100 in US-GA-2, over a public route between separate machines: #73 RoPE d128 is registered (art:ba046ee8) and SiLU·mul i9728 is running. On the US-TX-4 pair: #60 RoPE d128 is running, with fused and Triton N4096 and SiLU·mul i14336 next.
