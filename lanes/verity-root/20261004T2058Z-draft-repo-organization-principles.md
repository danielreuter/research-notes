---
id: 20261004T2058Z-draft-repo-organization-principles
campaign: verity
lane: verity-root
kind: draft
status: open
repo: danielreuter/verity
origin: verity-top's repository-layout agent (bc-d6f8b221, under bc-7f347b4b)
---

# Repository organization: the principles after the survey (4 Oct, 2:45 PM PDT)

This is version 9: Daniel's rulings of 2:21 PM PDT and the fan-out.

Version 8 added Daniel's rulings of 2:03 PM PDT on round 2's questions (below), and old-accounting's
finding on P2's response window.

Version 7 It moves the plan out of an agent store into the notes, after Daniel's ruling of 1:47 PM PDT: qualitative writing goes in the research notes, where it can be shared, and data in the evidence store. The Glossary's new terms are verity#1127.

Version 6 (1:45 PM PDT) moved to the README Glossary's vocabulary (Daniel, 1:38 PM PDT): a *guarantee* is what a
table or a ledger relies on as proved, and anything else proved is a *lemma*, so "cited" is gone as a status. And it
dropped the per-area design ledger: the notes' approaches registry already records every line of work, with its status,
reason and evidence.

Version 5 (1:35 PM PDT) was the first with round 2 folded in. It folds in the survey's second round (Slack thread `1791144994.129499`), which all ten coordinators
answered: @comms, @ci, @network-accounting, @lean, the lander, @compute-accounting, @proofs, @circuits (rounds 1 and 2
together), @memory-accounting, and @infra on the replay question. Nobody objected to the plan. It also adds Daniel's
rulings of 1:30 PM PDT: `experimental/` is a directory, and row captures aren't kept. The questions still with Daniel
are under "Still open". comms' ownership map draft is #1124.

