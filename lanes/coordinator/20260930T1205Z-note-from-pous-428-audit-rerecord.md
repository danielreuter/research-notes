---
id: 20260930T1205Z-note-from-pous-428-audit-rerecord
campaign: pous
lane: coordinator
kind: finding
status: open
repo: danielreuter/verity
origin: pous
---

# #428 needs an audit re-record at merge

Refers to note:20260930T0016Z-merge-request-pous-trusted-layer-pins-428.

PR #428 (head `00d31707`, granted) no longer merges cleanly into `main` at `f58d76d5`. The only conflict is `protocols/pous/lean/lean-audit.json`: since #428 was based, `main` took the `tools/lean` change `89fa48a2` (audit pin and read hashes are now SHA-256) and re-recorded its records in that format.

At the train step: merge `main` into #428, then run `audit.py --update` to regenerate #428's records in the SHA-256 format. The granted head itself is unchanged. #431 follows #428 and merges cleanly once #428 is in.
