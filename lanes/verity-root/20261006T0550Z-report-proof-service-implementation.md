---
id: verity-root/20261006T0550Z-report-proof-service-implementation
campaign: proof-service
lane: verity-root
kind: report
status: open
repo: danielreuter/verity
origin: top (captain), from Daniel's instruction of 5 Oct 10:45 PM PDT
---

# Implementing the proof service overnight (5–6 Oct)

Daniel's instruction (10:45 PM PDT): implement `note:verity-root/20261006T0545Z-draft-daniel-one-recursive-architecture-v2`
unless you have a very strong reason not to, and if you do, leave him a report for the morning. He wants a working
repository in the new shape when he wakes, "at a minimum", and progress on the other fronts too.

This note turns the draft into work. The order is the joint note's migration order
(`note:proofs/20261006T0307Z-draft-proof-service-architecture` §6, steps 0–14), which all three accounting leads agreed
at 8:41 PM PDT, amended where Daniel's decisions differ. Each lead owns its items, runs its own workers, and lands
through ci's trains.

## The rules for tonight

- **Implement unless there's a strong reason.** A strong reason is something like a measured cost that breaks a budget,
  a soundness or zero-knowledge hole, or a contradiction with a proved theorem. Taste isn't one. If you have one, still
  build the nearest version you can defend. Write the reason up as a note (`kind: report`, your lane, titled
  `…-report-strong-reason-<slug>`) by 7:00 AM PDT (14:00Z): what the draft says, what you measured or proved, and what you
  built instead.
- **Main stays green.** Everything lands through `research merge` trains with a passing `check`. A PR that can't land by
  7:00 AM PDT is pushed, marked ready if its tier passes, and listed in your final line.
- **Checkpoints:** one line each in the announcement thread at 11:30 PM (06:30Z: accept, or name your strong reason),
  1:00 AM (08:00Z), 4:00 AM (11:00Z) and 7:00 AM PDT (14:00Z: final status). Quiet otherwise; ask top only to unblock.
- **The other fronts keep running.** Your research lanes, GPU windows and 7:00 AM PDT results continue alongside.
- **Rulings that change what was agreed** are in the next section. Don't relitigate them tonight. If one breaks
  something, that's a strong-reason report.

## What Daniel's revision changes in the joint note

| Joint note | Now | Owner |
|---|---|---|
| D1: `-h3`'s seed keyed on the BLAKE3 row leaf (compute-accounting, 9:41 PM) | One hash: the seed keys on each row's SHA-512 digest. Measure the GPU cost first (the draft lists it as open). The 5.2× was hm96-sha512 hiding rows in the call path, not a plain SHA-512 row digest. If the measured cost breaks the served budget, write a strong-reason report and keep BLAKE3 behind a flag | compute-accounting |
| D3: the possession claim | Gone. The memory challenger hashes the received 2,056-byte block itself | memory-accounting |
| D4: where PoUS's timed verifier runs | The memory challenger, next to the certifier inside the node's isolation boundary | memory-accounting, infra |
| D5: the salt's source | Live coins only; Fiat–Shamir out. Delete the beacon and BLS code once nothing reads it | proofs, compute-accounting |
| D7: coins as ingress | Charge their timing, exempt their content (the draft lists it as settled) | network-accounting |
| D8: the firewall in Lean | (a): today's Rust under a named zero-knowledge-only assumption | proofs |
| D10: PoUS's setup | Sampled, `P2SlackFamilyFreeBlocks` | memory-accounting |
| PoUS's on-time bits as public items (memory-accounting's change) | Only the verdict is public. The per-round bits stay in the memory challenger's signed record, which is witness | memory-accounting |
| The partition is public (`verity/partition/v1`) | Private, with public predicates. Circuits asked for this decision, and this is it | circuits, lean |
| The warden's record digest: unsalted tagged SHA-256 | SHA-512, hidden: a certificate is witness, never public | network-accounting |
| Retries with fresh coins | None for now. Any failed proof is a visible failure, and a retry never redraws | proofs |
| `frame-b3`, `frame-b3s`, TurboSHAKE and BLAKE3 commitments | One hash: every commitment is hm96 rows in frame-v3-sha512 trees | proofs, with each owner |

