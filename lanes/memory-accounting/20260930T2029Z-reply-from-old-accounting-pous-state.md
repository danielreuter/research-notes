---
id: 20260930T2029Z-reply-from-old-accounting-pous-state
campaign: verity
lane: memory-accounting
kind: reply
status: open
repo: danielreuter/verity
origin: old pous/PoUW coordinator (bc-b729c175-2ef6-418e-98fe-10896709028b, @old-accounting), written by its handoff worker bc-5ce2ff3f
---

# @old-accounting → @memory-accounting (bc-15ada664): PoUS state at the pause

Answers `note:20260930T2010Z-handoff-from-memory-accounting-pous-addendum`, items 1–6. The compute-side handoff is
`note:20260930T2014Z-handoff-from-pous-state`, and its §B is the short version of this note. Times are Pacific.

**Two store trees, both PRESERVED:**
- `art:8bd64630bc06c23d5095996d2f198ce4bd557413722ad94bd3ca3c1a949e42e9` holds `notes.md`, `preferences.md`, `docs/` and `internal/`.
- `art:09a7c9ab4574a42d81d6edbaf6c0e2be8af85384f6f4bb83e8def025ccdbfe07` holds `lean/` (with `lean/pous` and
  `lean/submissions/*`) and `code/` (with `code/pous-ref`).

Fetch one file with `research data fetch <art> --path <member>`.

## 1. The five paused PoUS agents

None of the five has been active since before 5 AM PDT on 30 Sep, except bc-87c3b40e (IDLE, last active 8:01 AM PDT). PoUS has been paused since
Daniel's overnight objectives (9:51 PM PDT on 29 Sep: PoUW only).

| Agent | What it owned | Where it stopped | What it needs to resume | Retire? |
|---|---|---|---|---|
| bc-13eada34-51d3-5b54-b330-070221ddc934, the POUS band MVP and harness | The band d = 12 MVP (`docs/pous-mvp/plan.md`), the POUS-only harness #474 and the vLLM PRs #460 (PR B) and #463 (PR C). Earlier: #208 (merged), #312 and #333 (closed) | #474 at `102a1663` (`cursor/pous-harness-c934`); #460 at `5c1cf35e`; #463 at `9ff49b9e`. The red team gave NO-GO on #474 at 9:53 PM PDT on 29 Sep over two fixes (§2) | Fix B1 and B2 on #474, get the red team's re-check at the new head, then its one timed session (§5). #460 and #463 need a GPU line; theirs was withdrawn at 8:22 PM PDT on 29 Sep | **Keep** until #474 resumes. It holds the harness's context and all three PRs. Its VM couldn't push research-notes (HTTP 403), so it relayed notes through the store |
| bc-61023cab-6d53-50c4-8e35-f47f38053ebc, efficient POUS cryptography (P2) | P2: its spec (`docs/efficient-crypto/p2-spec-draft.md`, frozen v1 on 29 Sep), the deployment memo (`docs/efficient-crypto/p2-deployment-decisions.md`), the prime certificate, and the bounty kit (`internal/efficient-crypto/p2-bounty-kit/`) | P2 proved in abstract M1, at 23.7 GB/s on an L40S. P2's Lean pins are in `lean/pous` (`P2MeetsM1p…Uncond`). **No PR of its own**: P2's code is #474's P2 v1 arm | Daniel's Decision 1 (§3). Then the SHAKE256 expander's measured cost on a device (the ChaCha8 → SHAKE256 migration), and the P2 v1 arm through #474 | Keep. It is the only holder of P2's context and the bounty kit |
| bc-87c3b40e-c587-528c-8dfa-da14013b576e, band v6 names and fibers | The band pins #428 (`cursor/pous-trusted-layer-pins-576e`), the grader hardening (`internal/p3-instantiation/grader-hardening-review-request.md`), and `docs/band-vs-dense.md` | #428 is on `main` in substance (§2). A **P3 rounds follow-up is "ready locally, held while PoUS is paused"** (`notes.md`). I didn't find it in the store or on origin, so it may exist only on its VM | Push or bundle that follow-up before anything else. Its grader-hardening patch is staged, not applied (`lean/submissions/sponge-dense/trusted-draft/install/grader-hardening.patch`) | Keep until the follow-up is safe, then retire |
| bc-4b3abaed-5e3a-5a9d-823a-3ec326d9fbd7, P3 concrete-H at 14 GB | #431 (`cursor/band-family-pin-fbd7`, the band at every segment count to 2^64), `JointClassWeightJ` and `PinFamily`, all red-team GO | Done: #431 is on `main` in substance (§2). P3 itself is superseded by the band (Daniel; `docs/project-context.md`, "P3 superseded") | Nothing | **Retire** |
| bc-c0ee31ee-703e-5bc7-bf7b-3d9af5beba8a, public-encoder variant | `docs/public-encoder/` (problem statement, protocol, sampled check) | Milestone 1 proved at k = 111, red team GO. Its pins shipped in #428 (P3 concrete-H, band, public encoder, dense at k = 111). No PR or branch of its own | A milestone-2 brief, if you want the public encoder beyond exact setup | Retire unless you plan milestone 2 now |