Version 4 (1:20 PM PDT) added Daniel's rulings of 1:13 PM PDT: specs are minimal, every lemma lives in
`security_proofs/`, and the lock protects as little as possible. Version 3 came before it. Version 1 (12:10 PM PDT) was the picture Daniel, the layout-trial lane (`@architecture`, pending
#1113) and `@lean` reached in chat; the coordinators were surveyed on it. Version 2 (12:45 PM PDT) folded in the nine
answers (@comms, @ci, the lander, @network-accounting, @lean, @proofs, @memory-accounting, @infra, @compute-accounting).
Version 3 adds Daniel's rulings of 12:51 PM PDT and the follow-up answers from @compute-accounting,
@memory-accounting, @proofs and @lean (Slack thread `1791143698.815249`), and @lean's check of which specs separate;
@infra's is pending. Who said what in the
survey is in those Slack threads. Lean's guide to the Lean workflow is being updated to match. Nothing has moved.

## Daniel's rulings on the architecture after the move (5 Oct, 05:38Z)

These come after the recursive zero-knowledge architecture (the proofs coordinator's "Recursive zero knowledge: the
system architecture"). Under it, both soundness and zero knowledge are proved in Lean, and the prover's trusted code is
Lean too. These rulings fix the target the next layout derives from. They don't change tonight's move.

Locked:
1. The trusted code is Lean: each party's program over the whole run (registration, draw, the inner and outer sessions,
   the verdict, the profile), and the statements about it.
2. Python, Rust and CUDA make up the environment and the workers. The model treats the environment as adversarial, so a
   bug there can only make a run fail; it can't make a false claim pass.
3. Lean and everything else meet only through canonical bytes, with one Lean reader and vectors pinning the format.
4. The whole run's composition is in Lean, with end-to-end soundness and zero-knowledge theorems.
   This also settles the zero-knowledge threat from untrusted kernels (captain, 06:12Z). The inner C-Flock session runs
   on the developer's rack with zero knowledge off, a proxy salts and hashes every outgoing message, and the outer
   session proves V* with zero knowledge on and live coins. So a malicious kernel can't leak the witness, as long as the
   egress premise holds: the rack meets the auditor only through the developer's program, which the warden checks.
   The zero-knowledge theorem takes that premise as a named assumption; kernels need no trust.
   Its cost, measured at real size (proofs, 2:12 AM PDT, 09:12Z; note:proofs/20261005T0633Z-finding-rec-reprice,
   art:453bd179bb84e81ab73001606749b0ba70e6ae1e8314c5dbe2f7864731fa427e): at K = 4096 the outer proof takes 5.85 s, 6.7×
   the inner's ZK-off prove, against a go bar of about 0.5×. With the inner it is 1.25× main's `--zk` prove, 6.4× its
   bytes and 8× its Lean verify. Optimised by estimate, the outer is still about 4×. Daniel ruled 7:51 AM PDT (14:51Z):
   recursion stands at this cost, so the rollout goes on past step 1.
5. Security proofs live apart from specs and judges.
6. Untrusted code sits inside the component it serves, so there is no top-level `kernels/` or `provers/`.
7. The Python package is `verity/`, and keeps tonight's import names.

Also ruled:
- Tonight's move lands as planned (about 14:00Z).
- Overnight evidence default: if both evidence workers (the run-model draft and the co-change and Lake evidence) agree
  on a layout, the captain prepares that layout's move map. Nothing lands without Daniel.
- `verity/` is the whole system: a mixture of Lean and Python per component, where the Lean is the trusted part.

Open, for the morning memo (about 12:00Z). The memo is `note:20261005T0640Z-draft-lean-layout-memo`; the evidence
below feeds it:
- Whether the assumptions and guarantees sit inline with each component's Lean, or the components' Lean holds only
  executables and the security statements live together somewhere else. The captain leans to the second: `verity/`
  holds Lean executables with no dependencies, and one `security/` package on Mathlib holds the assumptions, guarantees,
  the model and the proofs. The memo checks this against the co-change and Lake evidence.
  Daniel's proposal (05:45Z): `security/assumptions`, `security/properties`, `security/proofs`. The captain's reply adds
  `security/model` (games, adversaries and probability, which assumptions and properties are both written in). It also
  says how statements attach to programs: by import and constant name, recorded by the audit's lock, with paths that
  mirror the component a statement reads. The memo specifies this layout.
  Daniel (05:51Z): the model is part of the assumptions; directories are capitalized as Lean does; the term is the
  captain's pick. So the target is `Security/Assumptions/` (with the model's definitions in it), `Security/Guarantees/`
  (the Glossary's existing term, so no rename) and `Security/Proofs/`. A cloud worker (bc-8a03b032) is inventorying every
  Lean module against it, including which programs use Mathlib today.
  Co-change and Lake evidence (bc-e529d785, 06:06Z; scripts, results and the layout-C pass in
  `art:8e07b30b6b1dc2908d7553d86c7f028561a53fcb3e3f0d6b8684431d85d42ff4`): of 170 Lean-touching PRs, statements inline (A) keep 49% in one directory and a
  separate `lean/` tree with judge, specs and proofs as packages keeps 41%. Proofs inline, as today, keep 87%. Flock
  is 123 of the 164 Lean PRs; protocol specs move with their proofs in 28 of 29 PRs; Lean spans two areas in 3 of
  772. Lake works for every layout, but module names are global with no duplicate check (a namespace guard test is
  needed), a Mathlib root costs about 8 GB (seven roots today), and a program that imports no Mathlib still clones
  it if its package requires it. The same worker is measuring the ruled target (`Security/` plus
  `verity/<component>/lean`) for the memo.
  Run-model draft (bc-c7b00243, 06:09Z; branch `cursor/run-model-draft-7bd6`, `experimental/run_model/DESIGN.md`,
  prototype log `art:69981778cc169c07aa583138cff652aabbe175c6033f61c989e3990b01d1dd42`): the composition theorem is
  stated over party programs that cut across components, plus a model that needs Mathlib, so it wants the security
  statements together and the programs dependency-free. The `check` audit cache is per package, so one large security
  package re-audits everything on any change (45 to 70 minutes cold for soundness alone); a per-module audit cache, or
  Proofs as a package of its own, comes first. Its prototype also hit the module-name collision (verity#1144). Open:
  whether `Security/` sits inside `verity/` or beside it.
  The Lean run-model draft (bc-03e91581, 06:26Z; branch `cursor/run-model-draft-c3b2` at `f7716b464`,
  `experimental/run_model/`, every proof still `sorry`) agrees on the shape. It has three packages: `exec` (the party
  programs, on the executable verifier alone, no Mathlib), `spec` (Protocol, Assumptions and Guarantees on core and
  Mathlib, no ArkLib) and `proofs` (on ArkLib). That is `verity/<component>/lean`, `Security/{Assumptions,Guarantees}`
  and `Security/Proofs`. It brings three things for the memo:
  - The run's programs cross areas (the send gate runs C-Flock's `Statement.verify`, and the coin server and proxy
    share hm96), so they are a composition of their own. Its `exec` requires a backend while its statements cite
    protocols, which the 2026-10-03 ruling (card `d9eb2f28`: no package requires both a protocol and a backend) forbids.
    Locked point 4 needs that ruling relaxed for the run layer alone; protocols still import no backend. Daniel decides.
  - The extraction and the simulator (`ZkOuter.layer`, `wmsg`, the Goldreich–Kahan finder) are trusted text, since a
    weak one makes the guarantee vacuous, but today they sit behind ArkLib. They move into `Security/Assumptions`, or
    the soundness guarantee's meaning can only be read in the proofs.
  - C-Flock's soundness package has its own `Game` type, separate from core's; it needs a transport, or C-Flock moves onto
    core's `Game`.
- Whether "judge" is a concept at all. Daniel thinks it's just part of the toolkit; the captain agrees. The run-model
  draft agrees: the run needs only parties, one program per party, hosts and workers; the deciding code is library
  functions the programs call, and the Glossary has no "judge" entry to retire.
- Whether Lean drives Python, with the party program as the main loop and the workers serving its requests. The
  run-model draft measured it on a toy audit (2^10 rows, a quarter wrong, 16 drawn, about 1% acceptance expected): Lean
  driving 0 of 50 accepted, an honest Python driver 0 of 50, a Python driver that reruns `draw` 20 of 20. Lean driving
  removes the coin-server assumption and two custody ZK assumptions, for 9.4 µs median per small request over pipes
  (0.35 ms at p99.9, so PoUS's 0.85 ms timing loop should own its socket and clock in Lean, measured on a node first).
- Where the runs layer (the onsite and remote products) lives.
- Native SHA-512 and carry-less multiply under named assumptions (still with Daniel).

## Daniel's rulings on the Lean layout (5 Oct, 8:53 AM PDT, 15:53Z)

These answer the memo (`note:20261005T0640Z-draft-lean-layout-memo`), worked through with the captain in chat from
8:03 AM PDT, with `@lean`'s views on the lock (Slack 1791213468.840519). They replace the open layout items above.

1. **Lean is split into code and security analysis.** Code is the programs and the interfaces they use (C-Flock's
   verifier, the PoUS grader, the warden, and each party program as it moves to Lean). It lives with its component,
   in files beside the Python, or a Lean directory when it's large. It is untrusted and never imports `Security/`.
2. **`verity/Security/` holds the analysis, in three trees** that mirror the components:
   - `Definitions/`: trusted vocabulary (reference circuits, games, the silicon model, shared assumptions such as
     SHA-512 collision resistance), on Mathlib.
   - `Specs/`: one per executable, its named assumptions → its guarantees, stated about the code's own constants. A
     protocol's own assumptions (the driver assumption) sit in its spec.
   - `Proofs/`: a package of its own (ArkLib allowed). Every proof lives here, including the equivalence of code's
     definitions to the trusted ones.

   Trusted text is `Definitions/` plus `Specs/`. A definition both code and specs need is written twice: in code as the
   program uses it, and in `Definitions/` as a plain reference, with the equivalence proved in `Proofs/`.
3. **Proof fields stay with their definitions.** Anything whose type is a `Prop` is proof and untrusted, even inside a
   trusted file (`bandExtra_lt`, `Circuit.toCircuit`'s fields). Anything that is data is trusted text.
4. **The lock attaches properties to programs.**
   - Assumptions are listed by name in the lock with their own records, like guarantees, instead of being recognised by
     module.
   - A program's last declaration lists the guarantees it must satisfy by name (`List Lean.Name`, no import). The lock
     checks that each one exists, reads one of the program's constants and is proved, and records the list as `required`.
   - The reads walk stops at a program's constants: a spec reads that the program exists, not its body.
   - Code that runs but no spec reads is reported, not failed, with exemptions that each give a reason.
   - Where Python still runs an algorithm, the lock records the Python–Lean pairing and the test that checks it, so the
     gap is a named assumption.
5. **Lean drives as far as possible.** The memo's ask 5: phased one assumption at a time, in the run-model draft's order.
   Each step retires the assumption it covers. PoUS's timing loop is measured on a node before it moves.
6. **Names.** `lean-audit.json` becomes `lean-lock.json`, and `tools/lean/audit.py` becomes `lean_check.py` (the `check`
   step `lean-check`). `spec_alert` must treat a renamed lock file as a move first, so that the rename sends no DMs.

Taken as following from these (Daniel can object):
- The memo's ask 2 is relaxed for the run's own Lean: the run's code calls C-Flock's verifier, and its spec cites
  protocols. Protocols still import no backend.
- The memo's ask 3: the extraction and the simulator move into `Definitions/`, or `Specs/` for the spec that names them.
- The memo's ask 4: `Security/` sits inside `verity/`.
- The memo's step 1 goes ahead now: the namespace guard (verity#1193), the audit's `srcDir` fix, `Main` renamed
  `FlockVerify`, the two ArkLib cuts, the warden's five definitions over `List`, and the per-module lock cache.

## Daniel's direction on the proof service (5 Oct, 7:11 and 7:17 PM PDT; 02:11Z and 02:17Z on 6 Oct)

1. **VBridge proves one direction** (7:11 PM): V* accepts ⇒ the verifier of record accepts. Completeness stays a test.
   Relayed to proofs (Slack 1791252706), to be recorded in note:proofs/20261005T2345Z-draft-vbridge-plan.
2. **The proof layer is the one service every accounting protocol uses** (7:17 PM). PoUW, PoUS and the warden are
   users of it: each calls its methods, consumes its outcomes, and keeps no infrastructure of its own (no commitment
   scheme, randomness, draw, transport, verifier, gateway or audit record). A protocol states only four things: what
   is committed, which units need proofs (or the policy that selects them), the check each selected unit must pass
   (a public Program or Definition), and what it does with the outcome. The service owns commit, live coins and the
   record, selection (sampled proofs' draw), proving (direct ZK or recursion), verifying, and the integrity profile.
   The architecture starts from proofs' design (agent store bc-7f347b4b,
   `internal/recursive-zk-system-architecture.md`, "How a protocol calls the layer"), and @proofs,
   @compute-accounting, @memory-accounting and @network-accounting work it out together (Slack 1791253199.410869):
   - by 11:00 PM PDT (06:00Z): each accounting lead lists what its protocol owns that the service replaces, with
     paths, and writes its protocol as a service user; @proofs drafts the interface (methods, types, which party runs
     each, the guarantee each carries, what core already has against what's new);
   - by 7:00 AM PDT (14:00Z): one joint note, `proof-service-architecture` (kind: draft, owned by @proofs, agreed by
     the three accounting leads): the API, each protocol's call sequence, what each protocol deletes, the migration
     order, the open questions with recommendations. It goes to Daniel in the morning and to Notion once he agrees;
   - the first user is compute-accounting's served-zk lane tonight (one served request whose commitment the proof
     opens), built against proofs' draft interface where that doesn't slip its 11 PM verdict;
   - the warden says whether it is a user of the service, part of its deployment (RecursiveZK's egress premise), or
     both.

## Status (captain: verity-top's layout agent, from 2:12 PM PDT)

Daniel named this agent captain of the migration. This section is the tracker; the captain keeps it current, and anyone
can pick it up from here.

*Superseded at 4:30 PM PDT (Daniel: "YOLO the PRs"):* the moves go as one generated move on one branch,
`cursor/layout-move-c3b2` (`tools/move/layout.py` plus its module map), fixed forward there until `check` passes on
`vy-mig-check-1/2`, then landed through `research merge` with a short hold on other merges. Out of it, each following the
same way when ready: C-Flock's Lean (after fail-closed and canonical V1), PoUW's Lean split (after slice 6), and
C-Flock's Rust and CUDA (until proofs draws the ZK layer). The prep PRs below are no longer gates; the branch merges in
what it needs. Lanes (4:40 PM PDT):
- the Python half: `tools/move/layout.py` and its map on `cursor/layout-move-c3b2` (captain's worker);
- the Lean half: lean, on `cursor/layout-move-lean-c3b2` (core, NCI, the warden and PoUS, by `tools/lean/split.py`);
- restacks: `tools/move/restack.py` reruns the move script on an open branch, then merges, so only content conflicts
  remain; it is dry-run across every open PR (captain's worker, on ci's `rename_merge.py`);
- look-ahead: what the move breaks outside `check` (store derivations, `-m`, readers of `census/` and fixtures,
  module-keyed data, guards that fail open), fixed before or with the move (captain's worker);
- pre-scripted follow-ups that fire when their blockers land: C-Flock's Lean (proofs), PoUW's Lean (compute-accounting);
- the node side and a redeploy right after landing (infra); the landing check sharded over five pods (ci);
- once the generated commit exists: one fix-forward worker per area, each on a sibling branch merged into the move.

The old path, kept for reference:

*Critical path to the first move* (core's Lean split into its spec and `security_proofs/`, a pure move):
1. ci's check-time fixes land, ci's tip `afacde975` among them, and ci measures check time. Owner: ci.
2. Content-keyed caches: ci's suite keys, circuits' per-target key (descriptor digest), lean's audit key (module name and
   source hash). Then `move-check`, which certifies a PR as a pure move (ci's fast lane, `note:20261004T2105Z-draft-refactor-ci-fast-lane`).
3. lean's validator change: a `security_proofs/<area>` package validated against its spec's lock, the reads check, an
   `owner` field, and lift certification. Waits on 1.
4. Core's split, checked cold and then warm, with the lock byte-identical. Owner: lean.

*In parallel, none of it on the critical path:*
- verity#1127, the Glossary and the writing rule: ready in the queue.
- verity#1124, the ownership map: comms.
- #1053's DM batching, then one lock reduction per package under the 2:03 PM PDT guarantee ruling.
- `research replay` (infra), each area's replay-set labels, and two reruns at main (PoUW's approved).
- Approaches: PoUS has 12 registered; the others are in progress. Done: old-accounting copied the 44 `store:pous/` files into the
  notes, and all 129 registry cites now point at those notes (verity#1145 adds `--uncite` and takes `store:` out of `EVIDENCE_RE`).
  Still to copy: the kernel pages the skill points at (gotchas, technique catalog, panel, the rtx-pro briefs), where compute-accounting decides.
- Move maps (drafts, for owners to correct): `note:20261004T2125Z-draft-move-inventory`,
  `note:20261004T2125Z-draft-move-map-backends-integrations-tools`, `note:20261004T2125Z-draft-move-map-protocols`,
  `note:20261004T2125Z-draft-move-map-core`.
- circuits splits its bindings and pins per Definition.

*Fan-out* (Daniel, 2:21 PM PDT: finish in short serial time). Every lead launches workers on its pieces that don't wait
(the kickoff, Slack `1791150333.889129`). The captain's four workers draft the move inventory (everything a move
breaks, and whether Python import names follow the directories) and the move maps for core, the protocols, and backends,
integrations and tools, for owners to correct.

*With Daniel:* the PoUW bridge's statement review (proof accepted to `TileGood`), when compute-accounting brings it.

## Why (Daniel's goals)

1. Make the trusted computing base cleaner.
2. Make the repo discoverable, with the tree following the architecture.
3. Clear up sprawl, and consolidate code that uncoordinated agents duplicated.
4. Prepare for many new contributors.
5. Standardize CI and infrastructure.

## Daniel's rulings (4 Oct, 12:51 PM PDT)

- **Consolidate, don't delete.** This is a research codebase. Cleanup must not lose past theoretical results, empirical
  results or efficient algorithms. Old paths stay findable, with why they failed, so nobody goes down them again
  unknowingly.
- **The Lean goes first.** The first migration step consolidates all of the Lean into `security_proofs/`. That's where
  most of the code is, and it keeps every past theorem through the migration.
- **Empirical results can be rerun.** Compute isn't the bottleneck.
- **The H100 lane stays.** The question is how to organize it, not whether to drop it.
- **Theory-to-practice gaps** (C-Flock's zero-knowledge on the binary, PoUW's torch screen) are normal and will recur.
  We build up hygiene for them over time.
- **Device-side enforcers** live in their protocol, under the role that runs them.
- **The products are named the *onsite protocol* and the *remote protocol*.**
- **Experimental is a label,** not a directory. (Reversed at 1:30 PM PDT.)

And at 1:06 PM PDT:

- **Superseded infrastructure can be deleted.** Math results, constructions and kernels go case by case, and the default
  is consolidation, above all on the untrusted side.
- **Everything except the specs moves into `security_proofs/`.** Once the specs' guarantees are proved, the math inside
  `security_proofs/` gets consolidated: it's surely duplicated, confusing and disorganized today. Being untrusted, it
  can be refactored freely, as long as every lock entry keeps its statement and still validates.

And at 1:13 PM PDT:

- **Specs are as concise as possible, and every lemma lives in `security_proofs/`.** As much machinery as possible
  goes there. That minimizes the TCB.
- **The lock protects as little as possible:** the guarantees and the definitions they read. This reverses version 3's
  "keep all 1,818 entries".
- **`verity/` is trusted, not trustworthy:** if it's wrong, security degrades.
- **The parsers of C-Flock's superseded formats leave the verifier early,** as part of C-Flock's move.
- **Archived frozen backends are re-checked at their own commits.** Their table rows cite those commits.
- **The settled version goes into the README** (the architecture section and the Glossary) and AGENTS.md, in one PR.
  No Notion write-up.
- **One more survey round before anything moves,** including @circuits.

And at 1:30 PM PDT:

- **`experimental/` is a top-level directory.** `verity/` holds only what a guarantee depends on, so the README can say:
  if the code in `verity/` implements its spec, then wherever a guarantee's assumptions hold, its conclusion holds of the
  running system. Work in progress and work kept for study live in `experimental/`, and promotion into `verity/` is a
  PR.
- **Row captures aren't stored,** or are shrunk drastically to what Match reads.

And at 1:38 PM PDT:

- **Use the Glossary's vocabulary.** A *guarantee* is a proved statement that a table or a ledger relies on; anything
  else proved is a *lemma*. Terms this plan adds go into the Glossary ("Glossary changes", below).

And at 1:47 PM PDT:

- **Qualitative writing goes in the research notes, data in the evidence store.** A Cursor agent store is its
  agent's scratch, and nothing cites a `store:` path (AGENTS.md, verity#1127).
- **Update the Glossary now** (verity#1127).

And at 2:03 PM PDT:

- **A guarantee is a theorem something relies on as proved:** a ledger row, a published table, the docs site, a claim
  id in `verity.claims`, or code that reads its result. A mention in prose, a PR, a test or an internal table doesn't
  make one (verity#1127's second commit). The lock reductions go by it.

And at 2:21 PM PDT:

- **Finish the migration in short serial time.** Leads launch workers on every piece that doesn't wait, and spend compute
  where it shortens the critical path. Pods stay bounded, and GPU work still names its question (verity#1133).
- **ci resolves rename-only conflicts** in the train tip's merge commit and names each one; judgment conflicts go to the
  owner (verity#1133).
- **P2's response window:** the RTT allowance is capped near 0.35 ms (Δ + RTT ≤ about 0.85 ms), and w stays 16,448.
- **The PoUW timed reruns are approved:** twice at current main and once after PoUW's Python move, #1116's window
  (all 8 GPUs of node 2 for 30 min each) and the K = 14,336 accept set (about $160 each on node 1).
- **The defaults stand:** proofs owns core's lock; an area's Python move is done only when its vectors are generated
  from its executable spec; a lock reduction is reviewed once per package; the landed `train-prep-*` branches whose tip
  is on main are pruned, keeping `cursor/pouw-hash-sm120-9569`.

And at 3:30 to 4:06 PM PDT:

- **The hardware-semantics area is `silicon`,** not `fp`.
- **Python import names follow the directories** (see Conventions).
- **A claim about a computation is verified only by a proof:** sampled proofs over C-Flock, zero-knowledge. No protocol
  verdict comes from the verifier recomputing the work. PoUS and the warden check physical facts (timed responses,
  timing), not computations, and keep their checks.
- **A replay is a diagnostic,** a tool that recomputes opened values in the clear and compares. It certifies nothing,
  and nothing cites its ACCEPT as a verdict. It lives beside what it diagnoses: vLLM's `check/replay/` stays in the
  integration, PoUW's device-run replay goes to `benchmarks/pouw/`. A replay may read a protocol's formats, since
  dependencies point inward, but it is never in `verity/`. `research replay`, which re-runs recorded results as
  evidence, is unrelated and stays in `tools/research/`.
  - Consequences for PoUW (compute-accounting, at `5049de02f`): every scheme in `schemes.SCHEMES` is verified today by
    `audit.Verifier.check_tile`, which recomputes the tile in the clear. Only `ncp-v2` and `ncp-v2-shift24` run under
    sampled proofs, so `verity/`'s registry is ncp-v2 alone until Pearl-C's tile check (`pc8`, with `rowk`, `leaves`,
    `boolean`, Pearl-C's half of `words` and TurboSHAKE128, all now on that path and not experimental) passes under
    sampled proofs. Until then, Pearl-C's served verdict and the exhaustion audit are diagnostics, and ncp-v1 and
    `pearl-c-sm120-v1-h2` sit beside their replay, in `benchmarks/pouw/`. The γ statements carry over. The bridge from "the proof accepted" to
    "the tile predicate holds" is new: the circuit's relation equals `TileGood` (the L3 tile-check slices), plus sampled
    proofs' soundness as a named assumption. It is a new or restated guarantee and needs Daniel's statement review. The
    served-overhead tables measure the kernel without proving, so the full overhead adds proving and ZK for the sampled
    tiles (hidden-zk's K = 14,336 sets).
  - In vLLM's `check/` (proofs, at `5049de02f`): the commitment and opening checks verify reads against `vllm-v1`, the
    record the replay reads, not the `frame-v3-sha512` roots sampled proofs registers, so they stay with the replay in
    `integrations/vllm`. The linkage from a run's public ends to its roots (`boundary_linkage`,
    `prescribed_input_linkage`, `link_to_commit_account`) recomputes nothing and is what an accepted sampled proof
    lacks to show the committed units are what was served; it moves to `verity_sampled_proofs.one_stage`, restated over
    the registered roots, with vLLM supplying the positions (proofs writes the rule after the move maps). The 12 codes
    stay in the integration as `check/`'s report vocabulary; sampled proofs keeps its own `Verdict` codes. If the
    re-baseline doesn't make `vllm-v1` the record, `verity/commitments/vllm_v1` follows the replay out (circuits).

And at 4:19 PM PDT:

- **Only the prover's zero-knowledge layer is trusted; every kernel lives outside `verity/`.** Trust means soundness
  for the auditor and zero knowledge for the developer. Completeness is out: its failures are loud, since a wrong
  kernel makes verification fail and the prover can run the verifier on its own proof.
  - The ZK layer is what a masked C-Flock session needs from the prover: coins and salts from the OS, the pads and
    adding them, the hiding (`hm96`) commitments, the padded encoding of committed rows, which columns open, and the
    coin commitment at Hello. It owns the wire: every byte a session sends is masked, committed or public, checked as
    it is sent (today `zkaudit` checks this after the fact). And it checks before it speaks: no message goes out whose
    own check fails. The first gap is `zk_veil::prove_inner`, which sends `Y` without checking the batched constraint
    (`let (c, _t) = batch(...)`), so a wrong kernel would show the verifier one witness-dependent field element.
  - Everything else is untrusted and goes to the top-level `kernels/`: the witness kernels (GEMM, attention, PoUW
    mining) and the prover's arithmetic (zerocheck, lincheck, Ligerito's folding, most of C-Flock's CUDA prover), whose
    wrong outputs stay hidden under the pads.
  - Open edge: the padded encoding and the leaf hashing are heavy kernels whose wrong output can leak. They stay in the
    layer unless proofs finds a check the prover runs before opening (recomputing each opened column on the CPU, say).
    proofs draws the line in C-Flock's code.
  - The non-recursive system stays in `verity/` and nothing moves to `experimental/` (Daniel, 4:25 PM PDT, with the
    silicon models to `catalog/silicon/`). The private-circuit line being built isn't recursive: protocol 2 (the universal unit, hidden Merkle
    reads) and route P (hidden wiring over a public gate table) are one masked session each. Recursion
    (`flock/recursion`) is paused for Daniel's call, with its code on PRs #97 and #1081, not on main; its outer proof
    would be the same masked session. The split above needs no recursion.

## The principles

1. **`verity/` is the trusted computing base (TCB):** protocol code for every role, the verifier and the prover's
   zero-knowledge layer, in both reference and fast form. It's *trusted*, not certified trustworthy: if it's wrong,
   security degrades, whether that's soundness for the auditor or zero knowledge for the developer. Completeness isn't
   a trust property: its failures are loud, and kernels live outside (the 4:19 PM ruling). `verity/` holds what the guarantees
   depend on and nothing else: if its code implements its spec, then wherever a guarantee's assumptions hold, its
   conclusion holds of the running system. How strong a guarantee is comes from its assumptions, not from which part
   of `verity/` it uses. One that rests on a kernel takes device assumptions (the GPU's arithmetic matches the captured
   model, its cost is what was measured), which are weaker than SHA-512's collision resistance (`cr/sha-512`). Each
   result lists them (principle 10). Code outside `verity/` is either untrusted or the workload being verified, and a
   wrong workload makes verification fail.
   - A second, *assurance* TCB says why we believe "G is proved" and "this commit passed". It is an owned list, not a
     directory:
     - Lean's kernel and toolchain, and the pinned Mathlib and ArkLib;
     - the validator (`tools/lean/`'s `audit.py`, `Facts.lean`, `Replay.lean`, `Upstream.lean`, `sandbox.sh`,
       `setup.sh`);
     - check's gates and what `merge_requires` reads, which should run from main's copy, never the PR's (today they
       run from the commit under check; ci's work);
     - upstream's Rust verifier, through lean-agreement;
     - the validating nodes, with their `git/verity.git` source refs, which nothing may prune.
2. **Specs are minimal and sit beside their code; everything else lives apart.** A spec is a package's trusted text,
   its Lean `Protocol`, `Assumptions` and `Guarantees`, kept as concise as possible, since every line of it is TCB. The
   only Lean in `verity/` is specs plus C-Flock's executable verifier, which is TCB code written in Lean and whose spec
   is its soundness guarantee. Every lemma and as much machinery as possible live in `security_proofs/` (untrusted,
   machine-checked). That includes PoUW's ~41 lemma statements now in `Protocol`, while its generated vectors go to the
   catalog. A guarantee is a `def G : Prop` in `Guarantees`, readable without the proof's own definitions.
   - The lock (`lean-audit.json`) protects as little as possible: the guarantees and the spec definitions they read.
     Everything in `security_proofs/` is free to change, as long as each guarantee still validates with the same
     statement.
   - A Lean PR is either a *move*, which leaves the lock's remaining entries byte-identical, or a *change of meaning*,
     which the DM shows in full. Never both. Declaration names are kept, and proof modules move under a root of their own
     (`CoreProofs.*`, `PouwProofs.*`), since Lean loads a module from the first package with a directory for its root
     component (lean, verity#1144). The umbrella module (`Verity`, `Pouw`) stays with the spec. A pure split leaves the
     `guarantees` and `reads` records byte-identical; `roots` and `proved_in` may change.
   - Lake packages split only where their `require`s differ. The proofs can become one package, since everything
     already shares one Mathlib and only `CheckAxioms` collides (the validator replaces it). The rest are C-Flock's
     executable verifier (no dependencies), the specs, and the catalog.
3. **Public parameters are data, not code.** `catalog/` holds digest-addressed entries, each with the named assumption
   it rests on. Entries cover:
   - hardware models: the tensor-core step, FP32 and the FP formats;
   - circuit Definitions and cost models;
   - device numbers: PoUS's Keccak step and RTT allowance, HBM bandwidth, erase timing;
   - calibrated parameters, such as the warden's r, B, τ and Σ_sync;
   - generated vectors and the census.

   The verifier's side chooses entries, and every result records which ones it used. The code that *builds* an entry
   (calibration, capture) is a tool, not TCB.

   A Definition is the exception, per circuits. It is a Python builder generic over statics, and what's
   digest-addressed is its canonical descriptor at given statics. Circuits' proposed entry: `id@version`, whether it
   is current or superseded, its reference evaluator, its Boolean-version link, its pins, and the canonical descriptor
   digest at each statics a kept Program or record uses. The builder stays the source and lives in `catalog/`, and a
   test regenerates the digests and compares them, like the format vectors. In circuits' area:
   - *catalog:* the word Definitions and their Boolean versions, the device dots (`HopperBF16WgmmaDot16`,
     `BlackwellE4m3QmmaDot32`, …), the FP formats, `pins.json` and each target's representative statics;
   - *TCB primitives:* the Boolean basis, the lowering and the evaluator, and SHA-512 and Merkle as gates;
   - *integration:* the frontend rules and vocabulary (which Definition each serving role binds), capture, capture
     maps, the κ profiles, the fold and Match.

   At `be2452acd` vLLM's registry has 59 modules, and 53 import nothing outside the registry, `verity` and numpy at
   module level (the AST scan is the record; circuits, 4 Oct). So "catalog imports only verity" is mostly a matter of
   separating each Definition's content from its twin and from the vocabulary, not of cutting imports.
   Definition ids and descriptor digests are name-keyed, so no move changes them. Every vLLM Definition's link to a Lean
   model is named, not proved, and is labelled so.
4. **Circuits are the core primitive:** the format, its digests, evaluation, compressed structure, and queries over it
   (partitions, cuts, units), generic over a basis of leaf operations. Work is `work(circuit, cost_model)`. Lean has one
   circuit model and one game model, both core's, and every protocol uses them.
5. **Fast code earns trust from a reference.** Every kernel is untrusted and bit-exact with a reference in `verity/` or
   the catalog, and fast provers take their coins from `verity.randomness`. Deleting every kernel changes only speed. The registry, keyed by op and
   device, has one entry per kernel, and an entry may be a whole Rust+CUDA crate with patches. Each entry records:
   - its reference, and the test that shows it's bit-exact (CI reads this);
   - its build key: source hash, architecture and the pinned toolkit;
   - for a binary a result rests on: the SASS/FTZ gate on every cache fill, and the binary's hash in the result;
   - a per-device timing record, marked as an *honest* kernel's time and never read as an attacker's bound;
   - whether its catalog Definition's link to the Lean model is proved or named.

   Kernels compile on first use into a per-node cache. The build runs sandboxed and unprivileged, and a gate passes
   before the cache publishes. Nothing compiles on a leased timed GPU, and CI builds every kernel before any traced step.
   vLLM's `program/kernels/` already has this shape (`_jit.py`, `kernel_registry.py`, and C++/CUDA twins of vLLM's
   attention, GEMM, RMS norm and sampling kernels, each checked word for word against its Definition by a row test,
   on sm_80, sm_89, sm_90 and sm_120), so there the registry is mostly a rename (circuits).
   Torch is a container only: trusted code never uses its math. Where a gap between theory and practice remains (a
   prover without a reference, torch math on a prover path), the result states it until a lane closes it.
6. **Dependencies point inward.** `verity` imports nothing else in the repo; `catalog` imports only `verity`; everything
   else imports both. Lean enforces this through `require`s, Python through a boundary test.
7. **Integrations are adapters.** vLLM, torch and JAX lower a model, capture what the protocol asks for, and hand it to
   `verity`'s prover. They never talk to the verifier, and they import kernels from `kernels/`, never from
   `benchmarks/`.
8. **Nothing is lost.** Cleanup consolidates; it doesn't delete results. Math results, constructions and kernels go case
   by case, and the default is consolidation. Superseded infrastructure is simply deleted. Four things ensure it:
   - Every theorem keeps building in `security_proofs/`, and the validator keeps checking that it is proved. Only
     guarantees' statements are locked. A lemma someone relies on is cited from its approach in the registry, with the
     commit that proved it.
   - Every empirical result a table, ledger, approach or note cites belongs to its area's *replay set*, in two tiers.
     - *Re-verify*: the preserved records are checked again at the new commit, and verdicts and certified numbers must
       match bit for bit. This is CPU-only and cheap, and runs after every move.
     - *Re-run*: the timed results *our code* produces are run again, twice at current main now (to measure their
       noise band, since most ran once) and once after the area's Python move. A measurement of someone else's system
       is an input: it is preserved as an artifact and re-verified through its CPU part, never re-recorded. For
       example, the warden's 88 GPU-h of vLLM serving traces measure vLLM, so the replay re-runs convert, calibrate and
       audit on the preserved traces (network-accounting).

     A kernel that reproduces its numbers has survived. A replay's label says what the timing measures; an honest
     kernel's time is never an attacker's bound. Where the verifier of record now refuses an old form, re-verifying
     expects "refused: <form>" at current main and the recorded ACCEPT at the run's own commit; the re-run regenerates
     the statement in the current format and proves it again. The same holds where fail-closed refuses a session kind
     until a guarantee covers it: since Daniel's 8:42 AM PDT ruling, `flock-verify` refuses PoUW's registered and anchor
     sessions until proofs' V3. Such runs are labelled `blocked: V3` with the ruling's ref, and a refusal there is an
     expected change, not a failed replay (compute-accounting). The Lean's replay is built in: the lock stays
     byte-identical, every package validates, and check's Lean wall time stays within noise.
   - Every dead end stays findable with why it failed: it is an *approach* in the notes' registry (`kb/onboarding.md`
     §3), killed or superseded, with its reason and evidence (`research notes approach <c>/<slug> killed --reason …
     --cite …`, rendered into `campaigns/<c>/APPROACHES.md`). Each area registers what it has tried and not yet
     recorded: C-Flock's formats, scopes and proof routes, PoUS's rejected redesigns, PoUW's forming v0, route U and
     H100 v0, and the warden's egress option (d) and egress chain rule. An approach's evidence must resolve from any
     VM: an art id, note id, run id, PR or repo path. A `store:` path into an agent store doesn't: P2's frozen spec,
     verdicts and cryptanalysis lived only in old accounting's agent store, and memory-accounting re-derived P2 without
     knowing it existed. Such a file is copied into the notes or the evidence store and cited by its note or art id. The PoUW and PoUS registries cite 44 files in the `pous` agent store 129 times; once they're relayed, the registry's evidence pattern (`research.approaches.EVIDENCE_RE`) drops `store:`, and `approaches check` enforces the rule. A `DESIGN.md` that holds
     an area's reasoning, like C-Flock soundness's, stays where it is.

   **Consolidation adds, bridges and supersedes; it never ports.** A new shared definition goes in beside the old one.
   A bridge relates them: in Lean a theorem (`old = new`, or a refinement where they differ), and in Python bit-exact
   vectors. Guarantees move onto the new definition, each move shown by its DM. The old definition, and everything that
   reads only it, keeps building, and its approach is marked superseded.

   A killed or superseded approach's code stays in `experimental/` while it still runs and teaches something. It goes
   to `archive/` when keeping it working costs more than it teaches, for example when every toolchain bump breaks it,
   with its record and its last-good commit, and nothing imports it. Superseded tooling and merged branches simply go:
   they hold no results.
9. **Code's status is its directory; an approach's status is the registry's.** Code that a guarantee depends on is
   in `verity/` (with its parameters in `catalog/`); code under development or kept for study is in `experimental/`,
   which may import `verity` while nothing in `verity/` imports it (a boundary test in Python, no `require` in Lean).
   The boundary fails closed: no forgotten label can put experimental code under a guarantee.
   - *Promotion* into `verity/` is an ordinary PR, reviewed by the area's owner. It brings what `verity/` requires:
     the spec and its guarantees' lock entries (with `owner`, and Daniel's DM), the reference and vectors, and for a
     kernel its registry entry with the SASS gate and binary hash. Experimental work pays none of that until it's
     promoted.
   - *Unfinished work on code already in `verity/`* (C-Flock's V2 and V3, registered reads) lands only behind a
     fail-closed refusal, so nothing reaches an accept through code no guarantee covers. C-Flock's verifier already
     works this way: its refusal list has one refusal per superseded or unfinished form.
   - *In Lean* the boundary is a reads check, which @lean adds beside the `layers` rule (that rule checks imports
     only, so a theorem pinned inline in `security_proofs/` could otherwise read a definition in the math): every
     definition a guarantee's statement reads lies in a spec module, core's spec, or a pinned dependency (Mathlib,
     ArkLib). C-Flock is the exception until its spec is extracted. On `main` it fails nothing else. The check is on the
     statement's reads (the lock's reads are exactly those), not the proof's: a guarantee whose proof uses a lemma from
     a superseded approach is still proved. The lock holds only guarantees, each with an `owner`, and a change to one
     DMs Daniel and that owner. No `Status:` header is needed.
   - Experimental Lean, specs included, sits in `security_proofs/` under the proofs' own module root, unlocked, with no
     package of its own. Promotion moves those modules into `verity/`'s spec package under the spec's root, with their
     declaration names kept, plus their lock entries. To keep `verity/` minimal, the validator *reports* (doesn't fail)
     any spec definition no guarantee reads, as a candidate to move out.
   - *What fails is often a reading, not the code.* Band and dense's theorems stay guarantees in the ideal model, while
     the approach that read them as deadlines secure on hardware is killed (art:7617c801, #1122). A Definition version
     in `catalog/` is current or superseded: kept only so old records replay, never bound by a new Program.
     `test_conformance_record` already tracks this.
   - C-Flock's superseded forms' parsing code is in the verifier's source today, unreachable for an accept, because
     their proofs read it. As part of C-Flock's move, each form's parser goes as a frozen copy into
     `security_proofs/flock/` beside its proofs, unlocked, and the verifier of record shrinks.
10. **Each result states its trust:** the assumptions its guarantees take (cryptography, each device's measured
    arithmetic and cost, each Definition↔model link that is named rather than proved) and the digests it read.

## Conventions

- **Tests stay beside their package,** as one input-cached suite each. Test-only code in packages moves into tests
  (PoUS's oracle, adversary and broken attack modes). The repository's own `tests/` keeps only whole-tree invariants.
- **Python packaging:** one uv workspace with one `uv.lock`. **Import names follow the directories** (Daniel, 4 Oct):
  `verity/primitives/silicon/` is `verity.primitives.silicon`. No digest, Definition id or Lean guarantee pin contains a
  module path (the move inventory), so a rename costs edits and one cold `check`, which the directory move pays anyway.
  - The move script carries a module map beside the path map. It rewrites imports, `import_module` strings,
    `module:attr` specs and module-keyed test data, and lanes run it on their own branches after a restack.
  - Before the first rename, the two guards that fail open on an unknown name fail closed (`suites.py`'s `foreign()`,
    circuit-check's `_authored`), and a whole-tree test checks that every dotted module string in tracked code and
    data resolves, history fields aside. That test is what makes the next rename safe.
  - Lean comments that name Python modules are rewritten in a later Lean PR, so a Python move doesn't rerun the Lean
    audit. Old data that resolves modules at run time (the vLLM quarantine's `verity_ir.*` adapters, node scripts
    that run old and new trees) gets an alias table.
  - The recurring `-m` runs become declared tools, whose derivation is keyed by tool name and version, not by module
    path. The 111 ad hoc ones fork, and their old records stay valid.
  - **Core is one regular package** (captain, 5 Oct 00:40Z, from the layout probe,
    `internal/layout-import-probe-report.md`, branch `cursor/layout-import-probe-c3b2`): `verity/` has an
    `__init__.py` in every directory, the repo root's `pyproject.toml` is the one `verity` distribution, it installs
    editable in hatch's exact mode, and each directory under `verity/` is its own suite through a tests-only
    `pyproject.toml`. Per-member hatch `sources` can't install editable, since hatchling and uv refuse a prefix
    rewrite, and their workaround puts the repo root on every `sys.path`. `suites.py` needs about 15 lines: count the root
    distribution as a member, key dependents on `verity/` and not `.`, and run pytest and `foreign()` with `-P`.
  - **Outside `verity/`, a top-level directory is a grouping, not an import name.** Each distribution under it is a
    directory with a distinct name of its own, as `integrations/vllm/verity_vllm/` is today: `catalog/verity_catalog/`,
    `kernels/verity_kernels/`, `experimental/verity_experimental/`, and tools keep theirs (`research`,
    `circuit_check`). `kernels` is Hugging Face's package, which transformers imports, and `experimental`, `infra`,
    `benchmarks`, `examples`, `tools`, `integrations` and `archive` are all PyPI names. Nothing on a pod puts the
    repo root on `PYTHONPATH`.
  - `tools/` holds one distribution per tool, each its own suite and cache key, so that a change to one tool reruns
    only its tests (ci). `research` stays its own distribution because the nodes pin it separately.
- **Silicon semantics**, how the hardware computes each low-level op bit for bit (the tensor-core step, FP and integer
  arithmetic, MUFU, PTX max and min), is public data: the models, their Lean, the formats, the device instances and
  their gadgets all go to `catalog/silicon/` (Daniel, 4:25 PM PDT). A circuit is claim content, pinned by digest, so
  no guarantee that a computation was verified reads a model; `verity/` keeps only the circuit machinery. A guarantee
  that prices an attacker on a device does read one: PoUW's certified γ reads `Sm120`'s E4M3 semantics and
  `Prices.sm120Loop`, so its lock entry reads `catalog/silicon/` Lean by definition hash, under lean's catalog-read
  allowance (Slack `1791153016.351199`; compute-accounting). Their Boolean circuits are Definitions in
  `catalog/`, which circuit-check ties to the models on edge and random vectors; no Lean proof ties them yet. The
  exception is a builder the verifier runs at verification time (PoUW's `ncp2`), which stays in `verity/`.
- **Kernels of catalog Definitions** register by Definition id from `kernels/`, so `verity/` imports no catalog
  module. A kernel's self-check against its Definition runs in the catalog's suite. `verity/`'s own tests import no
  catalog module either, so a catalog change never reruns core's suite (ci, 4 Oct). The core tests that use real
  entries today (seven in `ir`, three in `evaluation`, and `test_profile`) switch to toy registrations or move to
  the catalog's suite; circuits decides which.
- **`PROTOCOL.md` retires.** Definitions go to the Lean spec, parameters to the catalog, and where two implementations
  must agree, a vectors file is the spec. A short README keeps the threat model, the lifecycle and the open assumptions,
  and the area's approaches keep its history. Two sections stay until Lean states them: the warden's wire format and
  C-Flock's §16.15. C-Flock's deviation list becomes data that `agree.py` reads.
- **The ownership map is data:** path prefixes per handle in `registry.json`, built by @comms (#1124). The queue and
  router use it to send review and restack asks to owners.
- **Node configuration is data.** The systemd units and cpusets go to `infra/`. `deploy.toml`, `weights.tsv`,
  `monitoring/lanes.tsv` and `store.pod.toml` stay in `tools/research/src/research/`, because the nodes' tool snapshot
  carries only that tree (infra, 4 Oct).

## Layout

~~~text
verity/            TCB, with each spec beside its code: only what a guarantee depends on
  primitives/      circuits, randomness, commitments (one Merkle tree, one SHA-512 row hash), crypto (drand BLS),
                   physical (one timed challenge-response)
  protocols/       verification (C-Flock: its Lean verifier, its reference prover and the prover's ZK layer),
                   accounting (work/pouw, space/pous, communication/warden with its active enforcer),
                   compliance/nci, the onsite protocol and the remote protocol
kernels/           registered fast code by op and device (untrusted), e.g. Pearl-C on sm_120, C-Flock's CUDA prover
                   outside its ZK layer
catalog/           silicon/ (the hardware's low-level ops: models and their Lean, FP formats, device instances,
                   gadgets), Definitions, cost models, device numbers, calibrated parameters, generated vectors,
                   census
security_proofs/   every lemma and Lean proof, and as much machinery as possible (untrusted), experimental and
                   superseded ones included
experimental/      constructions, schemes, kernels and Definitions under development or kept for study, by area
                   (untrusted; imports verity, never imported by it), e.g. the H100 kernels, NVFP4, P2 and P3
integrations/      vllm/ (adapters only)
tools/             research, check, lean (the validator), circuit_check, cluster, catalog builders, PoUS's grader
infra/             node configuration (data)
benchmarks/  examples/  archive/ (frozen backends, and code of killed or superseded approaches that no longer builds,
                                  each with its record)
~~~

The H100 lane is a device lane, not a dead end. Its Pearl-C kernel lives in `experimental/` until a guarantee rests on
it, then is promoted as the sm_90 entry beside sm_120's; its 45 γ theorems and CPU twins keep building, as lemmas.
compute-accounting's split:
- in `verity/`: `pearl-c-sm120-v1` (and `-h2`), and `ncp-v1`/`-shift24`;
- in `experimental/`, live approaches: the H100 `-v1`, `-h1` and `-h2`, `pearl-c-nvfp4-v0` and `pearl-fp8-v4`;
- superseded: `pearl-c-h100-v0`.

The sm_90 entry needs a catalog device entry (Hopper wgmma FP8, from core's hopper vectors, with its FTZ pins as the
device assumption), `pearl_c_u` as its twin, and an ahead-of-time build with nvcc 12.9.1 and the FTZ gate. Neither node
has an H100, so re-running its timed results needs a rented H100 pod: a spend ask to Daniel when we get there.

## Still open

- **PoUS's primitive** is still Daniel's choice. Under "nothing is lost", nothing is deleted whichever he picks. P2
  keeps both expanders: the spec-conforming SHAKE256 `p2-16448/v3`, and the ChaCha8 `v2`, labelled nonconforming but
  kept as an efficient algorithm (about 1% key cost against SHAKE256's estimated 12%).
- **The P2 response window and w:** ruled at 2:21 PM PDT (cap the RTT allowance near 0.35 ms, keep w). The reason: old
  accounting found (2:03 PM PDT, thread `1791138312.751569`) that the frozen spec's "2× margin through Δ + RTT ≈ 1.9 ms"
  holds only against a Zen 4-derived floor of 13.2 ms per root that nothing in the store derives. Against the timing
  document's Zen 5 floor (5.97 ms per root, the one `ROOT_CALL_NS` encodes) and the measured 3.5× eight-core cooperation,
  the 2× margin holds up to Δ + RTT ≈ 0.85 ms. That covers the measured on-node 0.52 ms (about 3.3×) but not the frozen
  allowance of 1.5 ms (about 1.14×). The choice is to cap the RTT allowance near 0.35 ms, or to widen w (the width not
  computed yet; at about 26.6–36.5 kbit P2 loses to P3-ARX).
- **For @architecture to answer in the wrap-up:** circuits' catalog entry format (principle 3), and a yes on
  C-Flock's three-package shape (with @lean).
## The plan

1. **Prep, with no moves:**
   - ci's check-time fixes (#1079, #1117/#1119, #1118, circuits' per-target cache, due 2:30 PM PDT), then pass
     caches keyed by content alone, so moves don't make checks cold;
   - @lean: the validator change, piloted on core's package. It waits only on ci's tip `afacde975` landing (#1059,
     #1079, #1085), since #1085 moves the code it changes. It adds:
     - validating a `security_proofs/<area>` package against its spec's lock in the other package;
     - the reads check: a guarantee's statement reads only spec modules, core's spec and pinned dependencies (no
       `Status:` header since 1:30 PM PDT), plus a report of spec definitions no guarantee reads. PoUW's
       `Pouw.SecurityProofs.Dimension.Lifting` moves into the spec package at the split, name kept;
     - an `owner` field on every entry;
     - *lift certification:* `theorem X : <expr>` becoming `theorem X : Guarantees.X` changes the entry's signature
       and type hash, and today's `--moved` only certifies renames. The validator certifies a lift as a move when the
       new constant, unfolded once, hashes to the old entry's type hash. Without it, each lift would be a full-change
       DM.

     Then lean splits core as the first move, showing the lock stays byte-identical across it, and measures the
     pilot's validation time before and after (the split adds five Lake packages);
   - a lock reduction is reviewed once per package, not once per dropped record. Today each changed record DMs Daniel,
     and the reductions remove hundreds (PoUW alone 788). The DM batching of #1053 (@lean or @infra) lands first
     (the lander);
   - each owner reduces their lock to the guarantees (a removal changes no remaining entry), and lifts each guarantee
     pinned inline into `Guarantees` (mostly PoUW's). Before any entry leaves, @lean confirms that no remaining
     guarantee's statement reads a definition that only a dropped entry pinned. Where the validator can't yet derive
     "read by a guarantee", the owner keeps the reads list by hand (compute-accounting). What owners proposed in round 2:
     - *the warden:* about 10 of 51 stay, the egress and ingress bounds that the K charge and the bit bounds read
       (`EncardAccSeqsLeConstantRate` and its per-window form, `EncardDecodableLeConstantRate` and its per-window form,
       `EncardAccSeqsLeSync`, `EncardAccSeqsLeFixedClock`, and the four `EncardIngressObsDecodableLe` forms). The 25
       lemma-level entries leave, and the 16 non-vacuity witnesses stay as checked tests in `security_proofs/`;
     - *PoUW:* superseded by #1156 (lean-checked): the 151 pins that code, a ledger or a rendered table reads stay, and
       649 leave; under the 2:03 PM ruling each reader makes its pin a guarantee. The round-2 proposal was that 5 of 793 stay: `EndToEnd`, `WorkWeightedSampling` (the draw law `audit.py` implements), #1116's
       certified γ `pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_8192` (read by `pearl_c_device.py`), and the vLLM NCP
       option's `Theorem1` and `GammaFromTTNCP_U_v1`. Leaving the lock but still building: about 25 NCP and Barrier
       lemmas that `PROTOCOL.md` and `ncp.py` name, the γ variants `test_ledger.py` checks, the 104 in
       `harness/price_twins.json` (an internal pricing table), the 45 H100 γ pins and Pearl-C4's FP4 pins (both
       experimental), and the Dimension, TileBound and Fp8Atom families. Tonight's L3 pins enter as reads of
       `EndToEnd`'s tile check, not as entries;
     - *core and NCI:* nothing outside Lean names any of core's 29 or NCI's 8, so strict citation drops both to zero.
       @lean would keep each package's point instead: core's per-device step relations (`AmpereStep*`,
       `HopperStep*`, `AdaEqAmpere`) and `Compose`/`ComposeCone` (11 entries), and NCI's `Inference` and `Training`.
       A theorem another package's math uses (core's `ProbBatchInduced` in PoUW, `ContainsImplements` in NCI) is a
       lemma: it moves to `security_proofs/` with no entry;
     - *C-Flock* (proofs; 864 today: verifier 25, level3 56, soundness 783): about 9 stay. They are
       `flock_verify_sound` and what it reads (the executable verifier among them, TCB anyway), the named assumptions it
       takes (the unit draw's uniform bytes, the hm96 hash-derived key, record custody, SHA-512's collision resistance
       where its bounds read it), and the few audit-law bounds sampled proofs cites (`Audit.Work.work_escape_le`,
       `Audit.Partition.audit_exfiltration`, the stratified-miss and influence bounds). compute-accounting names its own
       in `Audit.Partitioning.Guarantees`. Leaving (about 855): every superseded headline (`zk_session_sound*`,
       `flock_headline_exec*`, `table_sound*`, the per-scope and canonical families), all of level3's 56 and all of the
       verifier's 25, including #1120's `Registered.check_ok` (a live approach). Each superseded headline is a superseded
       approach in the registry, with the commit that proved it. The reduction is one proofs PR right after canonical V1, in the tip after it;
       open proofs branches that touch the lock rerun `audit.py --update` after a rebase;
     - *PoUS* (memory-accounting; 104 today): it would keep about 73, counting anything `PROTOCOL.md`, a claim or a PR
       names. That includes the theorems a certificate enforces (`BandMultiMeetsFamily` and its D2, D1 and D0 forms,
       `ChainDenseMeets64`, and `P2SlackFamilyUncond` after #1123); band, dense and P3 (`BandChainMeets64*`,
       `BandMultiMeets14*`, `BandPubMeets*`, `P3Concrete*`, `SegTag*`); the six P2 pins; and the audit results
       (`ContinuousAudit`, `ContinuousComplete`, `BackgroundRebuildExcluded`, the sampled and stacked audit theorems).
       About 31 would leave, mostly tightness counterexamples (`not_meets_*`, `raw_b19_*`, `family_k85_fails`,
       `junk_*`) and helpers. `SecureErasureMeets*` stays pinned while #1096 is open. The exact list comes as
       memory-accounting's lock-reduction PR, after the ruling on which pins are guarantees;
     - ci, comms, the lander and circuits own no entries. Circuits notes that core's pins (tc-step soundness,
       completeness and iff for Ampere and Ada, unit soundness, `Compose`) are what the hardware-model catalog entries
       rest on, and leaves which are guarantees to proofs and compute;
   - @comms: the ownership map (`owns` globs per handle in `registry.json`, and `research msg owners PATH…`). A test
     checks only that every glob matches a tracked file, with no gate on unowned paths. Drafted from git history, each
     lead corrects their own, PR today or tomorrow;
   - the kernel registry's entry format.
2. **Each area labels its replay set, re-verifies it at current main, and re-runs its timed results twice there.**
   This finds what has already rotted, and gives each timing a noise band, before anything moves. Each area also registers
   what it has tried as approaches, with each dead end killed or superseded and its reason; PoUS's, and C-Flock's
   formats, scopes and proof routes, are under way. Labelling waits on @infra's replay-membership label key.

   *The replay mechanism* (@infra). Selecting and comparing exist: `research data select --label k=v` picks the set,
   `data snapshot --select …` freezes it as an art id, a derivation id (`research data show drv:…`) lists every attempt
   of the same computation at any commit, and `research compare A B` diffs two runs. Relaunching an attempt at a new
   commit doesn't exist yet. infra builds `research replay SET --at REV [--on M]`: it relaunches each attempt from its
   record with the source swapped, and reports a run with secrets, `--send` inputs not in the store, or a machine
   that's gone as *not replayable*, never guessed. Each attempt gets a verdict: named outputs equal by art id (content
   hashes, so bit for bit for free), run files compared per file minus the runner's logs, and metrics against a noise
   band from at least two originals. The verdict is a `replay` label on the original with the new run as its ref, plus a
   summary for the set. `compare` learns to read attempts from the store. The re-verify tier is the same command: a
   replay of a verifier tool whose inputs are the original's outputs. GPU-timed reruns still go through the node queues
   and booked windows. One module in `tools/research`, nothing on the nodes; a dry run first classifies each area's set
   as replayable or not, so gaps show before anything reruns. infra builds it after tonight's quick tiers.

   What owners proposed:
   - *the warden* (network-accounting; lane J registers the approaches and re-runs): pass 3 calibration
     (art:9c9c5f93, on traces art:a0d64641 and art:663168ff), the real audit over 5,290 windows (art:12570076), lane F's
     audit replay (art:a3c3281f), the Python↔Lean difftest (`runs.NetTimingDifftest`), the active warden's
     injected-clock and real-time runs (art:73bbd0a9, art:92d55b2d) and the per-window bounds (#994). The only timed
     result from our code is the active warden's real-time hour (1 CPU-h). Its dead ends to register include egress option
     (d), held for Daniel, and the chain rule that doesn't hold for the egress count;
   - *PoUW* (compute-accounting, tonight: the replay labels, and approaches for forming v0, route U, H100 v0 and the 60%
     window miss with its reason; the status field on `SCHEMES` is held, since experimental schemes move to
     `experimental/pouw/`). hidden-zk re-verifies on CPU #1116
     `-0c35`, the K = 14,336 runs (`-c6e3` and five from 8:44 AM PDT), cap units `-161e` and the head-link `-ccf7`.
     fp8-table re-runs #1116's window twice (all 8 GPUs of node 2 for 30 min, plus about an hour of CPU for its audit,
     in two node-2 windows booked by @infra) and #1001's served-table runs; hidden-zk re-runs the K = 14,336 set twice
     on node 1 (about $160 each). The H100 re-runs need a rented H100, asked for separately;
   - *C-Flock* (proofs): the ledger's C-Flock rows, the one-stage benchmark runs and the lean-agreement runs. A
     re-verify runs the Lean verifier at a commit on a preserved statement and proof, so an attempt that didn't preserve
     its proof bytes can only be re-run; step 2 counts them. Workloads with an output tail (`out_net` ≠ the unit net,
     e.g. `gemm-coordinate/tc-step/k64`) stay refused at main until tails enter the theorem, so they re-verify at their
     own commit only;
   - *rows* (circuits): re-verifying a Match verdict needs its capture, and captures aren't preserved (today's
     GLM-4.7-Flash capture was 234 GiB). Daniel (1:30 PM PDT): captures aren't stored, or are shrunk drastically to
     what Match reads. So row verdicts are re-run tier (a GPU recapture) unless circuits shrinks captures enough to
     keep;
   - *PoUS* (memory-accounting plus a worker; its approaches are registered now):
     band and dense audits, P2 decode and encode, and the slow-root run (r20260929-060834-0ec4), each a few CPU-h or
     GPU-h, re-run twice. The band margins (33.1×, 40.7×, 66.3×) time a whole `Π₂` call, so their replay label says
     "call time, not an attacker bound" (#1122). The HBM sweep (art:59c46dd8) went with TwoTierBandwidth, so it isn't
     re-run. Its approaches: band and dense's ideal-model theorems are guarantees; killed are the hardware reading of
     their deadlines (art:7617c801, #1122), `feistel-indifferentiability` (refuted), TwoTierBandwidth (no host RAM),
     and the rejected redesigns (one-round power maps, small-field SPNs, lattice and knapsack encodings, trapdoors,
     search-hard inverses) with old-accounting's reasons; live are P2 v3 (the candidate), P2 v2 (ChaCha8 keys,
     nonconforming) and P3 (no certificate). The frozen P2 spec goes from the old accounting store into the evidence
     store, or beside its code in `experimental/pous/`;
     `attacks/p2-redteam-timing.md` (which `ROOT_CALL_NS` and the spec's "2× through about 1.9 ms" rest on) still
     needs relaying from that store into the notes, by @old-accounting.
3. **Everything but the specs into `security_proofs/`.** This is Daniel's version (1:06 PM PDT), and @lean checked it
   against main's locks and imports. A spec is separable when its modules import nothing else of the package and every
   pin reads only them.
   1. *Split and move.*
      - Core, NCI, the warden, PoUS and PoUW all separate now. Their spec stays in place with its lock, and the math
        becomes a Lake package under `security_proofs/<area>/` that `require`s it.
      - Module names don't change, so every pin and read entry stays byte-identical and no DM fires. Only the lock's
        package-level sections (`roots`, `layers`, `dependencies`) are split between the two packages, and each umbrella
        root (`Pous.lean`, …) moves to the math package.
      - PoUW has two caveats. One spec module sits under the math's name
        (`Pouw.SecurityProofs.Dimension.Lifting`) and stays with the spec under that name. And 768 of its 793 pins
        state themselves inline in the math. The few that are guarantees are lifted into `Guarantees` in prep, and the rest move with
        the math, unlocked. PoUW's split runs after l3-tilecheck's slice 6 lands (lean's C/D/F rulings, a trusted-text
        change), and its move script is published so the `pouw-lean-*` branches and #1080 can rerun it
        (compute-accounting).
      - PoUS's split already exists in its tree: `Pous/Guarantees*` and `Pous/Assumptions*`, plus the models they
        read (`Protocol/Model`, `Accounting/Params`), are the spec, and `SecurityProofs/` holds the proofs. Moving the
        proofs updates `TRUSTED.sha256`, `CheckAxioms.lean` and the grader's registry (`Grader/Registry.lean`, which
        grades submissions against the trusted layer) in the same PR (memory-accounting).
      - C-Flock's three packages declare no spec: soundness's pins read 285 of its 561 modules. Level3 and soundness
        move whole to `security_proofs/flock/`, and their spec comes out once @proofs names the trusted subset.
        C-Flock's executable verifier is runtime code, so it stays with C-Flock (level3 and soundness `require` it by
        path) and goes into `verity/` with C-Flock's Python. Level3 and soundness move after fail-closed and canonical
        V1 land tonight, and ideally after V2 and V3. Soundness's cold validation is 45–70 min.
      - C-Flock ends as three packages: the executable verifier (no dependencies), its spec (`require`s the verifier
        and ArkLib, since its guarantee reads Mathlib and ArkLib definitions), and `security_proofs/flock/` (`require`s the
        spec). Until the spec is extracted, `flock_verify_sound` states its eight conclusions through proof-side definitions
        (`Discharge.Exec`, `Integrate`, `DecodeZL`, `HiddenExec`, `HiddenDec`), so "the guarantee plus what it reads" still
        locks much of soundness. So C-Flock's closed-form spec comes out *before* step 3.3 touches C-Flock's math,
        not after it; otherwise every refactor there fires the DM (proofs). Fail-closed's audit records tonight count
        the definitions the statement reads.
      - The sampled-proofs audit law lives inside soundness (`FlockSoundness.Audit.*`: 27 files, 120 pins,
        compute-accounting's nested bridge in `Audit.Partitioning`). It reads the executable's `Flock.Draw` and
        soundness's game and session-batch modules, so it moves with soundness under its current names. Giving it an
        area of its own, with its game folded into core's model, is a 3.3 job.
      - Before the move, @lean changes the validator so that a `security_proofs/<area>` package validates against its
        spec's lock in the other package. Core's package is the pilot, as the smallest and cleanest.

      Two path `require`s, `ci.toml`'s paths and the Lean tooling's package list change, and a test rejects the old
      directories. The Python↔Lean difftests' `runs` generate paths and lean-deps must follow each move, or the Lean
      half silently stops running (network-accounting, for ci). Later job: extract C-Flock's spec with @proofs.
   2. *Prove the specs.* The lanes now proving them (C-Flock's one theorem, PoUW's l3 slices, PoUS's P2) finish in
      their new home.
   3. *Consolidate the math inside `security_proofs/`:* one Lake package; lemmas deduplicated; one FP, game, circuit
      and commitment model on the proof side; organized by subject. It's untrusted, so it's refactored freely: every
      guarantee keeps its statement and validates, and the DM fires only if a spec changes. Merging the duplicated
      models *in specs* (two FP32 models, four game models) is a reviewed change of meaning, using the bridge rule.
      Superseded results keep their statements, and bridges keep them building.
4. **The frozen backends to `archive/`,** each with its record.
5. **The Python, one area per train,** in the order warden (after lane J's `--cpus` follow-up), NCI, PoUW, C-Flock,
   PoUS, then tools, CI and infra. PoUS goes late: P2 v3 (#1123), Daniel's window ruling, the root-floor
   recalibration and the erasure PRs (#1096, #1086) land first, since a move train among them would conflict with each
   (memory-accounting). Each area sorts its code into `verity/` and `experimental/` as it moves. Each area
   adopts the shared pieces as it moves rather than moving its own copy, most valuable first:
   - one FP semantics, in Lean and Python (core's `fp32`/`scalar`/`boolean.fp` against vLLM's `ref_prims` and
     `kernels/*_model.py`);
   - one game model, one circuit and partition model, and one commitment model;
   - one SHA-512, with the gate version bridged to commitments' by vectors;
   - one RoPE (`RoPE_v2`, `RoPEGptJ_v2/v3`, `RoPEHeadGptJ_v1`), and the MLA lane's Booleans bridged to the row
     lane's word twins once both are on main;
   - one GPU capture harness with per-kernel probes, in place of the six under `tests/properties/*_capture_gpu.py`;
   - one statement-form check, replayed from vectors;
   - one timed challenge-response;
   - infra's slot primitive, pass cache, compile cache, fetcher and timed-run tool;
   - one difftest harness.

   A move is done when its area's replay set re-verifies from the new tree, and, after its Python move, its timed results
   re-run within their band. With `PROTOCOL.md` retired, the Lean spec is the only spec the Python is tested against,
   so each twinned definition must be executable and the area's vectors generated from it (lean's "spec runner",
   its guide §5). Lean proposes that as part of the done criterion for each area's Python move, not prep. Each move PR updates the same things in the same commit: its suites' declared inputs, the
   `ci.toml`/`check.py` paths, `tests/test_lean_packages.py`, AGENTS.md and the skills.

   **No freeze, but each move is its own train.** Git's rename detection carries an open branch across a move only when
   the moved file is otherwise untouched: #1117 conflicted across #1085's move of `lean_audit.py` and was restacked
   (ci). So each move is a script that reruns on a rebased main and lands as a train of its own, after the queued tips.
   ci restacks, or asks for restacks of, whatever it breaks, within the hour. The moves interleave with ordinary tips
   and never block them. A move train holds the move and nothing else, landed straight after a fresh main (the
   lander). The lander also asks that step 3's Lean moves go as one train, so the cold re-audit is paid once; with
   content-keyed caches that cost goes away, and the Lean moves go as each is ready (core's pilot first, PoUW after
   slice 6, C-Flock after canonical V1). There are about eight Python moves plus the Lean ones, roughly a day of the pipeline at about
   one check an hour.

   **Every move would make the next check cold,** because the pass caches are keyed by input paths as well as
   contents. Soundness's cold validation alone is 45–70 min. ci keys the caches by content alone during prep, before
   step 3, so moves stay warm. ci also moves the gates to run from main's copy (new work, after the cache fixes), and
   asks @infra for a quiet window per move train and for node 1's Lean slot cap.

   `targets.py` and `pins.json` are single files every circuits PR touches, today's conflict hotspot. So circuits
   first splits circuit-check's bindings and pins per Definition module, each beside its Definition and labelled from
   the conformance record (circuits plus a worker, after the per-target cache lands), then splits each registry module
   into Definition, twin and vocabulary, one family per PR. The catalog moves only after that. A superseded Definition
   version is deleted when no kept Program or record names it, and `registry/quarantine/` (39 files in 6 subpackages) goes with the
   deleted versions' targets.

   The ownership map keys on today's paths, and each move PR updates its own globs (comms). `registry.json` stays
   where it is, because console's router copies the usergroups from it. Each move is announced with `--to` its owners
   and the changed paths.
6. **After:** C-Flock's closed-form spec as its own lane, and one PR rewriting the README's architecture section and
   Glossary (the changes below) and AGENTS.md. That PR
   closes the layout trial (#1036).

## Glossary changes

verity#1127 adds what the repo already has:
- **Spec:** a package's trusted text, its `Protocol`, `Assumptions` and `Guarantees`, kept as short as possible.
- **Lock:** `lean-audit.json`'s records of each guarantee's statement and the definitions it reads.
- **Lemma:** anything proved that isn't a guarantee.
- **TCB**, and beside it the assurance TCB.
- **Approach**, the notes' term, now cited from the README.
- **Guarantee**, in a commit of its own (Daniel, 2:03 PM PDT): a theorem a ledger row, a published table, the docs site, a
  claim id or code reading its result relies on as proved, never one only a PR names.

The rest arrive with the change that makes them true:
- **experimental** and **promotion** with `experimental/`;
- **catalog** with `catalog/`;
- **replay set**, **re-verify** and **re-run** with `research replay`;
- **proof system** (replacing "backend" and "backend family") with the README PR;
- **onsite protocol** and **remote protocol** with their code.

## Not covered

@infra answered only the replay question; its asks from others (node-2 window bookings for PoUW, quiet windows per
move train, node 1's Lean slot cap, #1053's DM batching) are in the threads above.
