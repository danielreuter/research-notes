---
id: proofs/20261007T0020Z-repository-layout-feedback
campaign: verity-repository
lane: proofs
kind: draft
status: open
repo: danielreuter/verity
origin: proofs coordinator (bc-8416bc72), for top's 6:30 PM PDT (01:30Z) collection, thread 1791331591.766669
---

# proofs on "Verity repository" (Daniel's proposal, art:8ae63b72…)

Refs: main `e7b5caa89`, the proposal as copied at 2026-10-07T00:05Z. Proofs' area covers:
- C-Flock: the Rust prover, the `verity_flock` Python, the Lean verifier, and its soundness and ZK analysis.
- Recursion: VBridge and the rec stack.
- Sampled proofs' one-stage audit and the proof service's verifier side.
- The firewall's zero-knowledge release.

## 1. Where it goes

| Today | Home in the layout |
|---|---|
| `backends/flock/verifier/lean/` (`Flock`, `FlockVerify`, no dependencies) | `core/protocols/flock`: already Lean, the verifier of record |
| `verity/Security/Proofs/Flock/*` | `Security/Proofs`; its spec goes to `Security/Definitions` and `Properties` when #1355 extracts it |
| Rust prover (Flock `b684b12` + `backends/flock` patches), `verity_flock` (M0 circuit builder, `rec_vstage.py`, staging) | `ml/`, except the zero-knowledge part (below) |
| upstream Rust verifier cross-check, selftest build (`+seed-injection`), `selftest_records.py` | `tests/`, as oracles |
| `verity.protocols.verification.sampled_proofs` (`one_stage`, `service.py`) | `experimental/` by the rule as written; see 2(a) |
| `benchmarks/one_stage` | `benchmarks/`, the measuring side |

**No home:**
- **The firewall.** The README Glossary calls it "the developer-trusted only path from the workers to the auditor", which
  "releases outer proofs, which are zero-knowledge". `Flock.Guarantees.ZeroKnowledgeHidden` is a property of the prover
  side, not the verifier: it quantifies over `P : LigProver`, and it names the honest prover's self-check stop in
  `zk_veil.rs`. Its code is Rust and Python, and none of it is verifier code. That's the same shape as network-accounting's
  certifier runtime and memory-accounting's challenger: code on a trusted device that a property is about.
- **The coin server**, on the auditor's side: it commits every coin at `Hello`, under `keyed-cr`.

**Wrong side of the line:** "ml/ affects only speed and completeness" is false for hiding. A prover change can leak the
witness, through the masks, the hm96 key, the salts or which leaves get opened, while every verdict stays the same. So
the zero-knowledge outer prover and the firewall belong on the trusted side. Alternatively, the line should read "speed,
completeness and nothing a property states", with the prover code ZK depends on listed by name.

## 2. Rules that would stop, slow or break proofs' work, and what to change them to

**(a) "core/ holds only Lean; until then experimental/", with "anything the verifier runs lives in core/".** Three
things on the verifier's path today aren't Lean:
- the one-stage draw and registration (`sampled_proofs.one_stage` and `service.py`, with coins from
  `verity.primitives.randomness.derive`);
- the verifier's own public-inputs file, PoUW's `TileAnchors.public_inputs` (Python);
- the reference for the program format and partition (`verity.primitives.circuits`), which vectors pin to the Lean
  `Q_word` check.

Sending these to `experimental/` makes core's PoUW import `experimental/`, because PoUW imports sampled proofs.
Change: I agree with circuits. core/ may hold a Python mirror of code a property names, pinned to the Lean by shared
vectors and listed like the `@[extern]` exceptions, until it's ported. Also say that core/ never imports experimental/.

**(b) "Every soundness property has a completeness property beside it", against the VBridge ruling.**
- Completeness of `flock-verify` on real proofs needs the Rust prover. A Lean completeness theorem would be about a Lean
  reference prover, not about what runs.
- Keep the VBridge ruling: a proof where it's feasible, else a pinned `runs` test, with the check enforcing the pair.
- The vacuity we actually hit wasn't a missing completeness theorem. Every `EndToEnd*` assumes `scopeOk` (v1 rows), so
  on PoUW's v2 `TileRead` sessions they say nothing. Meanwhile main's verifier accepts `--zk --public-inputs` with no
  theorem behind it (note:proofs/20261006T2352Z-public-input-restack-plan).
- Change: check each property's hypotheses on a pinned deployed instance, inside `verity check`. That means the
  verifier's own scope check (`ProvedScope.check`, #1179) run on a real staged statement of each protocol. That's "no
  vacuous claims" in a form a check can enforce. Compute-accounting is already doing this by hand for step 3's first toy
  statement.

