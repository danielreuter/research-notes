---
id: proofs/20261006T0615Z-draft-rename-map-proofs
campaign: proof-service
lane: proofs
kind: draft
status: sent to top for the 2:00 AM PDT rename move
repo: danielreuter/verity
origin: bc-8416bc72 (proofs coordinator), for top's rename move (note:verity-root/20261006T0550Z-report-proof-service-implementation)
---

# Proofs' rename map: prover gateway, verifier gateway, batch verifier, GPU workers

Read at `origin/main` `c305471c5` and at the heads of proofs' 44 open PRs (5 Oct, 11:15 PM PDT).

## On main: nothing of proofs' to move

None of the four old names exists on main in proofs' sense. `git grep -i` finds:

| Hit on main | Keep it | Why |
|---|---|---|
| `archive/direct/ligero/*`, `archive/ligero-verify/src/verify.rs`: "batch verifier", `test_python_file_batch_verifier_enforces_the_rule` | yes | B-Ligero's verifier of sub-batches, a different object, and frozen |
| `tools/check/guard/verity_suite_guard.py`, `tools/check/tests/test_guard.py`, `test_suites.py`: `node.gateway`, `"Gateway"` | yes | pytest-xdist's execnet gateway |
| `benchmarks/pouw/pearl_calibration.py`: `MINER_NO_GATEWAY` | yes | Pearl's upstream miner environment variable |
| every circuit "gate" (`and_gate`, `gates`, `Gates`, `xor_gate`, `sass_gate`, `ftz_gate`, `cell_gate`) | yes | logic gates and benchmark gates, not the firewall |

So the generator should exclude `\bgate\b`-style matches and the three rows above. Proofs needs no `--moved` guarantee:
no guarantee with an old name is on main.

**"coin server" (78 files on main, `CoinServer` in `backends/flock/live`).** It is the challenger's live-coin part, but
Daniel's Names table doesn't list it. Recommendation: leave it out of tonight's move; the Glossary's "challenger" line
says C-Flock's coin server is its live-coin part. Rename it later if you want one word.

## On proofs' open PRs: renamed on the branches, by proofs

Three open PRs carry the old names. They aren't on main, so the move doesn't touch them; proofs renames them on each
branch when it restacks onto the move (or before landing, whichever is first). Your dry-run restack can apply the same
map to them.

**#1270 (zk-gateway, `d828d3ea9`, base `cursor/rec-reprice-95d4`):**

| Was | Now |
|---|---|
| `backends/flock/live/src/gate.rs`, `mod gate`, `gate::{Checker, Framer, ShadowLink, Recorder, ShadowEnd, refused, skeleton, tagged, shadow_pair, cpu_seconds}` | `backends/flock/live/src/firewall.rs`, `mod firewall`, `firewall::{…}` (the item names stay) |
| env `FC_GATE`, `FC_GATE_TAMPER` | `FC_FIREWALL`, `FC_FIREWALL_TAMPER` |
| record and refusal strings `"gate"`, `"gate_opening_rounds"`, `GATE-REFUSED` | `"firewall"`, `"firewall_opening_rounds"`, `FIREWALL-REFUSED` |
| Rust/Python identifiers `gate_recheck`, `gated_round`, `gated_finish`, `GateDraws`, `GateRep`, `gate_why`, `gate_wait`, `gate_shadow`, `gate_on`, `gated`, `ungated` | `firewall_recheck`, `firewalled_round`, `firewalled_finish`, `FirewallDraws`, `FirewallRep`, `firewall_why`, `firewall_wait`, `firewall_shadow`, `firewall_on`, `firewalled`, `unfirewalled` |
| `backends/flock/tests/test_rec_live_gateway.py`; `test_the_gateway_serves_only_with_a_schedule`, `test_a_hello_the_gateway_cannot_read_is_a_refusal`, `test_the_schedule_of_the_gated_k4096_statement` | `test_rec_live_firewall.py`; `test_the_firewall_serves_…`, `test_a_hello_the_firewall_cannot_read_…`, `test_the_schedule_of_the_firewalled_k4096_statement` |
| prose "prover gateway", "the gateway" (live `PROTOCOL.md` §10.3, `rec_live.py`, `flock-circuit.rs`, `pod/85-rec-reprice.sh`) | "firewall" |
| prose "GPU workers" | "workers" |

**#1261 (rec-thm, `b4784eb8e`, base main):**

| Was | Now |
|---|---|
| Lean `Flock.Guarantees.gatewayLeaf` (`verity/Security/Specs/Flock/Guarantees/Recursive.lean`) | `Flock.Guarantees.firewallLeaf` |
| its `lean-audit.json` record `"Flock.Guarantees.gatewayLeaf"` (a new record on this PR, not on main) | `"Flock.Guarantees.firewallLeaf"`, re-pinned with `audit.py --update` on the branch; no `--moved` |
| docstrings "the gateway's commitments", "the developer's gateway" (`Guarantees/Recursive.lean`, `Assumptions/Recursive.lean`, `Proofs/Flock/Recursive/Guarantees.lean`) | "the firewall's commitments", "the developer's firewall" |
| "GPU workers" | "workers" |

**#1284 (rec-step3, `273017068`, base `cursor/rec-step2-95d4`):** prose "gateway" only (27 lines: `rec_outer.py`,
`rec_live.py`, `rec_vstage.py`, `rec_open.py`, `circuit.py`, `live/src/circuit.rs`, `tests/lean/InnerFold.lean` and its
tests) → "firewall".

Prose "verifier gateway" and "batch verifier" appear on none of proofs' open PRs. New proofs code tonight (the service's
first code, the firewall contract, the outer shape) is written in the new names from the start.

## Glossary lines proofs asks the move to carry

- **firewall**: the developer-trusted only path from the workers to the auditor. It commits every outbound message under a
  fresh salt, masks and checks or fixes everything else, and releases outer proofs on a fixed schedule. The prover is the
  workers behind it.
- **challenger**: the auditor's online service. It issues live coins, committed in advance, draws, and keeps the record.
  C-Flock's coin server is its live-coin part.
- **verifier**: the auditor's Lean verifier of record, run offline, and the outcome it writes.
- **workers**: the developer's servers and GPUs. They run the computation and nearly all proving, trusted by neither party.
