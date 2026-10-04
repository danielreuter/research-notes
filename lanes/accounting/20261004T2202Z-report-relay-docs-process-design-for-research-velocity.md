---
id: 20261004T2202Z-report-relay-docs-process-design-for-research-velocity
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/process-design-for-research-velocity.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/process-design-for-research-velocity.md`, sha256 `55c3ca69a7cf9a8989075981be59ba358348c9724c63f1875bc0e34adc7081ba`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Process design for research velocity

Daniel, 29 Sep 2026: "let's actually game it out and see what the impact is on research velocity", and the first step
toward a skill that makes agents assess that for any new process. This doc has five parts:

- what research velocity is in Verity;
- what last week's data shows about where it goes;
- what makes a process good or bad for it;
- a method for assessing a proposed process;
- that method applied to the Lean-first norms in
  [lean-first-protocols](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/lean-first-protocols.md).

It ends with a sketch of the skill.

## Summary

- **Velocity here is the rate of trustworthy decisions and claims, not the rate of commits.** A fast result that is
  later retracted costs velocity.
- **Process costs only matter in the resources that are scarce.** Those are your attention, the merge path, files many
  lanes edit, the rules every agent must read, and pods. Machine time and agent time are cheap and run in parallel.
- **A good process is almost free while exploring, and concentrates its checks where a result is relied on:** landing on
  `main`, publishing, citing, or handing to another implementer. It enforces in code, labels rather than blocks, keeps
  one source, and has an exit.
- **Gamed out on last week's changes, the Lean-first norms cost nothing on most changes.** They would have stalled one
  real burst: POUS changing its default scheme three times in nine hours. The fix is a lighter version with one match
  point (publish or cite) and automatic lag detection instead of a hand-kept lag list.
- **The real cost of Lean-first is one-time:** making each protocol's Lean executable, and reviewing the pins that then
  change. Schedule it per protocol once its design settles, and pilot it on the one-stage audit.
- **Daniel's tiers (29 Sep 05:04Z) are this doc's principles applied to proofs.** Tier 1 (no proof) is fine while
  exploring, tier 2 (a proof, not connected to the code) for many applications, and tier 3 (connected) is the target.
  The tier is a label that fires at the one match point, and its best home is a field generated from `lean-audit.json`,
  not a rule in prose (§5b).

## 1. What research velocity is here

Verity's research produces four kinds of output:

- security claims: statements proved under named assumptions;
- measurements: the benchmark tables;
- design decisions: which scheme, which parameters;
- working integrations: vLLM.

Velocity is how fast these converge to something you or a colleague can act on. Process changes it through five
channels:

| Channel | What it is | How process moves it |
|---|---|---|
| Loop latency | Time from an idea to a result someone trusts | Builds, checks, queues and reviews on the critical path add to it |
| Parallelism | How many lanes can work at once without colliding | Shared files, single queues and global rules subtract from it |
| Decision latency | Time a result waits for a human decision | Every blocking question adds to it; defaults and delegation cut it |
| Yield | How many results stay true | Checks at the right point raise it; errors caught late cost rework and retractions |
| Reuse | How easily a result is found, cited and built on | The evidence store, labels and generated views raise it |

The first three are paid on every change. The last two pay off only when an error would have happened, or a result
gets reused. So a process earns its place when its benefit on the few changes where it matters exceeds its cost on all
the changes it touches.

**Scarce resources**, the ones to price:

1. **Your attention**, which is the bottleneck.
2. **The merge path:** trains, `check` on the train's tip, the coordinator.
3. **Files and queues many lanes pass through.**
4. **The words every agent reads before working.**
5. **Pods and money.**

Agents are cheap and parallel, but they follow rules literally and at scale, and they don't push back on a bad rule. A
rule's cost is multiplied by the number of agents and how often it fires, and nothing prunes it unless someone decides
to.

## 2. What last week shows

These numbers come from `main` and `gh` for Sep 22 to 29, the project store, and the notes repo.

| Measure | Value | Reading |
|---|---|---|
| PRs merged since the repo started (Sep 21) | 185, about 23 a day | High throughput |
| Open to merged, median and 75th percentile | 2.6 h and 5.7 h (all PRs); 4.7 h and 11.5 h (the 24 that touch Lean) | Lean PRs take about twice as long |
| Open PRs | 109, of which 68 are drafts; the oldest is about two days old | A large queue that still turns over |
| Merged PRs touching `tools/`, `AGENTS.md` or skills | 71 of 185 (38%) | A large share of the work is on process |
| Commits touching the root `AGENTS.md` | 67 in 7 days, 25 of them on Sep 27 | Rules every agent reads change about ten times a day |
| Lane contract versions | 2.0 to 2.4 in about two days, each new rule with a "Why:" incident | Rules accrete one per incident |
| Words an agent reads before working | 2,007 (`AGENTS.md`) + 2,204 (lane contract), plus 3,293 in `backends/`, plus any skill | 4k to 7.5k words of rules |
| Commits touching a protocol's `PROTOCOL.md` | 57 in 7 days (POUS: 33), against 52 to those protocols' Python | The prose is edited more often than the code it describes |
| POUS's default scheme | Changed three times in about nine hours (Sep 27 16:49 to Sep 28 01:23: overwrite chain, dense, band) | Research moves in bursts |
| POUS's experimental P2 | v0, v1 and v2 in about five hours (Sep 28) | Exploration is fast when nothing gates it |
| "Waiting on Daniel", "pending Daniel's review", "decisions for Daniel" | 108 mentions in 39 store docs; 4 in docs on `main` | Decisions queue on one person, mostly outside the repo |
| Research Lean outside `main` | The store's `lean/`: about 235k lines, with copied and flattened files and a diverged trusted layer (organization plan §1) | Work routes around a heavy path |
| `check` on a train's tip | 35 to 47 minutes (organization plan §1) | One failure delays every PR on the train |

And two incidents worth remembering:

- **A process that paid for itself.** #118 made `merkle_binding` vacuous by redefining `MerkleScheme.Collision`. The
  axiom audit passed it; only the pins and a statement review would catch it (lane contract §5).
- **Drift between two sources.** The dense scheme's Lean was re-certified "matching the code" (`f8181a51`), after the
  tag format had diverged between Lean and Python. And `sampled_proofs`' step 4 still describes a beacon draw that
  "The law" has ruled out.

## 3. Good and bad process

| Principle | Why | Good here | Bad here |
|---|---|---|---|
| **1. Price it in scarce resources, not steps** | Ten automatic checks that take seconds cost less than one approval per change | Suites cached by input: only what changed reruns | A named reviewer on every change to a pinned definition, when that reviewer is always you |
| **2. Gate where results are relied on, not where they're made** | Errors are expensive only once something rests on them; exploration results are mostly thrown away | Pins only on cited theorems; P2 as `experimental`; `research run` preserving every attempt without asking anything else | `PROTOCOL.md` kept current on every behavior change (57 edits a week) |
| **3. Enforce in code, with the fix in the message** | Agents follow prose unreliably, and every prose rule taxes every agent's context; a check costs nothing until it fires, and it teaches at that moment | The audit's escapes list; FINAL's finish checks exiting 3; the boundary tests | Rules that live only in `AGENTS.md` or the lane contract. The contract says it: "a rule you can't see enforced is not protection" |
| **4. Label instead of block, unless the error would pass unnoticed** | A label lets work go on and lets readers filter; blocking is for errors nobody would notice until they cost a lot | `(alg.)` on algebraic-hash results; `experimental` schemes | Blocking a merge on documentation parity |
| **5. One source; generate the rest** | Every hand-kept copy doubles edits and drifts | The entities render the site reads; `lean-audit.json` records | Hand-written proved/open tables; audit fields re-recorded by hand after every merge; two POUS trusted layers |
| **6. Add no serialization points** | A file every PR edits, one queue or one reviewer caps how many lanes can work at once, and turns one failure into many waits | Per-package Lean packages; per-lane worktrees | Soundness's flat root import list, which conflicts across trains (#310, #287 and #293 against #319); `AGENTS.md` as a map most PRs edit |
| **7. Make the official path the cheapest one for exploring** | If following the process costs more than the exploration is worth, work moves outside it, and the cost returns at integration | Lane branches that build against `main` (the organization plan's proposal) | The store's research Lean, whose landing needed flattened 34k-line files and renames by regex checked by hand |
| **8. Make decisions stand alone, with a default that proceeds** | A reviewer near capacity makes waits grow sharply, so one blocking question stalls many lanes; a provisional default keeps work moving and is cheap to reverse | POUS's provisional `Meets` clauses, which carry defaults; your rule that questions must stand alone | Questions that block until answered, with no default |
| **9. Give it an owner, a named failure and an exit** | Rules accrete one per incident and rarely leave | The organization plan's rule that old results leave `main` | Contract rules with no retirement condition |
| **10. Change process rarely, and in code** | Rule churn has its own cost: every agent's instructions and every in-flight brief go stale | A check whose message says what changed | 25 edits to the root `AGENTS.md` in one day |

In one sentence: **a good process makes the right thing the easy thing during exploration, and makes the wrong thing
loud where a result is relied on.**

## 4. How to assess a proposed process

This is the method the skill would ask an agent to follow before proposing any rule, check, gate, review step or
document that must be kept current.

1. **Name the failure.** Give an incident or a concrete risk, how often it happens, and what it costs when found late
   (rework, a retracted table, a false claim to a colleague).
2. **Find the smallest mechanism.** Before writing a rule, try a label, a code check, or a generated artifact.
3. **Pull the real changes.** Take the last one to two weeks of git history in the area it touches and group the changes
   by type, with counts: behavior changes, refactors, proofs, experiments, promotions, publications.
4. **Walk each type through the process.** For each, record:
   - the steps it adds;
   - the wall-clock time it adds on the critical path;
   - whether it blocks or labels;
   - who acts: the machine, an agent, the coordinator, or you.
5. **Price the scarce resources per week:**
   - your minutes;
   - merge-path minutes;
   - new files or queues that many lanes touch;
   - words added to always-read rules;
   - pod money.

   Compare the total with the failure's expected cost.
6. **Run the tests:**
   - Where does it fire: exploration or reliance?
   - Is it code or prose?
   - Would the error pass unnoticed without it?
   - Does it add a second source?
   - Does it serialize lanes?
   - Is working around it cheaper than following it, and if so, where would the workaround appear?
   - Does it add a blocking decision, and what's the default?
   - What retires it?
7. **Simplify and walk again.** Drop any piece whose cost exceeds its benefit.
8. **Pilot.** Apply it to one package, measure the same numbers for a week, then extend or retire it.

**Default budget.** Exceeding any of these needs a stated reason in the proposal.

- No new step on the common path (branch edits, exploratory runs) unless it's automatic and takes under a minute.
- No new blocking human approval on the common path. Human gates sit at reliance points, as stand-alone questions with
  a default.
- No new file or queue that most PRs must touch.
- A few lines at most added to `AGENTS.md`; the detail goes in a skill or in the check's error message.
- An owner, a named failure with its incident, and an exit.

## 5. Worked example: the Lean-first norms, on last week's changes

The norms as proposed in "When the Python must match" have these parts:

- `check` regenerates the vectors on every commit;
- the Python passes every vector except those in a hand-kept lag list (`tests/vectors/lag.toml`);
- three match points: publishing a result, citing a theorem for a run, and making a scheme the default or bumping a
  wire-format version.

Here is what they would have done to last week's changes in POUS, PoUW, the one-stage audit and sampled proofs, and
what a lighter version would do.

| Change, last week | Count | As proposed | Lighter version |
|---|---|---|---|
| Python that doesn't change behavior: drivers, records, API, messages | about 30 | Nothing | Nothing |
| Experimental schemes (P2 v0, v1, v2) | 3 | Nothing | Nothing |
| Lean proofs and re-certificates (POUS) | about 14 | Nothing: the vectors come out identical | Nothing |
| Defaults and laws: POUS overwrite chain to dense to band in nine hours, the one-stage stratified law, PoUW's `ncp-v1` v1.1 | about 6 | Each switch waits for an executable Lean spec, new vectors and pin review before it lands. That adds 1 to 3 hours each, and would have serialized the Sep 27–28 burst | The switch lands. Results stay labelled until the spec and Python match, and nothing stalls |
| Lean spec changes the Python doesn't match yet | new | A lag-list entry per change: a hand edit, and a file lanes collide on | Detected automatically: the Python may fail a case only if that case's expected value changed since the Python last passed it |
| `PROTOCOL.md` edits | 57 | Become Lean docstrings, with the proved/open status generated | The same |
| Headline results published (tables, Notion) | a few | Must match | Must match: the one match point |
| Protocol PRs that change behavior, now touching Lean | about 6 | Move from the non-Lean median of 2.2 h to the Lean median of 4.7 h (11.5 h at the 75th percentile), about 15 to 36 PR-hours a week, mostly not on anyone's critical path | The same, less where the spec imports no Mathlib and no pin reads the change |
| One-time migration | — | POUS's executable spec with SHAKE-256 and `Π₂`, 52 pins reviewed, PoUW's pins restated, the exporter and the site | The same, scheduled per protocol after its design settles |

**Where it pays:**

- The one-stage stratified law was implemented twice, in `protocols/one_stage` and in `Flock/Draw.lean`.
- The dense tag format drifted between Lean and Python, and the Lean was the one changed to match.
- `sampled_proofs`' step 4 contradicts its own law section.
- Each protocol has built its own Lean-to-vectors plumbing: POUS's three check files and generate scripts that need the
  trusted layer on one VM, and PoUW's `ncp_lean.py` "on the integrated package".
- Headline claims become claims about the code that runs.

**Where it costs:**

- **The one-time migration, above all your review of the pins that change.** Keeping pins to headline results (the
  organization plan's decision 8) and letting the red team review the rest cuts that down.
- **Lean PR latency on behavior changes.**
- **More research Lean staying in the store,** if the spec rules felt heavy. That's why they apply only to `Spec/`
  modules, never to research Lean on branches.

**Verdict.** The steady-state cost is small, and it falls on changes that already needed a decision from you. The version
as first written carried two pieces the walkthrough can't justify:

- **The hand-kept lag list:** a second source, and a file lanes would collide on.
- **The "default or version bump" match point:** it would have stalled a real burst for no benefit, because a result
  built on an unmatched default is already labelled.

Drop both. Keep one match point, "publish or cite as the protocol", with lag detected by `check`. Then pilot on the
one-stage audit, whose executable Lean already exists.

## 5b. The tiers, through the same tests

Daniel's ruling of 29 Sep 05:04Z sorts every implemented protocol into three tiers:

1. no Lean proof;
2. a Lean proof with no mechanical connection to the code;
3. a Lean proof mechanically connected to the code that runs.

The definitions, the decision that vectors alone leave a protocol at tier 2, the provisional norm for when tier 1 is
fine, and each protocol's placement are in [lean-first-protocols](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/lean-first-protocols.md),
under "Tiers" and "Where each protocol stands". Read through §3, they come out like this:

- **They gate at the reliance point (test 2).** Tier 1 costs nothing while exploring. The first move up is triggered by
  the one match point from §5, a result published or cited as the protocol's security, not by a scheme becoming the
  default. So the POUS burst of Sep 27–28 would still land.
- **They label instead of block (test 4).** A tier travels with each result the way `(alg.)` does. Nothing fails
  `check` because a protocol is at tier 1.
- **They define tier 3 by the trusted code, which is what keeps them cheap (test 1).** Soundness holds against every
  prover, so only the verifier's decision, its draws and its setup need connecting. Provers, GPU kernels and drivers
  keep matching vectors, as decided, and never wait on Lean.
- **The home is code, from one source (tests 3 and 5).** A tier field computed from what the certificates already name,
  and what `lean-audit.json` already records, costs a small reader once and nothing per change. A prose rule in
  `AGENTS.md` would fire nowhere, and would be rewritten each time Daniel dials the norm in (test 10). The
  `process-design` skill is the wrong audience.
- **The exit is built in (test 9).** Tiers drop by themselves when the connection breaks, and a run keeps the tier it
  ran at.

Placing the protocols also turned up the failure the field would catch. Every POUS certificate names a theorem that
`check` doesn't audit (`band_meets_64`, `chain_meets_64`, `P2MeetsM1pB19Uncond`), yet the storage profile cites it as
what an accepted audit establishes. The pinning rule in `AGENTS.md` already forbids this. It went unnoticed because
nothing checks it: test 3 again.

## 6. The skill

A sketch, following `.agents/skills/authoring-skills`:

~~~yaml
---
name: process-design
description: >
  How to propose, change or retire a process in Verity (a rule in AGENTS.md or the lane contract, a check or gate in
  `check` or `research merge`, a required review or approval, a document that must be kept current, a convention every
  lane follows) and how to assess its effect on research velocity first. Use when adding a rule after an incident,
  adding a gate, requiring a reviewer, adding a file every PR must update, or when a process feels heavy.
---
~~~

The body would have four parts:

- the definition of velocity and the scarce resources (§1, in a paragraph);
- the ten principles as short test questions (§3);
- the eight-step method with the default budget (§4);
- a template for the proposal: the failure, the smallest mechanism, the walkthrough table, the price per week, the test
  answers, the pilot, and decisions for you written to stand alone.

A supplementary `examples.md` would carry this doc's worked example, with the commands that pull the numbers: `git log`
by path and date, and `gh pr list` for time to merge. `AGENTS.md` gets one routing line.

The skill is written: `.agents/skills/process-design/SKILL.md`, draft PR
[#359](https://github.com/danielreuter/verity/pull/359). Because the repo allows only certain markdown filenames,
there's no `examples.md`; the worked example and the proposal template are inside `SKILL.md`.

Both questions are settled (Daniel, 29 Sep):

1. **Does the skill also cover retiring processes?** Yes. It includes a retirement pass using the same tests. It runs
   weekly over `AGENTS.md` and the lane contract, and the draft names the coordinator as its owner, which Verity root
   is confirming.
2. **Should the numbers in §2 be one command instead of an agent's ad hoc queries?** No: just the skill, which gives the
   commands.
