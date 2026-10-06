---
id: network-accounting/network-accounting/20261006T0230Z-draft-warden-proof-service
campaign: network-accounting
lane: network-accounting
kind: draft
status: open
repo: verity@c305471c5 (main, 6 Oct 02:00Z), with #1268 (the warden program split) where named
origin: network-accounting (bc-ecea50f6), for Daniel's proof-service ask via top (5 Oct, 7:17 PM PDT, thread 1791253199.410869); beside note:network-accounting/network-accounting/20261005T2320Z-draft-consolidation
---

# The network warden and the proof service

Deliverable 1 of top's 7:17 PM PDT ask, for the warden, plus the question put to network-accounting: is the warden a
user of the service, part of its deployment, or both. Paths are relative to the verity checkout; `warden/` is
`verity/protocols/accounting/communication/warden/`.

## The answer: both

- **Part of the deployment.** RecursiveZK leaves two premises to the deployment: the GPUs reach nothing but the prover
  gateway, and aborts and timing are outside the theorem. Both are the warden's.
  - The developer's site (GPUs and prover gateway) is a spatial unit.
  - The gateway's link to the verifier gateway is an egress boundary link, and the live coins arrive on an ingress link.
  - The warden enforces that these are the only links (a frame on any other link is a fault), and bounds what leaves
    through their timing.
  - This needs no service method. It is where the service runs.
- **A user.** The warden's own audit asks whether each link-window's record equals the Program's grid. That is a check
  over committed values like PoUW's or PoUS's: the service can commit, record and verify it, and the warden consumes
  the verdicts.

The two roles meet in one place: the service's own traffic is warden-shaped (R1 and R4 below).

## (a) Infrastructure the warden owns that the service would replace

| what | where | replaced by |
|---|---|---|
| Commitments and hashing: the row and record digests, unsalted `tagged_sha256` over the real frames (padding elided) | `warden/commitment.py`, on `verity.primitives.commitments.identity` | the service's commit. The row encoding (count, then the n real frames) stays the committed value's format. Today's digest binds but doesn't hide, so a guessable egress frame is recoverable from it |
| The audit record: one record per link-window by the verdict deadline (`no-verdict`), never two (`duplicate`), record-and-reject with no halt | `warden/audit.py` (`Audit`, `Verdict`, `_settle`) | the service's record. The verdicts' names and the first-violation order stay the warden's |
| Custody: publishing each window's record raw and committed as it closes, from a worker thread | `warden/active.py` (`Proxy.publish`); offline, `benchmarks/network_traces/active_replay.py` (writes and audits records), `record.py`, `run.sh`, `active_live.sh` | the service's commit and record, called from `Proxy.publish` |
| The verifier: the Python audit, and Lean's definitions with the code package that runs them | `warden/audit.py` (`check_link`, `check_ingress_link`); `verity/Security/Definitions/Warden/`, `Specs/Warden/` (`NetTiming`); `warden/lean/` (`warden_program`, its difftest; #1268) | the service's verify, running the warden's check as a public Definition. The Python audit stays as the oracle the difftest compares against |
| Randomness and draws | none: the audit is exhaustive. `warden/lean/scripts/difftest_vectors.py` seeds test vectors only | nothing to replace |
| Transport and gateway | `warden/active.py` (`Proxy`, `Shaper`, `Bucketer`) | not replaced: this is the deployment role |

These stay the warden's, because they are the protocol itself rather than infrastructure:
- the grid and its fail-closed rule (`grid.py`);
- the Program's schedule (`schedule.py`);
- the online prover (`online.py`);
- calibration (`calibration.py`) and capacity (`capacity.py`).

## (b) The warden as a service user

- **What is committed.** One record per link-window: the link, the window, (T, r, B, τ_b), the status and the T row
  digests. Each egress window adds one declared clock sync for the spatial unit.
- **Which units.** Every link-window of every boundary link, ingress and egress: the policy is *all*, with no draw.
  - An unaudited window is not bounded at all: it can carry up to 8·T·r·B bits (`capacity.unbound_bits`).
  - So a sampled audit gives the K charge nothing to use.
  - The service's selection must offer *all* as a policy.