**(c) "Computational assumptions are reductions; never an axiom that SHA-512 is collision-resistant."**
- We have no axioms today; the audit forbids them. Assumptions are named Props, taken as hypotheses.
- C-Flock's collision hypotheses (`TableCRZ`, `LinkCRZC`) are already per-adversary. They're about the finder built
  from the prover's strategy, not "SHA-512 is collision-resistant" for every adversary, so they're reductions in shape.
  Restating each conclusion as `Pr[accept a false statement] ≤ ε + Pr[finder(P) outputs a SHA-512 collision]` is a
  rewrite, not new math. It does change the 8 `EndToEnd*` records and #1179's 36 `FailClosed` ones, so do it once, in
  the move to `Properties/`.
- Two assumptions don't reduce to a SHA-512 collision: `hash-derived-key` (`HashDerivedKeyHm96`, "the pinned hm96 key
  hides at 2⁻¹⁹³") and the coin server's `keyed-cr`. Both are hiding or PRF claims about a fixed function.
- Change: "an assumption is a hypothesis about an algorithm built from the adversary (a finder or a distinguisher), never
  a claim over every adversary about a fixed function". Use reductions to collisions where they exist.

**(d) Properties as numbers (`@[about …]`, never `2^-Pouw.queries`).**
- C-Flock's error depends on the circuit the verifier accepts, and the 2026-10-04 ruling makes it one theorem over every
  such circuit. ZK's bound, for example, is `Σ_j 2·|Hid_j|·2⁻¹⁹³`. A single number exists only at the verifier's caps.
- vbridge's header-cap PR (in progress) makes it one number: it refuses `k_log > 27`, `slot_log > k_log`, and a lookup's
  `in_bits` beyond the largest pinned table, before any `2^…` is computed.
- I agree with lean's change: a Property is the number at the deployed parameters and caps, proved from a parametric
  lemma in Proofs/, and the check refuses a free parameter in a Property.

**(e) "Conflicts are resolved by commits on the PR" and "a stack lands as one queued group", with grants pinned to heads.**
- Proofs' rec stack is a tree, not a chain: rec-step3 has three children (#1315, #1318, #1347), and #1270 has two chains
  (#1343 → #1349, and #1303 → #1323 → #1339).
- Tonight's restack (main merged into 13 heads) voided every grant. ci's 00:01Z trial on tip 87 found two siblings
  (#1315 and #1347) conflicting in `rec_vstage.py`.
- Change: grants carry when the PR's own patch is unchanged (#1412), as ci says. Define a stack as a tree queued as one
  group, or serialize siblings by rule.

## 3. Wrong about proofs' area

- "Every guarantee is about the code that runs" holds only for C-Flock's verifier, and C-Flock's `ZeroKnowledgeHidden`
  is about the prover, which the layout puts in ml/.
- "One file per protocol" for Properties doesn't work for C-Flock:
  - Today it has 874 pinned guarantees (`FlockSoundness` 778, `FlockLevel3` 56, `Flock` 29, `FlockVBridge` 11, out of the
    1,705 in `verity/Security/lean-audit.json`).
  - #1170 cuts those to the 41 that something outside Lean relies on. Even 41 in one file conflict across parallel lanes.
  - So use one file per property; lean's split per module works too.
- `core/protocols` lists "sampled proofs and Flock's verifier". Sampled proofs is Python today (`one_stage`,
  `service.py`); only its statement is Lean.
- The proposal implies we have a collision-resistance axiom. We don't; see 2(c).

## 4. One change

The check on a pinned deployed instance from 2(b): `verity check` discharges every property's hypotheses on a real
staged statement of each protocol, with the verifier's own scope check. It would have caught tonight's gap (PoUW's v2
sessions outside every `EndToEnd*`) when the first v2 statement was staged, not in a scoping pass later. A completeness
theorem beside each soundness theorem wouldn't have caught it.

## What `lean-audit.json` becomes

It becomes the Properties record, one file per property under `Security/Properties/<area>/`:
- Each file carries the property's statement, its named hypotheses, its `meaning` and every definition it reads. Those
  are today's `guarantees`, `meaning` and `reads`, per entry.
- `layers` become Lake package edges.
- `reads_exempt` shrinks to C-Flock's prefix until #1355, plus lean's `Proofs.Pouw.PearlC.FlockTile` line until PoUW's
  spec moves.
- Lemmas stop being pinned: only properties that something outside Lean relies on get a file (#1170's 41 for C-Flock).

Lock-touching PRs then stop conflicting with one another, and those conflicts are what void grants today.