Also PoUS-relevant, and shared with PoUW:
- **bc-22298e90**, the Lean red team (IDLE since 10:49 AM PDT). Every staged POUS set is GO so far.
- **bc-f9184c6e**, the deployment audit, which owns #473.
- **bc-cd1084a2**, the red team that wrote the #474, #428/#431 and #461 verdicts.

## 2. PoUS PRs

Checked against `main` `b1c77be0` at 1:20 PM PDT today. Merges go through the research coordinator's train (it still runs trains).

| PR | Head | State | Merge-ready? | Red team (verdict; private path) |
|---|---|---|---|---|
| #428, the red-team-approved POUS pins and grader hardening | `540a68a7` | open | **Landed in substance.** Every `protocols/pous` file it touches equals `main`'s except `lean-audit.json`, which `main` has since extended. It shows open because of a later merge of `main` into its branch. **Close as landed**, with the research coordinator's OK | GO at `00d31707` (`internal/lean/red-team-428-431.md`) |
| #431, the band at every segment count (`BandMultiMeetsFamily`) | `ee95f2be` | draft | **Landed in substance:** every file it touches equals `main`'s. **Close as landed** | GO at `ee95f2be` (same file) |
| #473, the band certifies every count to 2^64 (`band_meets_family`); the POUS adapter refuses FP8 linears | `85edd4fb` | open | **Not on `main`:** 3 files differ (`PROTOCOL.md`, `test_pous_protocol.py`, `schemes/band.py`). Local checks passed, and root queued it on node 1 "after tonight's trains" (`notes.md`). It needs a recorded `check` on current `main`, then a train. Owner: bc-f9184c6e | none needed that I know of |
| #474, the POUS-only harness (band and P2 v1 side by side) | `102a1663` | draft | **NO-GO**: B1 (P2's recompute control re-encodes blocks past the encoded head, so P2 publishes nothing) and B2 (recomputed answers busy-wait their device time twice, overstating the attacker's latency) | NO-GO at `102a1663` (`note:20260930T0453Z-answer-from-red-team-474-delta`; detail in `internal/red-team-bench-methodology.md`, "Delta review") |
| #460, vLLM PoUS PR B (engine twins by scheme id) | `5c1cf35e` | draft | Paused; its GPU line was withdrawn. It restructures the closed #172 | none |
| #463, vLLM PoUS PR C (band and dense decode kernels), stacked on #460 | `9ff49b9e` | draft | Paused, as #460. It restructures the closed #188 | none |
| #573, vLLM migration 1 (POUS refused beside PoUW schemes that keep weight state) | `5591a44d` | draft | Compute's (bc-f4e8ae34). It waits on #567, then #576 → #578 → #585 | none |
| #496, `infra/nebius` (shared server code for Verity and POUS) | `d06d14b5` | open | Infra's | — |

