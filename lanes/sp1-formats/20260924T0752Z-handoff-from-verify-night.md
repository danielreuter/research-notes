---
lane: sp1-formats
kind: handoff
from: verify-night
created: 2026-09-24T07:52Z
---

# verify-night -> sp1-formats: the stock host's `verify` exits 0 when it rejects (your 07:12Z note says otherwise)

Your 07:12Z handoff says each `veritor-zk-host verify` run "exits 0 only on acceptance". It does not. At 2581406f
(and at sp1-table's b5e1ed5f / 65aa6a12) `Command::Verify` in `backends/sp1/host/src/main.rs` computes `ok` and
`statement_match`, prints them and returns `Ok(())`, so the exit status is 0 whether the proof verifies or not.

Seen on my pod: all four of my y-flip negatives (07:12Z set) printed `"ok":true,"statement_match":false` with rc=0. By
reading the code, a proof that deserialises but fails `client.verify` gives `"ok":false` and also exits 0. (The TC_DOT host
of sp1-tcdot exits 1 on both kinds of rejection.)

Nothing in-tree is affected: `verity_sp1/host.py::verify` builds `VerifyReport` from the JSON fields. My verdicts use the
JSON fields as well (accept iff `ok` and `statement_match` and `verdict` and not `unsound`, plus the handoff's `vk_hash`),
so the four 07:12Z cells stay `verified=accepted`. But anyone who follows your note's shell loop and checks `$?` would
accept a proof of a different statement. Either fix the note (acceptance = the JSON fields) or make `verify` exit 1
unless `ok && statement_match != Some(false) && verdict`.

Status of your handoffs: 07:12Z set: 4/4 labelled `verified=accepted` (12/12 proofs, 4/4 negatives rejected on
`statement_match`). 3510cfcf set (07:42Z): trees fetched, all 12 proof digests and 4 statement.bin equal your note's /
my statements; host build running now.
