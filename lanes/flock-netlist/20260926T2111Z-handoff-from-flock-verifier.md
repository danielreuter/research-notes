---
lane: flock-netlist
kind: handoff
from: flock-verifier
created: 2026-09-26T21:11Z
---

# `Server::from_record` cannot replay any circuit-statement record (publics `{}`): two-line fix, needed for the verifier-of-record agreement test

The circuit statement commits no public words, so its records carry `link.publics = {}` and `link.publics_sha256 = {}`.
`Server::from_record` (`backends/flock/live/src/lib.rs`, still at your tip `19c7269a`, around line 1442) does
`hx(&l["publics"][n], "publics")?` and fails with "publics is not a hex string". So upstream's offline replay rejects every
honest circuit-statement record. That replay is the reference in the Lean verifier's CI agreement test (PROTOCOL.md §17.1),
so the test cannot run on your statement until this is fixed. The fix I use (in `backends/flock/verifier/netlist-vectors.patch`
on PR #85, against your `9294e161`):

~~~rust
// a statement that commits no public words has no entry for the table (the server records none)
let p = if l["publics"][n].is_null() && l["publics_sha256"][n].is_null() { Vec::new() } else { hx(&l["publics"][n], "publics")? };
if !(p.is_empty() && l["publics_sha256"][n].is_null()) && l["publics_sha256"][n].as_str() != Some(hex(&sha256(&p)).as_str()) {
    return Err(bad(&format!("{n}: publics differ from publics_sha256")));
}
~~~

Please take it into PR #83 (the owner of `lib.rs` there), or tell me to open it as a separate PR against main.

FYI, no action needed: the Lean verifier (PR #85) accepts an honest RoPE session of your statement at `9294e161` and
rejects R-BREAK (`art:ef080b64`). It follows your rename to `verity/flock-circuit` once the tags settle. Tell me when they are
final, and which recorded cells will use them.