D2 (|W| public), D6 (the audit window) and D9 (the lottery) aren't addressed in the draft. Follow the joint note's
recommendations, and list them as open in your final line.

## Work by owner

The "Step" column gives the joint note §6 step. Done means landed on main, or ready with a passing tier, by 7:00 AM PDT.

### Everyone: the names (the draft's Names table; Glossary in the same change, AGENTS.md)

One generated rename move, like the Lean move, landed in one quiet train slot at about **2:00 AM PDT (09:00Z)**. After
that slot, open PRs restack onto it with the restack tool (#1175), and new code is written in the new names. Each owner
sends top its old-to-new map by **12:30 AM PDT (07:30Z)**: module and file paths, identifiers, Lean declarations, and
guarantee names for `audit.py --update --moved`.

| Was | Now | Map owner |
|---|---|---|
| warden (`verity/protocols/accounting/communication/warden/`, Lean `Warden`), its records | network certifier, network certificates | network-accounting |
| prover gateway (`rec_live`'s gate, `FC_GATE`, `gatewayLeaf`), verifier gateway, batch verifier, GPU workers | firewall, challenger, verifier, workers | proofs |
| PoUS's timed verifier (what survives §5's deletions) | memory challenger | memory-accounting |

top runs the move: the generator, the Glossary and AGENTS.md lines, a dry-run restack of every open PR, and the train
slot with ci. A guarantee that only moves sends no spec-change DM (`--moved`).

### proofs

| Item | Step | Done means |
|---|---|---|
| P1. The service's first code: `Spec`, `Public`, `Value`, `Check`, `Outcome`; `register` enforcing the public-items rule; `select` and `outcome` over one-stage. No retries: an outcome is final and the draw is fixed once. A failure budget b stops the stream | 1 | Merged, where L12 recommends (`sampled_proofs`), with PoUW's served-zk calling it |
| P2. The firewall: #1270's six prover choices closed and the stop bound restated; the contract (fresh salt, mask-then-check, uniquely fixed) as a Lean definition, with the Rust send check tested against it the way lean-agreement tests the verifier (Lean's proposal; lean co-owns); a fixed release schedule; the failure budget; outer proofs one at a time across streams | 9 | #1270 granted and ready; the contract definition and its agreement test in a PR |
| P3. A fixed outer shape: pad V* to a cap, or add a combining step. Pick one, implement it, and measure it at K = 4096 | 9 | One outer proof of the fixed shape, Rust and Lean accept |
| P4. VBridge: the remaining 4 of 9 pieces; V*'s staging registers `coef` (#1261 gap 3); the Lean tag for `flock-leaf/sha512-unsalted` (#1284); and whether any `partial def` escape (`Flock.canon`, `Qword.evaluate`, `DCut.*`) is on the accept path, made total if it is | — | As many pieces as land; the escape answer in your 1:00 AM line |
| P5. #1261 (RecursiveSound/ZK) through red team; #1264 (the J-table repair) landed, then #1257 restacked onto it | — | #1264 on main; #1261 granted or its gaps listed |
| P6. One hash in core and C-Flock's live paths: inventory every non-SHA-512 commitment, move it or delete it (`frame-b3`/`b3s` once multiproof drops them; beacon/BLS per D5) | 4, 6 | The inventory in your note; the deletions in PRs |
| P7. Registered row/v2 and the shared tensor table (W by weight row) | 4 | In a PR with its `ZkReg` records |
| P8. The two-stage driver; hidden layout (`Check.window`, position reads) | 7, 8 | Started; whatever lands |

### compute-accounting (PoUW)

| Item | Step | Done means |
|---|---|---|
| C1. `-h3` keyed on SHA-512 row digests: a GPU SHA-512 row-digest kernel before forming, measured at b32 decode against BLAKE3. Either it lands, or a strong-reason report gives the measured cost | — | The measurement in a run; #1278 updated either way |
| C2. PoUW's draw into the service: uniform `subset:K′` over N tiles (L3), the window root registered before the draw, N padded to a public bucket with zero filler tiles, and the public-outputs list as the draft gives it | 3 | served-zk (#1282) calling P1's `register`/`select`/`outcome` |
| C3. Epoch coins as PoUW's salt, with proofs; the beacon path retired | 6 | In a PR |
| C4. §5's deletions as the service replaces each piece | 10 | Whatever the service already covers |
| C5. #1278 and #1288 (the row-seeded twin) landed; Pouw's four-name lifts with lean | — | On main or ready |

### memory-accounting (PoUS)

| Item | Step | Done means |
|---|---|---|
| M1. The memory challenger: a coin tree committed in advance, one index revealed per round, the whole 2,056-byte answer received and hashed by the challenger, and (index, send, receipt, H(block)) signed. Built on #1227's loop with µs timing and #1159's cap. The signature scheme is S1's | 5 | A timed audit through the memory challenger on node 2's timed lease, honest accepted and controls rejected |
| M2. The verdict-only public outputs: drop the per-round bits and the possession claim from the public-items list and from PoUS's PROTOCOL.md | 11.3 | In a PR |
| M3. PoUS's proofs: the traced 16,448-bit squaring through circuit-check, then `P2Decode` and `AnswerOpens` as Programs, then `P2SlackFamilyFreeBlocks` | 11 | Squaring checked; the rest as far as it gets |
| M4. The honest tail with no retries: the 200-per-cell sweep on node 2's quiet slot, and the release offset that gives ≤ 1e-5 lateness per round | — | A number, or a strong-reason report |

### network-accounting (the network certifier)

| Item | Step | Done means |
|---|---|---|
| N1. Network certificates: one signature per link-window (S1's scheme), the record digest moved to SHA-512 and kept as witness, the shaping role unchanged | 2 | In a PR, difftested against today's Python audit |
| N2. The records into the service's record (`register`; the receipt keeps only the order and the deadline bit) | 2 | Once P1 lands |
| N3. With circuits: the consistency relation between circuits and certificates (both directions of the draft's formula) as a Program spec, and a first check on a TP Build's crossing values against real certified frames | — | The spec in a note; a first check if it fits |
| N4. A declared bound on #A_c (the advice charge), and D7 in the charge | — | Stated, in the protocol's PROTOCOL.md |

### circuits

| Item | Done means |
|---|---|
| X1. Private partitions: `verity/partition/v2`, or a hidden mode of v1. The partition is advice under a hidden root, and the proof shows public predicates: each proof unit's outputs ≤ 16 bits; covering and disjointness; matmuls split into dot products rounded to BF16 after accumulation; short scalar chains; high fan-in graphs. Propose the predicate list (the draft asks for it) | The predicate list in a note; the format and Python checker in a PR; the Lean side with lean |
| X2. The coarse partition into isolation units at node or VM granularity (NCI's IU) | In the same note |
| S1. Hash-based signatures over SHA-512: pick the scheme with network-accounting and memory-accounting. One signature per link-window fits a stateful Merkle scheme (LMS/XMSS-style, Winternitz one-time keys). Build its verifier as a circuit-checked Boolean Definition on the SHA-512 gadget, and report the cost per link-window | Scheme chosen by 1:00 AM PDT; the Definition through circuit-check |
| X3. The schedule as advice: registered under a hidden root before any coin, and whether Match's dispatch-log fold can be made local | A note |
| X4. With network-accounting, N3 | — |

### lean

| Item | Done means |
|---|---|
| L1. The private-partition check in Lean (with circuits, X1) | Started, with the statement written |
| L2. The firewall's contract as a Lean definition, and its agreement harness (with proofs, P2) | In a PR |
| L3. The renames' Lean side: the guarantee maps for `--moved`, checked against the lock | Maps to top by 12:30 AM PDT |
| L4. The four-name lifts (Pouw's 14, #1288's 7), #1269, #1219, and making `partial def` escapes total where P4 needs it | Landed or ready |

### infra

| Item | Done means |
|---|---|
| I1. The firewall on its own VM with dedicated cores. Plan it and price it. If it fits an existing budget line, create it bounded (`--max-hours`). Otherwise put the price in your final line for Daniel | The plan, and the VM if it fits |
| I2. bench/placement as the deployment gate for the firewall, certifier, memory challenger and challenger | A gate that the timed runs call |
| I3. The memory challenger's placement beside the certifier on node 2's timed-lease cores (with M1) | M1's run uses it |
| I4. A short note: what makes a certifier or memory challenger auditor-trusted on a KVM guest (the confidential VMs Nebius offers, SEV-SNP or TDX, and attestation) | The note |

### ci and the lander

Keep trains running all night, in this order: #1264, #1277, #1244, #1219, #1269, #1149, then the service and firewall
PRs as they turn ready. The rename move gets its own quiet slot at about 2:00 AM PDT (09:00Z). Run a post-train after
each landing.

### console

C-1. A status page or table rendered from the store and the notes: each item above with its PR and state. Daniel reads
it at 7:00 AM PDT.

## top's own items

- The rename move (above): the maps by 12:30 AM, the generator and dry run by 1:30 AM, the slot at 2:00 AM PDT.
- Today's rulings into `.agents/skills/friction/SKILL.md`: the decisions table and the names.
- The morning report for Daniel at 7:30 AM PDT (14:30Z): what landed, every strong-reason report, what's open, and spend.

## Sequencing

This section comes from the seven consolidation notes (`note:<lead>/2026100{5,6}T…-draft-consolidation`, all but console's;
ci's arrived at 11:15 PM PDT), checked against the items above so that no two lanes move the same files at once. It was
posted at 11:20 PM PDT (thread 1791265836.679829).

1. Before the rename slot, the train adds #1268 (the warden's program package) and #1243 (one `machines.d` reader). The
   rename applies section 4 of `note:network-accounting/20261006T0625Z-draft-certifier-rename-map`.
2. Until 7:00 AM PDT, shared machinery changes only to unblock a train: `tools/lean/`, `tools/move/`, `tools/check/`,
   circuit-check's binding schema (#1163, circuits' registry loader), and the GPU nodes' lease and agent.
3. Lock reductions (#1170, #1192/#1201, #1156, Pouw's lock items) restack after the rename. A pure move sends Daniel no
   DM, but a pin removal does.
4. The warden's tree changes in this order: #1268, the rename, N1 and N2, then network-accounting's refactors after
   14:00Z.
5. X1 is `verity/partition/v2` beside v1. v1, its vectors and #1179's per-form cases don't change. L1 checks v2.
6. S1 binds core's `verity/primitives/commitments/gates/sha512.py`. PoUW's copy (`pouw/circuit/hashes.py`) is in P6's
   inventory to retire.
7. C1, #1278, #1288 and #1282 go before compute-accounting's single scheme registry and the sm120 kernel move.
8. P1's Glossary lines are written after the rename, in the new names.
9. The joint note's §5 deletions have owners now. PoUS's `protocol.Verifier` and `TimedVerifier` loops go to
   memory-accounting under M1. The warden's published commitment goes to network-accounting under N1.
10. v2 overrides these consolidation items:
    - compute-accounting's h3 deletion;
    - network-accounting's published `commitment.commit`;
    - memory-accounting's #1 and #2.

    The SHA-256 in NCP and Pearl's FP8 scheme goes into P6's inventory. Keeping it is a strong reason only if it is part
    of those external schemes' definitions.

The notes' other questions for Daniel go in his morning report.

## Checkpoint

- 5 Oct, 10:50 PM PDT (05:50Z): written and sent to all leads.
- 5 Oct, 11:20 PM PDT (06:20Z): the sequencing added, from the consolidation notes.
- 6 Oct, 12:40 AM PDT (07:40Z): sequencing points 1 and 4 changed. The last landing before the rename is the 1ad0 train
  (`935152515`: #1243 in, #1268 out; no new check finishes before the 1:30 AM PDT cutoff). The move is generated on main
  after 1ad0 and the 2:00 AM PDT slot doesn't wait for #1268, which restacks onto the move like every other PR; lean's
  items 2, 3 and 5 apply at that restack (thread 1791265836.679829, 1791272397).
- 6 Oct, 3:09 AM PDT (10:09Z): the rename move landed as main `a7134c413` (#1321, move commit `afc9d352d`, check
  r20261006-084525-c8b5); every PR restacks with `restack.py --move-commit afc9d352d --script tools/move/rename.py
  --onto origin/main`. 4:00 AM PDT (11:00Z): every lead but console reported; one strong reason so far, C1 (Pearl-C's
  `-h3` wholly on SHA-512 costs 13.5x BLAKE3's overhead, floor about 4.4x; report due 7:00 AM PDT).
- 4:05 AM PDT (11:05Z): standing ruling from the coordinator: closing a PR needs Daniel's direct approval, including any
  approval posted as top; top approves no closes. #1112 (closed 3:53 AM PDT on my word, content on main) goes to Daniel;
  my 10:35 PM PDT note that ci close #1280 is withdrawn (1791284713).
- 7:10 AM PDT (14:10Z): final. Main `b722adaad` after seven checked landings (40 PRs); every lead but console sent a
  14:00Z final (console never answered); one strong reason (C1); 14 questions for Daniel. The morning report is
  `/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/docs/morning-report-2026-10-06.md`.
- 7:51 AM PDT (14:51Z): Daniel ruled on C1: SHA-512 everywhere for now, Pearl-C's `-h3` included, performance
  requirements relaxed as needed; no hash flags or modular hashing in research mode; BLAKE3 code kept off the served
  path (default `archive/`). Accounting leads asked for implications by 16:00Z (1791298351.637869); Pearl's FP8 scheme
  goes back to him with compute-accounting's answer.
- 8:07 AM PDT (15:07Z): Daniel answered the morning report's questions (8:03 AM PDT: research velocity first; 1 cap kept, no B200; 2 graphed stock FP8; 3 later; 5 grants carry on an identical patch; 6 delete flaky tests, write how to avoid them; 8 no firewall VM; 9 Nebius trust a named assumption; 10 literal 16-bit width, placement parked; 11 UNLOWERED yes; 14 skip the ready mark; 4, 7, 13 owed context) and the SHA-512 follow-ups (Pearl FP8 semi-maintained as Pearl's; SHA-256 retires, P2 v4 and core's derive; P2 key expansion to SHA-512-CTR after a GPU measurement; LMS truncation counts, claim euf-cma/lms-sha512-n32; timed -h3 window approved). Relayed in 1791299214.453199 and 1791298351.637869.
- 8:25 AM PDT (15:25Z): Q12: the Nebius key stays 3 more days (to 9 Oct). LMS goes to n = 64 (full SHA-512). Rulings PR #1362 open (velocity first, flaky tests deleted, one hash). #1280 and #1055 closed with Daniel's approval. Today's goals posted (1791300143.885349): 9:30 AM PDT, every granted PR in a train on every full-check host plus the SHA-512 PRs open; 11:30 AM PDT, all done v2 work on main; 3:30 PM PDT, each protocol end to end through the service, SHA-512 only.
