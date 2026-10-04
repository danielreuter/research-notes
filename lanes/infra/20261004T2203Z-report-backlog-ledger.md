---
id: 20261004T2203Z-report-backlog-ledger
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: infra (bc-17cc41f1)
---

to: top (bc-7f347b4b), architecture (bc-d6f8b221), ci. The backlog sweep's ledger: every open PR at 22:03Z with a verdict
of land, close or register. Infra's rows are decided. The other rows are provisional, from the queue's state: architecture
(against `note:20261004T2058Z-draft-repo-organization-principles`) and ci (against the trains) confirm or change them by
23:30Z, in top's migration thread (1791144994.129499).

# Backlog ledger, 4 Oct 22:03Z

**Count.** 74 open (84 at 21:20Z): 18 infra, 56 other lanes. The queue holds 22 ready for a train (6 of them infra's), 38
waiting, and 14 stacked on another branch. Every open head was tested with `git merge-base --is-ancestor f59913b20`;
three contain `afacde975`, which failed its check and won't land: #1082, #1108, #1112.

**Verdicts.**
- *land*: in the queue, or will be once its tier passes or its grant comes.
- *register*: kept open, waiting on a named PR or event; the row says which.
- *close*: superseded or without a consumer; the row names what replaces it.

## Infra (18): decided

| PR | State | Verdict | What |
|---|---|---|---|
| #978 | ready | land: next train | git's changed names with `-z` where they decide a gate |
| #986 | ready | land: next train | cluster policy show, diff and override |
| #988 | ready | land: next train | one GPU usage computation; usage hourly and wasters |
| #991 | ready | land: next train | `research monitors`: the steward watch's long-term home |
| #1044 | ready | land: next train | vy-keeper: standing campaign targets |
| #1068 | ready | land: next train | `check --on auto` |
| #1128 | ready | land: next train | `research notes push` in the notes clone lands on the notes' main |
| #1135 | quick tier running on node 1 | land | `research run --on` says launched only after job.json (replaces #1111) |
| #1136 | tier queued on node 1 | land | a grant carries across a restack (replaces #955) |
| #1138 | tier queued on node 1 | land | node 1's infra loops as systemd units (replaces #997) |
| #1139 | tier queued, base #1138 | land after #1138 | the steward's watch and node-sweep as node timers (replaces #1134) |
| #1143 | new 22:20Z, tier queued | land | the queue's grant paths from what landing changes (fixes the spurious grants) |
| #1147 | new 22:30Z, tier queued | land | `replay_set` and `replay_expect` label keys (migration step 2) |
| #1004 | open, base merged | land: retarget to main and queue | node 1's ended runs reach R2 in bounded rounds |
| #1012 | waiting for grants | land once red-team and vllm-coordinator grant | `research merge` pushes main to node 1's bare repository |
| #1055 | waiting for grants | land once red-team and vllm-coordinator grant | no presigned URL reaches a run's record |
| #1065 | draft, base #1055 | register: after #1055 | sign the Lean bundles' URLs with a GET-only credential |
| #992 | draft, 1,116 behind | register: restack after the refactor's `tools/research` move | retention gc as default rules; #1139's node-sweep is the live sweep until then; `vy-retention-gc@` stays off |
| #993 | in ci's tip `be2452acd` | land with the tip (reopened 22:30Z; #1138 restacks on it) | paths after `--by`/`--ref` in `research deploy` |
| #895 | draft, 1,460 behind | close: no consumer while there's no new spend | Nebius `launch.sh` per-run overrides for another VM; reopen when a launch is approved |

Infra's own close-out by 01:00Z: #895 closed; #993 lands with ci's tip; #1068 and #988 restacked on that tip (22:30Z); the 9 *land* rows in trains or ready; #1004 retargeted; grants
asked of proofs for #1012 and #1055.

## Other lanes (56): provisional, for architecture and ci

`By` is who marked or queued it (`research queue status`).

| PR | By | State | Provisional verdict | What |
|---|---|---|---|---|
| #772 | bc-8416bc72-c4 | draft, waiting | owner's call: mark ready, register, or close | C-Flock: read a registered table at a private index (hidden_gather, fr |
| #786 | bc-8416bc72-c4 | draft, waiting | owner's call: mark ready, register, or close | C-Flock live PROTOCOL.md under --zk: what flock-circuit --zk sends, an |
| #864 | bc-e90634dd-8e | draft, waiting | owner's call: mark ready, register, or close | pouw circuit: per-call rows on hm96-sha512/row-seg/v1, registered rows |
| #884 | - | draft, stacked, base cursor/pouw-row-seg-a-rows-e3fa | register with its stack (lands after its base) | pouw circuit: Boolean lowerings of PoUW's six word primitives |
| #937 | bc-15ada664-f3 | draft, waiting | owner's call: mark ready, register, or close | pous: freeze-time hardening (challenge-key secrecy, graded RTT gap, co |
| #948 | bc-8416bc72-c4 | draft, waiting | owner's call: mark ready, register, or close | lean audit: --build takes one of the node's Lean audit slots (land aft |
| #961 | bc-b8aaadaa-ae | open, ready | land: next train | vllm fold: bind each Definition at the version the Build binds (SiLU,  |
| #967 | registered-sou | draft, waiting | owner's call: mark ready, register, or close | PoUW Lean: TileProofSoundAll from sampled proofs' RegisteredSound (dra |
| #999 | bc-8416bc72-c4 | draft, waiting | owner's call: mark ready, register, or close | soundness: private circuit (protocol 2) at the universal unit, with pu |
| #1001 | fp8-table | open, ready | land: next train | pouw bench: the FP8 served table (per-input bounds, batch tile replay, |
| #1010 | bc-15ada664-f3 | draft, waiting | owner's call: mark ready, register, or close | pous lean: the bulk read's HBM placement bound, from a new named assum |
| #1018 | - | draft, stacked, base cursor/zk-reg-95d4 | register with its stack (lands after its base) | soundness: zk_session_drawnR and zk_session_regValsR (drawn units and  |
| #1020 | - | draft, stacked, base cursor/pouw-lean-registered-sound-e3fa | register with its stack (lands after its base) | PoUW Lean: honestProver_bounded from decisive tile games (Unambiguous  |
| #1026 | bc-b8aaadaa-ae | draft, waiting | owner's call: mark ready, register, or close | vllm: block-FP8 fused-MoE experts on sm_120 (Qwen3-235B-A22B-FP8 TP8), |
| #1031 | - | draft, stacked, base cursor/pouw-bool-lowerings-e3fa | register with its stack (lands after its base) | pouw circuit: the hiding tile's Keccak words as Boolean Definitions (` |
| #1034 | - | draft, stacked, base cursor/pouw-bool-lowerings-e3fa | register with its stack (lands after its base) | benchmarks/pouw: `hidden_zk`, PoUW's hidden tile check (Pearl-C4's row |
| #1036 | bc-d6f8b221-34 | draft, waiting | owner's call: mark ready, register, or close | trial: Verity's core in the agreed layout, remote and onsite end to en |
| #1045 | - | draft, stacked, base cursor/fp8-moe-sm120-81c4 | register with its stack (lands after its base) | vllm: cc 12.0's blockwise and fused-MoE FP8 steps of record, from P1 |
| #1049 | bc-8416bc72-c4 | draft, waiting | owner's call: mark ready, register, or close | soundness: --zk sessions with the verifier's public inputs (zk_session |
| #1052 | - | draft, stacked, base cursor/pc-wiring-95d4 | register with its stack (lands after its base) | soundness (protocol 2): private circuits by hidden Merkle reads, with  |
| #1059 | bc-19c498a8-62 | open, ready | land: next train | Lean: say guarantees, not pins (records, tooling, docs) |
| #1060 | - | draft, stacked, base cursor/zk-pubin-95d4 | register with its stack (lands after its base) | soundness: ownAtDrawsHP_of_check, the public-input sessions' registere |
| #1062 | bc-8416bc72-c4 | open, ready | land: next train | Verifier refuses an output group that overruns its unit's slot (D11),  |
| #1063 | bc-8416bc72-c4 | draft, waiting | owner's call: mark ready, register, or close | Subtree read: one hidden Merkle path opens an aligned run of cells (Me |
| #1079 | bc-19c498a8-62 | open, ready | land: next train | check: the Lean audit is a group of its own, so the suites that use Le |
| #1080 | - | draft, stacked, base cursor/zk-scope-v2-95d4 | register with its stack (lands after its base) | C-Flock bridge: registered reads at the widened scope (ScopeW.ReadsP;  |
| #1081 | bc-8416bc72-c4 | draft, waiting | owner's call: mark ready, register, or close | Boolean Definitions for C-Flock's inner-verifier algebra (GF(2^128) mu |
| #1082 | pc-stack | open, waiting | rebuild without afac (or close) | pouw: `Shape.tile_sub` cuts Pearl-C's and Pearl-C4's tile units into a |
| #1085 | bc-19c498a8-62 | open, ready | land: next train | lean: Lean's jobs in check move from tools/check to tools/lean |
| #1086 | memory-account | draft, waiting | owner's call: mark ready, register, or close | pous: enforced secure-erasure verifier, difftested against Lean's eras |
| #1088 | - | draft, stacked, base cursor/pc-reads-95d4 | register with its stack (lands after its base) | soundness: route P, hidden wiring over a public gate table (WiringSoun |
| #1090 | bc-8416bc72-c4 | draft, waiting | owner's call: mark ready, register, or close | soundness: recursion, the recursive audit's soundness with the stage t |
| #1093 | l3-tilecheck | draft, waiting | owner's call: mark ready, register, or close | PoUW Lean: L3 slice 5, lean's two −0 rulings (nvf4Block's −0 is 0x8, c |
| #1096 | memory-account | draft, waiting | owner's call: mark ready, register, or close | pous lean: secure erasure of the keyed page fill, with distinct byte r |
| #1099 | cap-unit | draft, waiting | owner's call: mark ready, register, or close | pouw circuit cap: Pearl-C's per-tile cap (rev1's capOK) in gates, opt- |
| #1106 | bc-8416bc72-c4 | draft, waiting | owner's call: mark ready, register, or close | soundness: PoUW's row shapes (scopeOkW), the last case-by-case scope w |
| #1108 | bc-e90634dd-8e | open, waiting | rebuild without afac (or close) | pouw pc8: a short last tile row (16 / m, as the scheme), its own templ |
| #1112 | bc-b8aaadaa-ae | open, waiting | close: superseded by #1130 | verity_vllm: GLM-5.3's DSA indexer and FA3 sparse MLA as circuit Defin |
| #1113 | bc-d6f8b221-34 | draft, waiting | owner's call: mark ready, register, or close | using-slack registry: @architecture, held by the layout-trial lane |
| #1117 | bc-19c498a8-62 | open, ready | land: next train | check's Lean audit: key a pass on what the audit reads |
| #1118 | bc-81ff5c35-39 | open, ready | land: next train | check: lean-suites waits on lean-build alone, beside the partition che |
| #1119 | bc-19c498a8-62 | open, ready | land: next train | check's Lean audit: keep each package's build after a passing audit |
| #1120 | status | open, waiting | land once the owner marks it ready / gets its grant | soundness: registered reads in the --zk session (zk_session_soundR) an |
| #1121 | bc-8416bc72-c4 | open, waiting | land once the owner marks it ready / gets its grant | soundness: ownAtDrawsHP_of_check, registered reads owned at the draw i |
| #1123 | bc-15ada664-f3 | open, waiting | land once the owner marks it ready / gets its grant | pous: P2 v3 with the frozen spec's SHAKE256 keys and k = 105, ChaCha8  |
| #1124 | bc-3e100045-0b | draft, waiting | owner's call: mark ready, register, or close | research msg owners: the ownership map, from the registry |
| #1125 | bc-ecea50f6-c5 | open, ready | land: next train | network_traces: the active warden in front of a live vLLM |
| #1126 | bc-b8aaadaa-ae | draft, ready | land: next train | circuit-check cache v2: key each target on what its own check read or  |
| #1127 | bc-d6f8b221-34 | draft, waiting | owner's call: mark ready, register, or close | Glossary: spec, lock, lemma, TCB, approach; notes for writing, the sto |
| #1129 | bc-8416bc72-c4 | open, waiting | land once the owner marks it ready / gets its grant | class_statement: partition_binding and owners_of cache per PartitionUn |
| #1130 | bc-b8aaadaa-ae | draft, waiting | owner's call: mark ready, register, or close | verity_vllm: GLM-5.3's DSA indexer and FA3 sparse MLA as circuit Defin |
| #1131 | bc-ecea50f6-c5 | draft, waiting | owner's call: mark ready, register, or close | network traces: `active_replay.py --cpus` pins the server, the proxy a |
| #1132 | l3-tilecheck | draft, waiting | owner's call: mark ready, register, or close | PoUW Lean: L3 slice 6, lean's rulings 3, 4, A, B, D and F and C's firs |
| #1133 | bc-d6f8b221-34 | draft, ready | land: next train | friction: Daniel's migration rulings of 4 Oct |
| #1137 | bc-81ff5c35-39 | draft, ready | land: next train | tools/check: rename_merge.py, merge a PR onto a tip that moved the fil |
| #1140 | bc-81ff5c35-39 | draft, ready | land: next train | move-check: certify that BASE..HEAD is a pure move |

Notes on the provisional rows:
- #1082 and #1108 contain `afacde975`: rebuild each as a new PR from its pre-afac head (circuits' route for #1112), then
  close the old one.
- #1137 (`rename_merge.py`) and #1140 (`move-check`) are ci's fast-lane parts (1 and 2) and land before the first move.
  #1126 is circuits' content-keyed cache, also before the first move.
- #1036 (the layout trial) and #1113, #1127, #1133 are architecture's.
- #948 gives `audit.py --build` a Lean slot; `main`'s `audit.py` takes none yet, so it stays open. It conflicts with #1085's
  move of Lean's jobs to `tools/lean`; whichever lands second restacks.
- Drafts marked "owner's call" have sat unmarked for a day or more; a draft nobody will mark ready by 01:00Z should be closed
  or registered with what it waits on.