- **The check, as public Definitions.**
  - Egress: `NetTiming`'s `Accepted (constantRate T W ss frames)` on each prefix of whole windows. That is `check_link`:
    status complete; rows equal to `expectedRow` of the Program's frames; the declared sync in Σ_sync; one sync per
    unit per window.
  - Ingress: `StatusComplete` (`check_ingress_link`).
  - The code form is `warden_program`. #1268's guarantees `CodeAcceptedConstantRate` and `CodeStatusComplete` say it
    decides exactly these.
- **What it does with the outcome.** The verdict per link-window, recorded, with the run rejected on any violation. On
  an accepted run, the charge:
  - egress: log2 #Σ_sync bits per window (7 at 16 × 8);
  - ingress: the K charge's share by span.
- **Proof form.** The check reads the egress frames' content, since `expectedRow` packs them in canonical order.
  - If the auditor may see egress content (it already left the boundary), the check runs in the clear, and the warden
    uses only the service's commit, record and verify.
  - If not, the statement "the committed rows are `expectedRow` of the committed frames" is small (counts plus
    hashes), so it needs direct ZK, not recursion.
  - The expected counts would still reveal each session's output length and anchor bucket to the auditor.
  - Recommendation: in the clear first. Move to ZK when served-zk's commitment opens the served frames, so that the
    frames' commitment is the same one.

## Requirements the service doesn't meet yet

- **R1. The record's arrival times are a channel.** The verifier gateway "keeps the record of what arrived when". Every
  message from inside the boundary that reaches it is egress, so its arrival time leaks unless it is fixed in advance.
  - The warden's status is untimed (W5): one symbol per link-window, and the audit reads only whether the record was in
    by the deadline.
  - The service must keep the same rule for its own messages. The record may hold "by the deadline or not", but no
    arrival time inside the window. Otherwise the gateway's link must itself run on a warden grid, with message sizes
    and order fixed by the public statement (true of C-Flock: its message sizes follow from the circuit).
- **R2. Exhaustive selection, with a charge for any gap.** The policy *all*, and an integrity-profile entry that charges
  a rejected or missing unit its unbound capacity. Today `IntegrityProfile` holds exhaustive facts, a law and δ, but no
  quantity charged.
  - Recommendation: the warden computes the charge from the verdicts, as `calibration` does now, and the profile
    records only which units were exhaustive.
- **R3. Commit runs off the tick, in real time.** Every link commits one record per window, from rows produced 10 times
  a second.
  - The tick's slack is 25 ms, so commit can't run on the tick (today it runs on a worker thread).
  - At r = 1,024 and B = 4 KiB, a full row is 4 MiB to hash per bucket per link, or several ms of SHA-512 on one core
    (unmeasured). The service's commit must take a stream of rows, not one value.
- **R4. The live coins are ingress.** They cross into the developer's site, so under the inference-only policy their
  timing sits on the ingress grid, and their content counts as reads in the K charge.
  - Recommendation: charge their timing, and exempt their content, which the auditor chose independently of the
    secret.
  - **This changes what the K charge counts, so it needs Daniel.**
- **R5. Aborts and timing composed with RecursiveZK.** The warden bounds the timing of the gateway's egress (R1).
  Aborts are one outcome symbol per session, so roughly log2(#outcomes) bits per session, which no current statement
  charges.
  - Recommendation: one corollary for the auditor's whole view: RecursiveZK's simulator, plus at most the warden's
    charged bits (`EncardDecodableLeConstantRate`) plus the abort symbols. proofs and network-accounting own it
    jointly; not tonight.

## What the warden deletes when it migrates

- `commitment.py`'s digest, keeping the row format as the committed value's encoding.
- `audit.py`'s record-keeping (the deadline, duplicates, settling), keeping the check and the verdict names.
- `Proxy.publish`'s sink becomes the service's commit and record.
- The offline audit in `active_replay.py` calls the service's verify.

## Migration order (recommendation)

The warden goes after served-zk's first call and after PoUS. Its migration is the cheapest of the three: records go to
the service's record and the check runs in the clear (no ZK). It is worth doing only once R1 is settled, because the
record is where the warden's untimed-status rule has to hold for the service as well.
