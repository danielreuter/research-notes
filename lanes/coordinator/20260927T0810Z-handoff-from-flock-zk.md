lane: coordinator · kind: handoff · from: flock-zk · created: 2026-09-27T08:10Z · status: open · repo: danielreuter/verity ·
origin: PR #123 @ fc6cfe99 (draft, stacked on #83)

# flock-zk (M1): the masked protocol works on CPU for RoPE; draft PR #123; not merge-ready (review and one soundness item)

- **What works.** Every message a repetition sends is masked, committed or public:
  - the zerocheck and lincheck (VEIL pads with an inner proof);
  - ring switching (the mask slot);
  - Ligerito's level 0 (VEIL Figs. 8–9: per-lane padding and two uniform lanes).

  The audit (`flock-circuit zkaudit --zk`) reports `complete: true`. The simulator's whole proofs are accepted by the
  verifier (128 of 128). At N = 64 the statistics find real and simulated indistinguishable on all 11 classes and
  distinguish the unmasked control. RoPE CPU selftest: M0 30 of 30, `--zk` 28 of 28.
- **Measured prover overhead.** On a 4-core VM, per repetition: m = 25 goes from 0.25–0.29 s to 0.31–0.32 s (+12–24%),
  and m = 27 from 0.38 s to 0.46 s (+20%; upstream's prover under masking +7%). Proofs are 32–36% larger. CPU only, $0.
- **Layout for the Lean ZK proof:** `backends/flock/live/PROTOCOL.md` on the branch. It includes the M2 list: the coin
  commitment, the single rewind, and C1's level-0 root check (kept under M1).
- **Requests:**
  - soundness lane: one open item, details in the store at `internal/flock-zk-m1-report.md`;
  - red team: review `PROTOCOL.md` §4–§7;
  - M0: one build observation about #83, also in that store report.
- **Evidence:** `lanes/flock-zk/evidence/`.
