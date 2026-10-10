---
id: 20261010T2057Z-finding-pous-lean-vor-redteam
campaign: pous
lane: memory-accounting
kind: finding
status: open
repo: danielreuter/verity
origin: memory-accounting worker (bc-7f347b4b), F7-style red team of PoUS's Lean verifier of record, branch cursor/pous-lean-vor-redteam-3cf5
---

# Red team of PoUS's Lean verifier of record (pous_check, memory challenger)

Scope: `verity/core/protocols/pous/check` (`PousCheck.Wire`, `PousCheck.TimedAudit` and its file path `pous-timed-audit`)
against `benchmarks/pous/p2_v1/wire.py` / `reference.py` and `benchmarks/pous/band_gpu/memory_challenger.py::verdict`;
and `verity/core/devices/memory_challenger/lean` against `verity/core/protocols/pous/memory_challenger.py::verdict`.
Method: a scratch differential harness on `interop.transcript` and `pous-audit-difftest serve` (full transcripts, messages
included) and on `timed_audit.lean_verdict` (the file path), with hand-built inputs per edge class. Every finding is a named
instance in `scripts/difftest_vectors.py::redteam_audits` (pinned by the Lean audit's run, 1462 instances) or in
`timed_audit.py::file_instances`, and `test_interop.py` holds the wire's to `wire.py` word for word.

## Findings

| id | severity | input | Lean (before) | Python | spec | status |
|----|----------|-------|---------------|--------|------|--------|
| F1 | HIGH | manifest `w=32, profile p2-24b, c0=2^32−16777199` (p < 2^24), honest setup and mode-0 audit | SUCCESS FINAL (verdict 1, code 0) | code 1 `no P2 prime: every payload is below p` | refuse: the codec needs every payload below p (§2, `reference.Params`) | fixed in `manifestParams` |
| F1b | HIGH | same, `c0 = 2^32+1` (p = −1 ≡ 3 mod 4) | manifest accepted, later codes by luck | code 1 | refuse | fixed (same check) |
| F2 | none (known (a)) | manifest `bps=2^16, segments=2^63` (B = 2^79), SETUP_ROOT count 0, 2^64−1, 2^15 | code 2 | code 2 | code 2 | unreachable: `parseSetup` binds B to a u64 before `rounds`; comment rewritten, 3 vectors |
| F3 | MEDIUM | audit doc with `deadline_ns` and `limit_ns` the float `1e+16` (json.dumps of a float) | `pous-timed-audit` accepts | fault `record` | fault `record` (naturals) | fixed (`Prim.PyJson.scan` in `TimedAudit.run`) |
| F3b | MEDIUM | `NaN` / `±Infinity` in a field the verdict never reads (`clock`, `device_ns`, ready `port`) | fault `record` / `ready` | judges (accepts the honest record) | judge | fixed (same) |
| F6 | MEDIUM | SETUP_COMMIT manifest `"w":1e1000000` (20 bytes) | no verdict for minutes (`1e100000`: 7 s; Json.parse expands the exponent) | code 1 at once | code 1 | fixed (`PyJson.scan` before `Json.parse`) |
| F4 | LOW (known (b)) | manifest with a duplicate key, or a float whose Python repr round-trips (`"w":64.0`) | code 1 `manifest is not canonical JSON` | code 1 `duplicate manifest key K` / `manifest value has wrong type` | code 1 | unfixed: needs a duplicate-reporting parser and Python's float repr in Lean; codes agree |
| F4b | LOW (known (b)) | manifest `NaN`, `±Infinity`, `1e400`, a lone `\ud800`; the three no-P2-prime refusals | code 1, other messages | code 1 | code 1 | fixed: Python's messages |
| F5 | LOW | mode-1 beacon list naming round 1 twice, wrong value first | code 2 | success (dict: last wins) | n/a (Python's API is a dict) | fixed (`findRev?`) |

Checked with no finding: the frame envelope and lengths; setup order, binding and the 1, 2, 3, 5 precedence; the private
root; checkBlocks; challenge and response identity, index and nonce; path length and index bits past the tree; LATE at
`elapsed > Δ + RTT` on both (on-deadline accepted); decode and the held payload; trailing frames; FINAL; an elapsed time
past u64 (refused on both); TimedAudit's field and order checks and strict refusals (a segment-count gap is intentional).
Memory challenger: the port's fuzzer already draws a flipped, truncated or emptied signature, `q` past `2^h`, a stranger's
or untrusted key, a replayed leaf, receipt and send edits, duplicated and reordered openings, `j` past u32 and index past
u64; a wrong-size public key and an undecodable signature read as no signature on both; openings are looked up last-wins on
both. No disagreement found.

## Rulings

None needed: every fix aligns the Lean with the reference and the spec's text, and no wire format, guarantee or spec text
changes. A recommendation, not an ask: `PousCheck.TimedAudit`'s statement (`TimedAuditAccepts`) is over a parsed `Json`;
how the files are read (as Python's `json` reads them) now lives in `run`, outside the statement.

## Tests (branch head 1c4b0f5ea)

- `uv run tools/verity/check/suites.py pous-check verity/core/protocols/pous`: pous-check 25 passed; pous 337 passed, 8 skipped.
- `cd verity/core/protocols/pous/check && lake build`: 150 jobs, success.
- `uv run python tools/verity/lean/check.py --build --update verity/core/protocols/pous/check`: AUDIT PASS (893 declarations; difftest run 1462 instances).
- `uv run python verity/core/protocols/pous/check/interop.py --all`: 40 transcripts, 0 mismatches.
- `uv run python verity/core/protocols/pous/check/timed_audit.py --generated`: 321 instances, 0 differences.
