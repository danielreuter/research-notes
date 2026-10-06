---
id: review-zk-gateway/20261006T1227Z-finding-review-zk-gateway-r9
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1323@5f2fb232265d9354e276ed9554414fa8aaa1e08b, pr:1339@d5aa5ffd29484401b8f0426b82efd4fda3144f1b]
---

# Red-team round 9: #1323 at `5f2fb2322` GRANT, #1339 at `d5aa5ffd2` NO-GRANT

r6 refused #1323 at `12d84d3e8` for B1 to B4 (`note:review-zk-gateway/20261006T0934Z-finding-review-zk-gateway-r6`).
The detail and the probes are in the store's `private/red-team-reviews/1323/` and `1339/` (`review-r9.md`, `r9-*`).

## #1323, `cursor/firewall-contract-95d4` at `5f2fb232265d9354e276ed9554414fa8aaa1e08b`: GRANT

- B1 is fixed: the schedule owes the commitments (`State.owed`). r6's dropped, extra and moved commitments are refused at
  their items.
- B2 is fixed: `tapeError` refuses a tape that repeats a salt or pad value. r6's three tape leaks are refused at 0.
- B3 is fixed: the public input is the verifier's file and `fixes` reads only it. r6's four probes, and a schedule taken
  from the transcript, are refused.
- B4 is fixed: the theorem descriptions say what the statements say.
- Runs:
  - Lean audit `r20261006-120904-9619` (vy-nebius-1, own clone): PASS, 6,164 declarations, the three standard axioms, 14
    guarantees, a clean tree.
  - A local `lake build flock-firewall` is clean, and the four firewall and rec-live test files give 72 passed.
- Non-blocking:
  - `finish` doesn't need the schedule's end, so a truncated session ending in `finish` is accepted. It leaks only a
    prefix; the code or the body should say which is meant.
  - A fixed item's `pads` dependencies are the transcript's word.
  - With no schedule, outer items have no order or count, which is #1339's B1′ below.

## #1339, `cursor/firewall-outer-95d4` at `d5aa5ffd29484401b8f0426b82efd4fda3144f1b`: NO-GRANT

- **Blocking, B1′.** The outer phase's order and count are held by nothing. With the outer public input (`schedule`
  null), the contract decides each item on its own, and `firewall_outer_agree.py` doesn't compare sequences. On the run's
  samples, under its own public input:
  - outer sessions with statement, own and coins items dropped, swapped, duplicated or moved are accepted;
  - so is one ending in `finish` after 20 items, with no proof or check;
  - an extra masked value, a duplicated shadow item and a duplicated or dropped check are released ahead of the controls'
    cuts.

  To grant: the harness requires one item sequence across the honest sessions, and each control's to match it up to the
  cut, with a negative test; and the body, §10.4 and the README state the limit. A Lean fix (the public input carries the
  outer sequence) can follow in the contract.
- Non-blocking:
  - The samples hold no honest transcript.
  - The outer `finish` can come early.
  - Fixed-item `pads` lists are on the transcript's word.
  - The recorder holds one session per process.
- Checked: the recorder is inert without `FC_GATE_TRANSCRIPT`, and `test_firewall_outer.py` passes 6 of 6.
