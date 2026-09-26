---
lane: coordinator
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T22:00Z
---

# Total unit granted and gated on an L40S; the 9 cells are blocked by bench.cell's placement check (shared NAT IP). Hour limit reached, so here are the options

**Done:**
- **Total unit** (`bf16-ampere-total`, pin fef256df, statement `verity/flock-pure-block-total`, domain `total`):
  red-team-flock-3 GRANTED WITH CONDITIONS at 20:35Z.
  - TG4 fixed: `supports()` refuses sm80 BF16 K1536 with SHA-256 rows (UL1).
  - TG5 fixed: ChunkTail is granted in `granted()`.
  - Branch at d2292e3b, on GitHub.
  - TG3 (a `/v1` name) not taken: Daniel's instruction is no version suffix in names.
- **TG1 met.** `51-total-gate.sh` ran on the L40S prover pod itself (EU-NL-1, machine fpuyltj3q41d) as run
  **r20260926-213915-70e3**: GATE OK. That covers CPU and `--gpu` selftests at K 1536 and 2048 with 8 and 64 VUs, plus the
  NaN/inf negatives with the GPU prover. An earlier gate on a 4090 was r20260926-202308-c367.

**What blocked the cells:**
- The poller searched from 20:45Z and at 21:36Z got an L40S prover plus an H100 SXM verifier in EU-NL-1:
  - different machine ids (fpuyltj3q41d / go1zlmhqhfmq) and different GPU models;
  - reached over RunPod global networking (`w3joukypegsto7.runpod.internal`, a routed 10.x path).
- `bench.cell plan` refused all 9 cells: "prover and verifier share public_ip 91.199.227.82 (one machine)".
  - That is the DC's egress NAT address, shared by both pods.
  - `placement.separation` treats any shared public IP as one machine, even when the machine ids differ.
- Both pods were terminated at once. Spend today is about $2.

**Options:**
- **(a) bench-spine relaxes `placement.separation`:** a shared public IP is not "one machine" when both machine ids (or DMI
  uuids) are known and differ, and the link is not host-private. That is the same exception it already makes for
  host-private peers. The EU-NL-1 pairing is then valid, and I'd re-run there (L40S + a cheap verifier), about $6 for the
  9 cells.
- **(b) A cross-datacenter verifier** with public IPs that differ, recording the measured RTT (red-team-flock's ruling
  allows it). L40S stock this evening was only EU-NL-1, so the verifier would be in e.g. EU-RO-1 or EU-SE-1, at about
  10–30 ms per round. The cells run, but slower.
- **(c) Wait** for an L40S in a DC whose pods get distinct public IPs (US-MO-1 did earlier today), on a longer poll.

**My recommendation: (a).** The identities that matter (machine id, GPU model) prove separation. The public IP here is the
NAT's, not the host's.

The queue is ready: `evidence/gemm-workloads/launch.sh l40s` with `GATE=1` and the 9 tags, and `/tmp/fp/total-auto.sh` on
my VM.
