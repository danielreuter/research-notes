---
id: 20260930T2031Z-handoff-from-pous-network
campaign: verity
lane: network-accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: old pous/PoUW coordinator (bc-b729c175-2ef6-418e-98fe-10896709028b, @old-accounting), written by its handoff worker bc-5ce2ff3f
---

# @old-accounting → @network-accounting (bc-ecea50f6): the network warden, bc-6b78649f and #326

Answers `note:20260930T2008Z-handoff-from-network-accounting-network-state`, items 1–7. The compute handoff's §C
(`note:20260930T2014Z-handoff-from-pous-state`) is the short version of this note. Times are Pacific.

**Where it lives:**
- The store tree `art:8bd64630bc06c23d5095996d2f198ce4bd557413722ad94bd3ca3c1a949e42e9` holds:
  - `docs/network-transparency/timing-channel.md`, the result and its history;
  - `internal/network-transparency/`: the working notes, calibration spec and data, the red-team verdicts (two rounds), the
    statement review, the ontology alignment and the scripts;
  - `internal/lean/red-team-461.md`;
  - `docs/verity-resource-ontology.md`.
- `art:09a7c9ab4574a42d81d6edbaf6c0e2be8af85384f6f4bb83e8def025ccdbfe07` holds the Lean staging, `lean/submissions/network-timing/`
  (with `review.txt`).

Fetch one file with `research data fetch <art> --path <member>`.

## 1. bc-6b78649f (network timing), IDLE since 8:34 AM PDT today

- **What it did:**
  - Proved the bucketed warden's timing-channel capacity. #461, the `network-timing` Lean package with 31 pinned theorems, merged
    at 8:07 AM PDT today in Lean train TLS.
  - Wrote the reference, #326 (`protocols/network_warden`, branch `cursor/network-timing-reference-86f3`, head `c176adb1`).
  - Filed #326's merge request at 8:35 AM PDT (`note:20260930T1535Z-handoff-from-network-warden-326-merge-request`), then went
    idle.
- **Its last brief from pous:** I didn't find a written one after that merge request. The charter (10:40 AM PDT today) lists it as "not PoUW, IDLE, for the top-level to place". Ask @old-accounting on Slack if you need the brief's wording.
- **What I'd have it do next:**
  1. Refresh #326 onto current `main`. Its recorded check `r20260930-151146-adaf` ran on base `2c4101bf`, which `main` has left 62
     commits behind, so `research merge` will want a check of the merged tree. Your 1:03 PM PDT note found it merges cleanly onto
     `b1c77be0`, with `uv lock --check` passing.
  2. Ask the research coordinator for a train. It still runs trains until the Job queue runs a whole one.
  3. Then one of the directions in §2.
- **What it owes:**
  - Nothing that I know of, beyond keeping #326 current.
  - It noted `cursor/network-timing-lean-86f3` is stale (three commits TLS superseded) and can be deleted. Leave that to its owner
    or the research coordinator; lanes never delete others' branches.
- **What it's owed:** a train slot for #326, and the resource-ontology owner's term mapping (§5).

## 2. Direction: what network accounting should deliver next

**What Daniel said** (`docs/project-context.md`):
- **The mandate** (28 Sep, 10:41 AM PDT): network transparency is a new experimental branch. Assume an active warden against
  physical-layer steganography. The timing channel is the core threat, so prove its covert capacity with the warden bucketing.
  Keep the ontology minimal and pruned, and roll out only those terms.
- **Grid decisions** (28 Sep, 12:18 PM PDT):
  - The protocol sets the grid parameters from a security parameter, and the warden only executes them.
  - The Program's canonical gate order fixes the release order.
  - The operating point is 100 ms buckets, with the slot count chosen to support honest inference.
  - **The vLLM integration should ship a calibration for it.**

**My recommendation, in order:**
1. **Land #326.** The theorem is on `main`, but the reference that executes it isn't.
2. **Ship the vLLM calibration Daniel asked for:** honest release traces from real served inference, per spatial unit. The 100 ms
   bucket was chosen on traces rebuilt from recorded runs (4.8% of K per day, 51 bit/s), with the per-token trace run deferred
   (28 Sep, 5:45 PM PDT). A real trace run on node 1 or node 2's untimed capacity is the cheapest next evidence. It fits the
   one-pool queue as CPU and untimed-GPU work.
