---
id: firewall-contract/20261006T0725Z-finding-firewall-contract
campaign: proof-service
lane: firewall-contract
kind: finding
status: active
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
---

# The firewall's contract in Lean, and the inner firewall's agreement with it

Item P2 of `note:verity-root/20261006T0550Z-report-proof-service-implementation`. Branch `cursor/firewall-contract-f5e7`
on #1270 (`cursor/zk-gateway-95d4` at d828d3ea9); the PR body is the store's `internal/proofs/firewall-contract-pr.md`.

- The contract (fresh salt, mask-then-check, uniquely fixed) is an executable Lean definition in the verifier package,
  `Flock.Firewall.run`, run by `flock-firewall check`. Five theorems say what an accepted session lets out
  (`holds_commit`, `holds_masked`, `holds_fixed`, `holds_coins`, `holds_finish`), plus `firewallLeaf_eq`.
- D8 (a) is a named `Prop`, `Flock.Firewall.FirewallComputes`, in the verifier package's new assumptions module, with
  `holds_computed` under it. Not in core's Lean (it reads the C-Flock firewall's transcript, which only the verifier
  package defines) and not in `verity.claims` yet (no rendered table cites it).
- Agreement with the inner firewall (`rec_live.Proxy`), 22 cases: the honest sessions are accepted by both; five of the red
  team's six gaps on #1270 are refused by both; six tamper controls are refused by the contract alone, as expected. One
  divergence class: verdict OBJECT on #1270's inner firewall for it, details and the recommended fix in the store's
  `private/firewall-contract/open-order.md`.
- Real sessions: 4 of 4 recorded K = 4096 inner sessions accepted by both (`r20261006-070620-e02d`, vy-nebius-1, CPU only;
  Lean's check 0.26 s and about 90 MB a session).
- Lean audit of the verifier package passes with the seven new pins and no existing pin changed: `--update` in
  `r20261006-074513-c43e`, the pinned commit audited in `r20261006-074037-42e8` (5,839 declarations, the three standard
  axioms only). The new pins need a named statement reviewer.
- Not covered: the outer phase (`gate.rs`) and its `FC_GATE_TAMPER` controls. That needs a transcript exporter there, in
  #1270's `flock-circuit.rs` or a new binary.
