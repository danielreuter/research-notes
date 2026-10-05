---
id: network-accounting/network-accounting/20261005T2320Z-draft-consolidation
campaign: network-accounting
lane: network-accounting
kind: draft
status: open
repo: verity@b87eeef64 (the Lean layout move's head, #1225)
origin: network-accounting (bc-ecea50f6), for Daniel's finish-the-layout ask via top (5 Oct, 4:07 PM PDT); read-only survey of the tree by bc-dc51b1d8
---

# The network warden's code: what to consolidate

Scope: the warden's Python (`verity/protocols/accounting/communication/warden/`: 9 modules, 1,734 lines, 83 tests), its
benchmark drivers (`benchmarks/network_traces/`: `record.py`, `replay.py`, `active_replay.py`, two shell scripts; 2,852
lines, 37 tests), and its Lean (`verity/Security/{Definitions,Specs,Proofs}/Warden/`) as far as it ties to the Python.
Nothing outside these imports the warden except the calibrate entry point and the boundary test. Every change below is in
network-accounting's own code unless it says otherwise.

Already in flight, so not repeated as proposals:
- K out of core: #1216 (`k_share(bits, k_bits)`, `--k-bits`; ready, in ci's train). `K_BITS` goes.
- The warden program split (`cursor/warden-program-split-728f`, tonight): the executable Lean leaves the trusted tree
  for a dependency-free package beside the Python, with the difftest and its generator
  (`warden/lean/scripts/difftest_vectors.py`, today a one-file leftover of the old Lean package). The trusted
  `Definitions.Warden` stays the `Finset` reference form, and `Proofs/Warden` proves code = definitions.
- #1205 (draft) adds a third value to `online.declare`'s return, which makes item 6 more pressing.

## Ranked: value against risk

| # | Change | Value | Risk | Touches | Ruling? |
|---|---|---|---|---|---|
| 1 | One schedule kernel: `schedule.eligible` and one "next hand" step, used by `schedule.handing_buckets`, `active.Shaper.tick`, `online._Link` and `calibration.choose_syncs`' cost | high | med | warden core, replay | no, if the existing equality tests stay green |
| 2 | A public stall/change hook on `Proxy` instead of `proxy._changed = Stalls(...)` | high | med | `active.py`, `active_replay.py`, its tests | no, if stalls fire where they do now |
| 3 | Doc and path hygiene after the two moves | med | low | PROTOCOL, READMEs, Lean headers | one: where the timing-channel prose lives |
| 4 | One `Setup` and one sync-policy parser for `replay` and `active_replay` | med | low | benchmarks only | no |
| 5 | Shared bucket helpers: ingress `⌈t/τ⌉` in four places, egress `⌊s/τ⌋+1` | med | low | `calibration`, `active`, both benchmarks | no |
| 6 | Named results for `online.declare` and `calibration.choose_syncs` (today positional tuples) | med | low | warden, both benchmarks, tests | no |
| 7 | A typed `Advice` for `Proxy` (syncs, or a prover with its windows) instead of `prover_args`' dict popped into `**advice` | med | low | `active.py`, `active_replay.py` | no |
| 8 | `calibration.replay_fifo` built on `grid.released`, so sizing can't disagree with the warden's FIFO | med | low | `calibration.py` | no |
| 9 | Units in names: `Proxy.slack` is seconds and `bucket_ms` is ms beside it; rename `slack` to `slack_s` | med | low | `active.py`, callers | no |
| 10 | `record.build_trace`/`convert(**rules)` take a frozen `DropRules` | med | low | `record.py`, its test | no |
| 11 | Library defaults that encode a calibration outcome (`GridParams.bucket_ms = 100`, `ingress_bucket_ms = 100`) move to the CLI | med | low | every `GridParams(...)` call | no; yes only to change 100 ms |
| 12 | Small: shared trace fixtures for the two benchmark tests; one percentile helper; `__init__`'s module list (omits `active`, `commitment`); tests reading `warden._fault`; drop the `arrivals` ingress encoding once tests use `arrival_ms` (the recorder writes only that) | low | low | warden and benchmark tests | no |
| 13 | A typed calibrate report (`to_json`/`from_json`) instead of a nested dict re-parsed by key | med | med | calibrate, both `Setup`s | yes, if a report key changes: reports are custody records |
| 14 | `Proxy`'s TCP server out of core into the benchmarks or an integration, keeping `Shaper`, `Bucketer` and the framing codecs in core | med | high | `active.py`, `active_replay.py` | yes: a component boundary |
| 15 | Rename the Lean namespace `NetTiming` to match `Warden` | low | high | every warden Lean file, locks | yes: changes every declaration's name and record |

Items 1 and 2 are the two worth doing first. Item 1 is the only duplication on the security path: the eligibility
formula `a + d + ⌊kρ⌋` is written three times (`schedule.eligible`, `_Link._eligible`, inline in `_Link.cost`), and
the hand rule `max(eligible, previous hand, ready, last)` twice (`handing_buckets`, `Shaper.tick`). The hindsight and
online algorithms stay separate (they see different data); they share the step. Item 2 removes the one place a
benchmark writes a private attribute of core code.

## Duplication, in detail

- **The schedule step** (item 1): `schedule.py:88-149`, `active.py:151-179`, `online.py:131-160` and
  `calibration.py:161-204`. Survivor: `schedule.eligible` plus a pure step function in `schedule.py`. Callers: `Shaper`,
  `online.Prover`, `choose_syncs`, `replay_configuration` (which re-derives hands itself at `replay.py:178-180` instead
  of calling `run_shaper`).
- **Sync-policy parsing** (item 4): `replay.parse_sync_policy` and `active_replay.parse_sync_policy` differ only in the
  offline name (`hindsight` against `model`). Survivor: one parser taking the offline names. Both online branches
  already call `online.rule`.
- **`Setup`** (item 4): `active_replay.Setup` subclasses `replay.Setup` and rebuilds both `GridParams` at the report's
  frame size, because the parent forces 8 bytes. Survivor: one `Setup(frame_bytes=...)`.
- **Bucket arithmetic** (item 5): `calibration.py:302`, `active.py:373`, `replay.py:231`, `active_replay.py:349` for
  ingress. Survivor: two helpers in `grid.py`.
- **Two published-record forms**: `commitment.commit` (the protocol's) and `active_replay`'s zlib `pack_record` blob
  (custody size). Both stay; the blob's left-pack check should call `grid.row_left_packed` rather than repeat it.
- **Python ↔ Lean**: deliberate (the difftest pins it), with one exception the split fixes: the difftest's generator
  lives in the Python package's leftover `lean/` directory and the Proofs lock reaches back into it.

## Fragile APIs, in detail

- `Proxy(... , **advice)` after `advice.pop("syncs")` (item 7), and `proxy._changed = Stalls(...)` (item 2): the stall
  benchmark depends on `Proxy`'s internal event loop shape.
- Order-dependent use that is correct but undocumented: `Warden.tick` exactly `buckets` times before `close_window`;
  the online prover declares at the window's first tick; `Audit` takes the unit's sync from the first egress link it
  checks, so the order of link checks matters for multi-link units. These go into PROTOCOL.md as invariants. Changing
  the `Audit` order would change verdicts, so it is not proposed.
- Stringly typed: rule names (`last`, `cover-K-M[-…]`, `sticky-…`) parse in `online.rule` only, which is right; the
  violation tags (`advice`, `mismatch`, `duplicate`, `no-verdict`, `status:<reason>`) are also the difftest's wire
  format, so add Python constants beside them and keep the strings.

## Dead code and stale references

- No dead CLI options in `calibrate`, `replay` or `active_replay`; every flag has a caller.
- `Reason.DROPPED` has no production fault path (only a commitment test injects it), but the Lean mirrors it. Keep it,
  documented as reserved for a non-proxy enforcer.
- Stale paths from the two moves: `Definitions/Warden/Schedule.lean:6` cites `protocols/network_warden/...`;
  `PROTOCOL.md` (lines 5, 68-69, 108, 308, 356, 363-364) cites `lean/`, `NetTimingDifftest.lean` and
  `lean/lean-audit.json`; `Proofs/Warden/README.md:35,49` cites `NetTimingDifftest.lean` as a path. The docs give the
  suite selector `verity-network-warden`, which needs checking against `suites.py --list` after the move.
- `docs/network-transparency/timing-channel.md` is cited by nearly every warden Lean header and the Proofs README and is
  not in the tree.

## What needs Daniel's ruling

1. **Where the timing-channel write-up lives** (item 3). Proposal: PROTOCOL.md's sections become the one current-truth
   home, and the Lean headers cite them. The old long-form document's history is in Notion and the notes.
2. **Whether the active warden's TCP proxy stays in core** (item 14). Proposal: not now. It is stdlib-only and the
   warden's enforcement, and the split only pays once a second integration needs the core without the proxy.
3. **The Lean namespace** (item 15). Proposal: keep `NetTiming`. A rename changes every record for no change in meaning.

Everything else is an ordinary refactor in network-accounting's code, each behind the existing tests, and lands as
small PRs after the move: item 1 first (with a test that the four users agree on random schedules), then 2, then the
benchmark-only items 4, 6 and 7 together.