- **Train order when PoUS resumes:** close #428 and #431 as landed; land #473; then #474 once it's GO; then #460 → #463.
- **Closeable as superseded:** #428 and #431 (landed). #172, #188, #312 and #333 are already closed.
- **Nothing is waiting on the research coordinator** except #473's check and the close calls.

## 3. Daniel's PoUS decisions

**None has an answer from Daniel.** Every one is "default, Daniel deferred" or open.

- **P2 key expansion: ChaCha8 or SHAKE256.** This is item F4 of the P2 freeze table, and it is decided at the default: accept
  P2-EXP-IO, realized with SHAKE256 ("default, Daniel deferred", 29 Sep). The MVP migrates from ChaCha8 and measures the cost:
  about 23.7 → 21 GB/s on an L40S is estimated, not measured. It's written in `docs/efficient-crypto/p2-deployment-decisions.md`
  (the F-table, and §F4 "Keeping the MVP's ChaCha8").
- **The SMS-to-M1 instantiation assumption** (P2–M1-SGI: square–mask–square with fresh per-block keys behaves like M1's ideal
  permutation in the storage game). This is the memo's **Decision 1**. Its default is **"not accepted yet"**, so P2 stays
  experimental ("default, Daniel deferred", 29 Sep). It's written in the same memo ("Decision 1") and in `docs/project-context.md`
  "Morning questions" (P2 deployment, question 1). Its second question, cooperating cores within one chiplet, is also still
  open.
- **PROTOCOL.md's three provisional items** (`protocols/pous/PROTOCOL.md` on `main`, "Provisional, waiting on Daniel"):
  - `|C| ≥ |W|` in `Meets` (so `|pp| ≤ 0.05·|W|`);
  - `ε_crypto ≤ 2^-128`;
  - which reveal a graded `Meets` may use.

  None is answered. They're also in `docs/project-context.md` "Still open (Daniel)": the `pp` size and the ε bound are
  provisional, and the reveal mode waits on per-answer versus shared deadlines.
- **Other open PoUS questions** from "Morning questions": should the verifier keep refusing an effective D > 5, or scale k with
  it? Who is the colleague? Where does the Notion handoff page live?
- **Nothing since has changed my recommendation.** Keep the defaults.

## 4. The PoUS store

**It's this same Project store: pous, `/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/`.** Every file PROTOCOL.md cites is
in the trees above:

- **In `art:8bd64630…`:**
  - `docs/band-vs-dense.md`, `docs/p3-cryptanalysis.md`, `docs/p3-instantiation.md`, `docs/public-encoder/protocol.md`,
    `docs/efficient-crypto/p2-spec-draft.md`, `docs/p3-gpu-measurements.md` and `docs/scheme-choice-e2e.md`;
  - `internal/p3-instantiation/` (design notes and red-team verdicts);
  - **the red-team log with §39, §40, §47 and §50**, which is `docs/lean-trusted-layer-review.md`.
- **In `art:09a7c9ab…`:** `lean/submissions/{band-chain,band-multi,sponge-dense,dense,public-encoder,efficient-crypto,…}`, the
  staging PROTOCOL.md cites as "the POUS store's `lean/submissions/…`", plus `lean/pous` (the trusted layer and grader) and
  `code/pous-ref`.

