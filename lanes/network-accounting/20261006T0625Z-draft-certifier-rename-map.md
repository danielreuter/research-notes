---
id: network-accounting/20261006T0625Z-draft-certifier-rename-map
campaign: proof-service
lane: network-accounting
kind: draft
status: open
repo: danielreuter/verity
origin: network-accounting, for top's rename move (warden -> network certifier), due 07:30Z
---

# warden -> network certifier: the old-to-new map

This is checked against main `68e614869` and against #1268 (`d4d816915`, the warden program split). #1268 adds the
`warden_program` Lake package and the `Warden` namespace. If it lands before the move, apply section 4. If it doesn't, #1268
restacks onto the move and I rename it there. Every rule is case-sensitive and whole-word unless it says otherwise.

## 1. Paths

```toml
"verity/protocols/accounting/communication/warden/" = "verity/protocols/accounting/communication/certifier/"
"verity/protocols/accounting/communication/warden/tests/test_network_warden_" = "verity/protocols/accounting/communication/certifier/tests/test_network_certifier_"   # prefix: all 8 test files
"verity/Security/Definitions/Warden.lean" = "verity/Security/Definitions/NetworkCertifier.lean"
"verity/Security/Definitions/Warden/" = "verity/Security/Definitions/NetworkCertifier/"
"verity/Security/Specs/Warden/" = "verity/Security/Specs/NetworkCertifier/"
"verity/Security/Proofs/Warden.lean" = "verity/Security/Proofs/NetworkCertifier.lean"
"verity/Security/Proofs/Warden/" = "verity/Security/Proofs/NetworkCertifier/"
```

## 2. Python

```toml
[modules]
"verity.protocols.accounting.communication.warden" = "verity.protocols.accounting.communication.certifier"   # prefix: .grid .audit .active .online ...
[identifiers]
"Warden" = "Certifier"            # grid.Warden, the class (replay.py and active.py import it)
"test_warden_" = "test_certifier_" # prefix
[scripts]
"network-warden-calibrate" = "network-certifier-calibrate"   # root pyproject.toml [project.scripts]
```

The records keep their identifiers: `Record`, `CommittedRecord`, `commit`, `record_digest` and `row_digest` don't
change. N1 adds `Certificate`, the signed object per link-window over a window's records. Renaming `Record` to
`Certificate` now would put two meanings on one name. "Network certificates" replaces "the warden's records" and "the
published records" in prose only.

## 3. Lean (security and security_proofs)

Modules, with their files (section 1) and every lock key that names them: Security's `meaning`, `layers`, `reads` and
`assumptions`; Proofs' `roots`, `exempt` and `runs`; `Proofs/lakefile.toml`'s `roots`.

```toml
[lean.modules]   # prefix
"Definitions.Warden" = "Definitions.NetworkCertifier"   # and .Grid .Ingress .Run .Schedule
"Specs.Warden" = "Specs.NetworkCertifier"               # .Assumptions .Guarantees
"Proofs.Warden" = "Proofs.NetworkCertifier"             # all 11, and .CheckAxioms .DifftestMain
```

Declarations, for `audit.py --update --moved` (the four that the lock reads, plus their constructor):

```toml
[lean.moved]
"NetTiming.Warden" = "NetTiming.Certifier"
"NetTiming.Warden.mk" = "NetTiming.Certifier.mk"
"NetTiming.Warden.obs" = "NetTiming.Certifier.obs"
"NetTiming.Warden.wire" = "NetTiming.Certifier.wire"
"NetTiming.Interaction.warden" = "NetTiming.Interaction.certifier"
```

Test-only names in `Proofs.Warden.Sanity`, which no lock pins:

```toml
[lean.identifiers]
"witnessWarden" = "witnessCertifier"   # prefix: _assumptions, _jitter_varies
"aWarden" = "aCertifier"
"iWarden" = "iCertifier"
"rWarden" = "rCertifier"
"syncWarden" = "syncCertifier"
```

No guarantee moves. The namespace stays `NetTiming`, and no guarantee's name or statement mentions the warden (lean's
L3 check). The four guarantees #1268 adds (`NetTiming.SecurityProofs.Code*`) don't either.

## 4. #1268's program package (only if #1268 is on main before the move)

```toml
"verity/protocols/accounting/communication/warden/lean/Warden.lean" = ".../certifier/lean/NetworkCertifier.lean"
"verity/protocols/accounting/communication/warden/lean/Warden/" = ".../certifier/lean/NetworkCertifier/"
[lake]   # both lakefiles: the package's own and Proofs' `require`
"warden_program" = "certifier_program"   # package name, and Proofs' require name and path
"Warden" = "NetworkCertifier"            # lean_lib name and root module prefix (.Grid .Ingress .Run .Schedule .Difftest .DifftestMain)
"warden-difftest" = "certifier-difftest" # lean_exe
```

Its namespace `Warden` becomes `NetworkCertifier`. Here is every name the locks read, for `--moved`:

```toml
[lean.moved.program]
"Warden.Accepted" = "NetworkCertifier.Accepted"
"Warden.ClockSync" = "NetworkCertifier.ClockSync"
"Warden.ClockSync.delta" = "NetworkCertifier.ClockSync.delta"
"Warden.ClockSync.rho" = "NetworkCertifier.ClockSync.rho"
"Warden.LogicalFrame" = "NetworkCertifier.LogicalFrame"
"Warden.LogicalFrame.anchor" = "NetworkCertifier.LogicalFrame.anchor"
"Warden.LogicalFrame.index" = "NetworkCertifier.LogicalFrame.index"
"Warden.LogicalFrame.payload" = "NetworkCertifier.LogicalFrame.payload"
"Warden.Obs" = "NetworkCertifier.Obs"
"Warden.Obs.rows" = "NetworkCertifier.Obs.rows"
"Warden.Obs.status" = "NetworkCertifier.Obs.status"
"Warden.Program" = "NetworkCertifier.Program"
"Warden.Program.rows" = "NetworkCertifier.Program.rows"
"Warden.Reason" = "NetworkCertifier.Reason"
"Warden.Reason.coverageNeverEstablished" = "NetworkCertifier.Reason.coverageNeverEstablished"
"Warden.Reason.deliveryRefused" = "NetworkCertifier.Reason.deliveryRefused"
"Warden.Reason.dropped" = "NetworkCertifier.Reason.dropped"
"Warden.Reason.malformed" = "NetworkCertifier.Reason.malformed"
"Warden.Reason.monitorUnavailable" = "NetworkCertifier.Reason.monitorUnavailable"
"Warden.Reason.overflow" = "NetworkCertifier.Reason.overflow"
"Warden.Row" = "NetworkCertifier.Row"
"Warden.Status" = "NetworkCertifier.Status"
"Warden.Status.complete" = "NetworkCertifier.Status.complete"
"Warden.Status.notEstablished" = "NetworkCertifier.Status.notEstablished"
"Warden.StatusComplete" = "NetworkCertifier.StatusComplete"
"Warden.SyncSet" = "NetworkCertifier.SyncSet"
"Warden.SyncSet.Elem" = "NetworkCertifier.SyncSet.Elem"
"Warden.SyncSet.deltas" = "NetworkCertifier.SyncSet.deltas"
"Warden.SyncSet.rhos" = "NetworkCertifier.SyncSet.rhos"
"Warden.SyncSet.sync" = "NetworkCertifier.SyncSet.sync"
"Warden.constantRate" = "NetworkCertifier.constantRate"
"Warden.eligible" = "NetworkCertifier.eligible"
"Warden.enqueued" = "NetworkCertifier.enqueued"
"Warden.expectedRow" = "NetworkCertifier.expectedRow"
"Warden.fifoGrid" = "NetworkCertifier.fifoGrid"
"Warden.fill" = "NetworkCertifier.fill"
"Warden.handingBuckets" = "NetworkCertifier.handingBuckets"
"Warden.handingFrom" = "NetworkCertifier.handingFrom"
"Warden.ingressUpTo" = "NetworkCertifier.ingressUpTo"
"Warden.offset" = "NetworkCertifier.offset"
"Warden.payloads" = "NetworkCertifier.payloads"
"Warden.queue" = "NetworkCertifier.queue"
"Warden.released" = "NetworkCertifier.released"
```

## 5. Prose (comments, docstrings, Markdown, descriptions)

In order: "network warden" -> "network certifier", "the warden's records" -> "the network certificates", "wardens" ->
"certifiers", "warden" -> "certifier", "Warden" -> "Certifier". Three are by hand: "fail-closed wardening" ->
"fail-closed certification" (`Proofs/Warden/Counting.lean:258`, `Specs/Warden/Guarantees.lean:125`, docstrings only),
and "nothing is forwarded unwardened" -> "nothing is forwarded uncertified" (`grid.py:126`). Two more lines also move:
the `using-slack` skill's "`@network-accounting` (the network warden)" and its `registry.json` description. The Slack
handle and the lane name `network-accounting` stay.

## 6. Leave alone

- `tools/move/layout_map.toml`, `tools/move/lean_map.toml` and `tools/research/src/research/store/moves.json` are
  earlier moves' history. Add this move as a new entry rather than editing theirs.
- Store tool ids, run ids, claim ids, branch names and note ids, which are cited and never renamed. None contains
  "warden" in a way that would need to change.
- Old notes and handoffs.

## 7. Amendments from lean's certification (L3, scratch `45487b511`, run `r20261006-065120-9ee5`)

These are part of the map.

1. **Locks: rename module keys only.** Declaration names in `reads` keys, guarantees and signatures stay old, and then
   `audit.py --update --moved` runs. `--moved` compares records under their old names. The module key `Warden.Grid`
   and the declaration `Warden.Grid` are the same string, so a text-wide rename over the locks is wrong.
2. **Two `Warden`s.**
   - `Warden.` before a name is #1268's program namespace, and becomes `NetworkCertifier.`.
   - A bare `Warden` in `NetTiming` is the structure, and becomes `Certifier`.
   - The backticked library name `Warden` in `Proofs/Warden/Code.lean:11` becomes `NetworkCertifier`.
   - `warden_program` becomes `certifier_program` everywhere, docstrings and lakefile comments included
     (`Proofs/Warden.lean:17`, `Code.lean:11`), not only whole-word code tokens.
3. **Section 4 also renames both `lake-manifest.json` files:** the certifier package's own, and Proofs' entry for
   it (name and path). Without that, Proofs fails with "dependency 'certifier_program' not in manifest". This overrides
   the "lake manifests" exclusion for these two entries.
4. **A stale path:** the docstring `protocols/network_warden/verity_network_warden/schedule.py` in
   `Definitions/Warden/Schedule.lean:6` becomes `verity/protocols/accounting/communication/certifier/schedule.py`.
5. **#1268's four `Code*` guarantees read `Warden.*`,** so `--moved` takes section 4's `[lean.moved.program]` list
   as well as section 3's five `NetTiming` names: 48 in all, as lean ran it.
6. **On main without #1268,** Proofs' lock needs no `--moved`, since its reads are module keys.