3. **Then a live warden run** against those traces, with the exact audit on hash-committed records (#326's `commitment`).
4. **Bandwidth and latency guarantees beyond timing** can wait. Nothing from Daniel asks for them yet.

## 3. Daniel's decisions

**All answered; none is open that I know of.** From `docs/project-context.md` and `timing-channel.md` "History":

| When | Decision |
|---|---|
| 28 Sep, 12:18 PM PDT | The grid is set by the protocol from a security parameter; release order is canonical gate order; 100 ms buckets; the vLLM integration ships a calibration |
| 28 Sep, 12:33 PM PDT (round 2) | Packing is left-packed. Release is constant-rate (constant bandwidth per link, with a cap), with timing advice to sync the logical and physical clocks. POUS challenges stay inside the spatial unit. Jitter is calibrated against honest provers on the same hardware. A violation is recorded and rejected, with no halt |
| 28 Sep, 12:33 PM PDT | Terminology: "compartment" is retired for spatial unit and temporal unit, and "claim" is dropped for the repo's terms (`IntegrityProfile`, the Glossary) |
| 28 Sep, 5:07 PM PDT | The package is named `network_warden`, not `network_timing`, "for now" |
| 28 Sep, 5:45 PM PDT | Decision D: the ingress bucket is 100 ms, good enough for now; no definitive trace run |
| 29 Sep, 10:40 AM PDT | A11 and A13 were taken on the agents' recommendations (Daniel deferred): committed weights sit outside the wipe domain, and warden records are committed by hash with padding elided. The capacity bounds on committed records also assume `cr/sha-256` |

Also accepted by Daniel (in the FP8 deployment rulings): constant-rate release's padding and its first-frame latency of about 1 s.

## 4. Promises on the network side

- **To Daniel, @proofs, infra or anyone else:** none that I know of.
- **To the research coordinator:** #326's merge request stands. Keeping it mergeable is on the owner, which is now you.
- **The one soft item:** `internal/network-transparency/working-notes.md` flagged to the ontology owner that the ontology's §3 and
  decision 7 still describe report-and-halt, which Daniel dropped (28 Sep, 12:33 PM PDT). Its term mapping is still pending
  (`timing-channel.md` §4.2).

## 5. Other work that touches it

- **Resource ontology, bc-e79791ab** (IDLE; `docs/verity-resource-ontology.md`): decided at defaults. Its Glossary edit lands with
  the first resource-accounting code. Two sources show the overlap:
  - the warden's K charge follows the ontology's decision 7 (ingress only, from the last wipe before the temporal unit starts);
  - `internal/network-transparency/ontology-alignment.md` and `ontology-impact-of-redteam-fixes.md`.
- **`census/networks.json`** (on `main`) holds the benches' network model: `dc-1ms-100gbps` (the reference, 1 ms RTT at
  100 Gb/s) and `rtt-20ms-100gbps`, under Daniel's 25 Sep reporting standard, t = compute + rounds × RTT + bytes / bandwidth.
  `backends/direct/src/rtt.rs` is the frozen B-Ligero's RTT code.
- **PoUS timing:** P2's operating point allows an RTT of at most 1 ms beside Δ = 0.5 ms. The P2 memo says the verifier's real
  round trip is what matters most to measure (`docs/efficient-crypto/p2-deployment-decisions.md`). POUS challenges must stay
  inside the spatial unit, per the round-2 decision.
- **PoUW:** nothing yet. PoUW's traffic crosses no wardened link in any current design.

## 6. Reviews

- **#461: GO, with no outstanding verdict.** The red team gave GO at `19c7ddd5` (`grant = red-team` by bc-cd1084a2, label
  `1210f42c…`), with `internal/lean/red-team-461.md` as the private path. It has a statement-reviewer grant from bc-22298e90. The
  one follow-up was docs only (31 pins, not 34), and #326 carries it.
- **#326: no verdict outstanding.** Its merge request says no grant is needed: it pins nothing and touches nothing under
  `backends/flock/` or `integrations/vllm/`. The theorem's red team (two FIX rounds, then GO) is in
  `internal/network-transparency/redteam-verdict.md` and `redteam-verdict-round-2.md`.
- **Stale line:** `working-notes.md` still says the statement review by bc-440a5670 is "pending". It's superseded by the grants
  above.

## 7. Traps

- **A recorded check goes stale when `main` moves.** #326's check is on a base 62 commits old, and `research merge` refuses when
  `main` has moved past the checked commit. Re-check on the merged tree.
- **The pin count:** 34 `#print axioms` lines, 31 pinned. `occ_fill`, `leftPacked_occ_fill` and `leftPacked_fifoGrid` are proved
  but not pinned. A doc that says 34 pins is wrong.
- **A changed `lean-audit.json` record needs a named statement reviewer.** #326 changes none; keep it that way, or name one.
- **Terms:** "compartment" and "claim" are retired, and "halt on violation" is gone. Older drafts, including Daniel's September
  draft (`internal/network-transparency/sept-draft-fixed-slot-bucketing.md`), still use them.
- **The 100 ms bucket rests on rebuilt traces, not a definitive run.** Don't cite 51 bit/s as measured on live serving.
- **`network_warden` is "for now".** A rename touches the distribution, `pyproject.toml`, `uv.lock` and `tools/research/tests/test_pythonpath.py`.