Two exceptions:
- `code/pous-band-unpushed.bundle` is stale: both of its heads (`ee781de8`, `df2c04e5`) are already on `main`.
- `internal/efficient-crypto/p2-bounty-kit/challenges-private.json` (the bounty's private challenges) is in neither tree. Ask for
  it if you need it.

## 5. Evidence and plan at the pause

- **The last PoUS runs** (all RunPod, before node 2 existed; nothing since):
  - **The band MVP's table of record:** `r20260928-032701-b4a1` on an L40S. Band12 timing-only ran 1.334 s per forward, with 20 of
    20 audits passed.
  - **The band codec in vLLM:** `r20260928-051630-d0b1` (Qwen2.5-0.5B, 1,545 MB/s, 20 of 20 audits), `r20260928-052755-b202`
    (0.5B, 1,563 MB/s) and `r20260928-053203-9ffe` (a 7B slice, 1,348 MB/s).
  - **The encoded band run:** `r20260928-215545-dbac` (`note:20260928T2355Z-handoff-from-pous-band-run-done`, lane `verity-root`,
    4:55 PM PDT on 28 Sep). It spent $2.00 against a $1.50 cap.
  - **The band rerun:** `r20260929-005714-6615` (#333 at `30d53306`, `note:20260929T0115Z-handoff-from-pous-band-rerun-done`,
    6:15 PM PDT on 28 Sep). The audit passed; tuned slowdowns are 24× prefill and 68× decode, for $0.29 of $0.60.
  - **Decode bandwidth:** `docs/band-decode-benchmark.md`, 1,550 MB/s, near the memory-bound ceiling.
  - **Audit tails and Δ:** `docs/p3-gpu-measurements.md` sets Δ = 0.5 ms.
- **What the band MVP was for:** to freeze the band result (proved, benchmarked, written up) as the first implementation of a
  generic POUS protocol, for handoff (`docs/pous-mvp/plan.md` §1).
- **What `vy-pous-harness-4090` was for** (`lanes/coordinator/20260930T0352Z-ACTION-budget-line-pous-harness-4090.md`,
  8:52 PM PDT on 29 Sep, amended 9:50 PM PDT):
  - It was one RunPod RTX 4090, capped at $1.50 and 2.0 h, for #474's first POUS-only baseline: band, then P2 v1 side by side.
  - The runs were Qwen2.5-0.5B with the NVMe probe, Qwen2.5-7B layer 0, and a 0.5B repeat for clock stability.
  - Its comparison baseline was `r20260928-032701-b4a1`.
  - **I found no record that it ran:** the NO-GO and the pause came two minutes apart.
- **The first thing I'd do on resume:**
  1. Close #428 and #431 as landed, and get #473 checked and trained. That is cheap and clears the board.
  2. Have bc-87c3b40e push its P3 rounds follow-up.
  3. Fix B1 and B2 on #474, get the red team's re-check, then run the harness once. Run it as an **exclusive one-GPU timed window
     on the central queue** (your 20:20Z inventory's ask), not a RunPod 4090, so the 0.5 ms deadlines see no co-tenant.

## 6. Traps

- **"Open" on GitHub isn't "not landed".** #428 and #431 went in through Lean train TLR, but their PRs stay open. Diff against
  `main` before assuming work is missing.
- **Some work may exist only on an agent's VM:** bc-87c3b40e's follow-up. VMs get reset (node2-ops' was wiped at 11:47 AM PDT
  today). Ask for a push or a bundle into the store first.
- **Some PoUS VMs can't push research-notes (HTTP 403).** bc-13eada34 wrote its notes into `internal/pous-mvp/` for relay. Look
  there for handoffs that never reached a lane.
- **Pod caps overrun.** The encoded band run spent $2.00 against $1.50. Pods need `--max-hours` and a `budgets.toml` line before
  launch.
- **A shared GPU invalidates timed audits.** The 0.5 ms deadlines need an exclusive GPU, and CPU load on the other socket moved
  node 2's decode timing by up to 1.35%.
- **The shared domain breaks multi-segment security:** `tag_s = salt ‖ u64 s` must be injective across segments (the MVP plan's
  "hard requirement: `shared_domain_breaks`").
- **A statement change needs a named reviewer** (lane contract §5; the Lean audit's `--update` records). bc-22298e90 has been the
  statement reviewer for every POUS set.
- **The P2 bounty's private challenges** live in `internal/efficient-crypto/p2-bounty-kit/challenges-private.json`. Keep them out
  of trees, lanes and PRs.
