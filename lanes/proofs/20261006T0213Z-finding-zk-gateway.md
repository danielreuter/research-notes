---
id: proofs/20261006T0213Z-finding-zk-gateway
campaign: proofs
lane: proofs
kind: finding
status: done
repo: danielreuter/verity
origin: bc-32c932ac-e151-5c17-a04d-54c57d2bfd73 (zk-gateway, for the proofs coordinator bc-8416bc72)
---

# The prover gateway's send check: nothing leaves the GPU workers that the gateway did not fix (prototype, node 1, K = 4096)

## Answer

Yes, for both phases of a recursive session, in a prototype that runs end to end on node 1 at K = 4096.

- **Inner phase** (ZK off). `verity_flock.rec_live`'s proxy is the gateway. The coin server receives only the public
  schedule and salted hashes. Every tree-top node and every message row goes out as a registered row's `b ‖ c`, each under
  its own fresh 192-byte salt. The session is held to a pinned schedule, and `Link`'s `y` must be zero.
- **Outer phase** (`--zk`, `FC_GATE=1`). The gate recomputes the level-0 commitment from the host witness and holds every
  algebraic frame to the statement's skeleton. It recomputes the whole opening in lock step with the device and compares
  every frame byte for byte, and it builds the inner proof itself with its own lincheck comb.

Everything that leaves is one of three things: the gateway's own value, a value masked by a pad the device never sees, or
a value the gateway recomputed and compared. The device's one remaining choice is where to stop the session (a refusal).
That is at most log₂(R + 1) bits a session, R being a rep's rounds, and the auditor sees every stop.

**For Daniel, decision 2.** The rule the prototype needs is not "recompute everything". It is: mask the algebraic phase,
recompute the polynomial commitment's outputs, and fold the lincheck's comb itself. The gateway does not recompute the
zerocheck or the lincheck, which are the bulk of the device's arithmetic. Two places need more than masking:

- `T'` needs recomputing. The lane-phase relation alone leaves a device 256 bits of its choice (§10.1).
- The comb needs folding by the gateway. A device's comb would choose the rows the inner proof proves.

What that costs, over V*'s eight `--zk` statements: prove is 46.8 s gated, against 7.4 s with the host witness ungated
(6.3×) and 6.7 s with today's device witness. The proof bytes are identical. The gateway does about 176 CPU seconds of work a
session. All of it is CPU work that sits on the session's critical path today. Three changes, not yet made, would take
about 15 s of the 39 s the gate adds off that path; the shadow's opening and the comb fold stay on it (see "What it costs").

## Branch

`cursor/zk-gateway-95d4` at 606955894, off `cursor/rec-reprice-95d4` 454e3cd86. The runs are of b98ea02f9 and earlier
commits; 606955894 changes only PROTOCOL wording. The branch merges cleanly into rec-reprice's
current head edf8f70ad (which brings main's Lean move): the move touches none of this branch's files, and the Lean paths
the pod script reads are still there. The branch changes no Lean file, no circuit Definition, no `RecOpen` and no algebra
statement. The rule is written in the live `PROTOCOL.md` §10 (backends/flock/live).

## The send check's rule, outer phase (§10.1)

Five kinds of rule:

- **constant**: the gate holds the only allowed value.
- **recomputed**: the gate computes the value from the host witness, its own randomness and the coins, and refuses any
  other.
- **masked**: the wire carries `v + h`, where the pad `h` is host-only.
- **the gateway's own**: the device never touches the value.
- **relation**: an early tripwire that fixes nothing by itself.

| message (one rep, in §1's order) | rule | why the device has no free choice |
|---|---|---|
| the frame skeleton: domain, every label, each item's op, kind and length, every round's coin count | constant | a function of the statement's shape |
| statement digest (`bind_statement`) | constant | the digest of the statement the gateway loaded |
| witness cap: `Commit`'s root, `bind_statement`'s cap, Ligerito level 0's cap | recomputed | the level-0 recheck: `commit_zk` of the host witness under the session's salts and hiding |
| pads label and root | the gateway's own | the masking challenger inserts them |
| masked algebraic values (`round1_ab'`, `round1_c'`, `G_j`, `final_a'`, `final_b'`, `q_j`, `z_partial'`) | masked | uniform whatever `v` is. A `v` that breaks §4's rows stops the session at `zk_finish`'s self-check, before anything that depends on them leaves |
| `final_c'` | the gateway's own | the inner proof sends it, from the host |
| `s_hat_v` of the masked claims and of the region claims | recomputed | from the host witness at the claim points (coins), or from public data |
| Ligerito's `target` | recomputed | a function of the `s_hat_v` and the opening's coins |
| level 0's OOD value `y'`, lane messages `msg_j'`, `e^r'` | masked | as the algebraic values |
| every grinding nonce | constant 0 | live coins need no grinding |
| `T'^r` | recomputed | `⟨w^r, y_1^r⟩ + ρe` with the honest `e`. The relation alone lets a device shift `e` by δ and `T'` by ρδ |
| `ybar^r`; levels 1+ (code switch, caps, OOD, sumcheck, nonces) | recomputed | functions of the host's padding, `y_1'^r`, the coins and the host's salts for trees 1..R |
| the inner proof (`[ρ, σ]`, `τ`'s commitment, `Y`, its openings) | the gateway's own | `zk_finish` from the host's pads, over §4's rows replayed from the passed values with the gateway's own comb fold. The device's comb is dropped |
| the proof bytes | recomputed | every transcript field equals what the gate passed, and the rows and paths are the recomputed trees' |

The prototype is stricter than this rule in one place. The shadow recomputes the whole opening, level 0's lane rounds
included, and the opening that leaves is the shadow's.

## The send check's rule, inner phase (§10.3, `rec_live`)

| item | rule | why the M0 prover has no free choice |
|---|---|---|
| `Hello` | constant | forwarded without Σ, only when it equals the pinned schedule's |
| `Commit`'s level-0 roots, and each round's caps | salted | each 64-byte node is sent as a registered row's `b ‖ c` (`top_rows`: its 32 u16 words, then 32 zero words; `hm96-sha512/row/v1`) under a fresh 192-byte salt |
| a round's free message | salted | `c_k`: its rows, each under a fresh salt |
| statement digest, labels, domain, nonces | dropped | public constants, or functions of the hidden statement |
| `Link`'s `y` | constant 0 | the gateway refuses anything else |
| stream names, `Open`'s parent and position, every count (coins, cap nodes, message rows) | constant | the pinned schedule's (`--schedule`, or the first session's) |

A refusal stops the session: every later request is refused for the same reason, and only what the coin server had
received is written.

## The level-0 recheck: what it costs

The recheck is `commit_zk` over the gateway's own host witness, before `Commit`. It runs on the prover's 16 cores, shared
with the device's host phases.

| stmt | m | recheck wall (s) | recheck CPU (s) |
|---|---:|---:|---:|
| L0 | 32 | 1.768 | 17.81 |
| L1 | 31 | 0.919 | 8.81 |
| L2 | 31 | 0.843 | 8.77 |
| L3 | 30 | 0.421 | 4.20 |
| L4 | 30 | 0.452 | 4.30 |
| L5 | 29 | 0.326 | 2.84 |
| L6 | 28 | 0.223 | 1.88 |
| alg | 29 | 0.241 | 2.76 |
| **sum** | | **5.192** | **51.37** |

The recheck uses about 10 CPU seconds per wall second. It scales with the committed size: about 1.1 CPU s per 2^28 at
m ≥ 30, and a little more below. It reads only the host witness and the gateway's own salts and hiding, so it can run a
session ahead.

## Negative controls, each refused by name

Outer (`FC_GATE_TAMPER`, on L6; serve rejected every one):

| control | the device | refusal |
|---|---|---|
| `root` | flips a bit of its level-0 root | `GATE-REFUSED: level-0 root: the device committed d94479c2a771c6a7 where the recheck has d84479c2a771c6a7` |
| `witness` | proves a witness one bit off the host's | `GATE-REFUSED: level-0 root: the device committed c94f700b99c434a9 where the recheck has 387c9588f878c65a` |
| `label` | flips a label byte in the algebraic phase | `GATE-REFUSED: algebraic phase, round 0, frame 1: label "glock-r1cs-v0" where the statement has label "flock-r1cs-v0"` |
| `opening` | flips an observed value in the opening's first round | `GATE-REFUSED: opening round 0, frame 2: the device's observe slice of 128 differs from the gateway's in its payload` |
| `algebra` | flips a masked value, in its frame and its proof alike | `PROVER-STOPPED: the batched constraint fails (⟨c, h⟩ ≠ t)` (`zk_finish`'s self-check) |
| `algebra-proof` | flips a masked value in its returned proof only | `GATE-REFUSED: the proof's exposed value 0 is not the one the gate passed` |

Inner (V*'s inputs, `rec_vstar`, on the last salted session):

| control | refusal |
|---|---|
| `forge --what top` (a clear top that does not open the salted one) | `GATE-REFUSED: tree top: circuit/rep0 round 62 cap 0 does not open the salted top the coin server received` |
| `forge --what unsalted` (a record of clear tops) | `GATE-REFUSED: tree top: the record's tops are not salted (rec_live.TOPS)` |

## End to end on node 1

All runs were on node 1 (`vy-nebius-1`), with one RTX PRO 6000. The prover and gate shared 16 cores, and serve used 16 more.
Numbers are medians of 3 sessions after 1 warm, between 5:40 and 6:42 PM PDT on Oct 5. The inner phase was rerun at
b98ea02f9 between 7:05 and 7:10 PM PDT, after the top format changed (see "Salted tops").

Every gated session was verified three ways:

- serve accepted all 8 statements × 4 sessions;
- upstream `replay --zk` accepted each statement's kept gated session;
- Lean's `flock-verify` accepted all 8, and the inner session with `--coins os`, both the first inner run's and the
  rerun's.

Outer, per statement. Prove times are for three modes:

- **dev**: today's path, with the witness assembled on the device.
- **host**: `FC_HOST_WITNESS=1`, ungated.
- **gate**: `FC_GATE=1`.

| stmt | prove dev | host | gate | session gate | serve verify | shadow wait | comb fold extra | gateway CPU/session | bytes/rep |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L0 | 1.195 | 1.410 | 10.089 | 10.491 | 1.525 | 3.914 | 0.901 | 52.6 | 1,037,530 |
| L1 | 0.808 | 0.972 | 6.113 | 6.243 | 1.158 | 2.291 | 0.818 | 27.4 | 1,005,602 |
| L2 | 0.869 | 1.038 | 5.713 | 5.908 | 1.174 | 1.950 | 0.801 | 26.8 | 1,005,602 |
| L3 | 0.548 | 0.758 | 4.170 | 4.271 | 1.094 | 1.239 | 0.895 | 15.3 | 946,586 |
| L4 | 0.574 | 0.657 | 4.065 | 4.208 | 0.972 | 1.285 | 0.775 | 15.2 | 946,586 |
| L5 | 0.486 | 0.577 | 2.789 | 2.991 | 0.652 | 1.065 | 0.429 | 10.4 | 834,202 |
| L6 | 0.371 | 0.388 | 2.191 | 2.346 | 0.654 | 0.796 | 0.440 | 7.8 | 777,946 |
| alg | 1.821 | 1.606 | 11.626 | 11.750 | 7.112 | 0.861 | 5.477 | 20.3 | 879,866 |
| **sum** | **6.672** | **7.405** | **46.756** | **48.209** | **14.339** | **13.403** | **10.537** | **175.9** | **7,433,920** |

Seconds, except bytes. Sessions summed in dev and host modes are 11.421 s and 12.607 s. Gateway CPU is the gated process's
CPU over the ungated one's. The host-witness prover's own CPU is about 75.8 s a session, so the gateway is about 2.3× that.

Beside rec-reprice (`note:proofs/20261005T0633Z-finding-rec-reprice`): its V* had prove 6.522 s and session 11.312 s in its
first run. Its rerun had prove 5.846 s, session 9.889 s, serve verify 12.934 s and Lean 595.2 s. This lane's dev mode,
6.672 s and 11.421 s, is rec-reprice's like for like. Proof bytes match exactly: 14,867,840 over both reps. Lean's verify
summed to 626.3 s over the nine sessions (inner 49.4 s). Peak host RSS gated is 17.7 GB on L0 and 16.9 GB on alg, against
8.3 GB and 12.4 GB in dev mode.

**What it costs.** The gate adds 39 s to prove. Of that:

- the level-0 recheck is 5.2 s (51 CPU s);
- the device's wait for the shadow opening is 13.4 s;
- the gateway's own comb fold is 10.5 s (on alg it is 5.5 s, the largest piece);
- the rest is the device's host phases slowed by the gate's threads on the same cores. On L0, `t.arithmetic` is 2.73 s gated
  against 0.24 s per rep with the host witness.

Three changes not yet made would shorten it:

- give the gate cores of its own, which removes the contention (about 10 s);
- run the recheck a session ahead (5.2 s);
- have the device skip the opening the shadow replaces, which frees the device's share of the cores.

What stays on the path is the shadow's own opening (15.7 s over the eight statements, measured under contention) and the
comb fold (10.5 s). I have not measured the result of the three changes.

**Inner** (r20261006-020547-cf84, 4 sessions held to rec-reprice's pinned schedule):

| | this lane | rec-reprice's proxy |
|---|---:|---:|
| prove | 0.997 s | 0.875 s |
| session | 1.060 s | 0.909 s |
| bytes/rep | 963,794 | 963,794 |
| host peak | 20.7 GB | 20.7 GB |
| GPU peak | 73,987 MiB | 74.0 GiB |

The prover's cores were 100% busy before the session (idle-weight backfill). Every session has 278 rounds, 510 message rows,
2,082 coins and 16 caps.

What reaches the coin server is 147,456 B of salted tops (1,152 nodes × 128 B) plus 65,280 B of row commits, 212,736 B in
all. rec-reprice's coin server got clear caps, 73,728 B, plus the same row commits, 139,008 B. The record holds none of the
session's 640 distinct clear nodes. Salting costs the gateway 29 µs a node, about 0.03 s a session (measured on the agent VM,
salt draws excluded).

Checks (r20261006-020736-15a0): upstream replay accepted (18.65 s wall), and `rec_vstar` accepted 1,118 openings and 510
rows in 0.47 s.

## Runs and evidence

PDT on Oct 5; every run record is preserved.

| step | run | record art | PDT | result |
|---|---|---|---|---|
| build (prover binary 8dd0ea75, statement digest 2602e07c, identical to rec-reprice's) | r20261006-004710-e840 | art:1e513a5f1b48a1043cf07959b203c77e88845f8f2f51b07571f96d511f7f5e38 | 5:47 | passed |
| inner (old top format, `hm96-sha512/v1/node`) | r20261006-005146-188b | art:ba3278905a22b803125ce66ed84bef9b6ed3a24e5bf42cfb5d4cd363c34f6287 | 5:51 | passed: 4 sessions held |
| icheck (old format) | r20261006-005431-695f | art:b5e36cf2ffc30f8d4c81a3cae0084b13e62b5adc0a8c7d59fd1a97c228737d14 | 5:54 | passed; both controls refused |
| ostage (V*'s 7 `RecOpen` statements from that inner's last session) | r20261006-005442-e283 | art:0e624d49f0642aa5f502e9fb1eb1b1a5ca603eac0e4e39ed9156ecdbea18c708 | 5:54 | passed |
| alg (claims, `InnerRepCheck`) | r20261006-005502-9218 | art:6523bd88df3854bbb4771099835e4b85e89b0fb48175b2e032460935e496cde8 | 5:55 | passed |
| oprove L0–L6 `MODES=dev,host,gate CONTROLS=L6` | r20261006-010844-c628 | art:6196c69025a97ddfa21387e8edb4a71a114470d67b030e4fca736ef982ea3abf | 6:08 | passed: serve accepted every session; 6 controls refused |
| oprove alg `MODES=dev,host,gate` | r20261006-012457-b6c4 | art:29bc5f89ca43d9aaabce42e1aaff9f53fb298eddfa8f46cdda1d266ee298fade | 6:24 | passed |
| oreplay (upstream `replay --zk` of the 8 gated sessions) | r20261006-013154-11dd | art:43187eac3a0592190101f9bdee89cd9b9b773a21528e311a4d70cea2d077ac33 | 6:31 | 8 of 8 accepted (6.4 to 42.1 s) |
| lean (8 gated sessions `--zk`, the inner `--coins os`) | r20261006-013204-9c98 | art:a57c33f859a051704fbe9152d844fa26f9885c8ccd95852c461da3facefdf367 | 6:32 | 9 of 9 accepted |
| inner rerun at b98ea02f9 (tops as registered rows) | r20261006-020547-cf84 | art:6e71f21f988a414ee806cc70ed7cdff5d4bef397cc096322945b5285835b8366 | 7:05 | passed: 4 sessions held |
| icheck at b98ea02f9 | r20261006-020736-15a0 | art:eedf6eae8396ecdd0f1cb947ee7556a8d7dc468ee2186b36f7400e628027db5c | 7:07 | passed; both controls refused |
| lean, the rerun's inner session `--coins os` | r20261006-020801-73dd | art:b27e2ecc945ec88bb789d55f3340293f4a0f88b3ca10ce6f4ddb42feb3934dc9 | 7:08 | accepted (verify 99.3 s, wall 4:11, beside other lanes' Lean audits) |

Failed or refused, kept for the record:

- r20261006-004044-b2b4 (art:413611a097a02c1d08f08edca9e6f776d13ee9bda9224562613040ee2d3aade7): a build superseded when the
  binary's key stopped hashing `*.md` (b99343d94).
- r20261006-004524-c5e5: an inner run that failed "run STEP=build first", because a PROTOCOL.md edit had changed the
  binary's key.
- r20261006-004637-08c9: launched from a stale commit and refused by the queue.

The outer statements were staged from the first inner run's last session. That inner data is kept on node 1 at
`/workspace/jobs/zk-gateway/data/k4096/inner-node`, and the rerun is at `.../inner`.

## Salted tops: the format rec-step3's circuit reads (b98ea02f9)

rec-step3 (`cursor/rec-step3-95d4`; its note to this lane is the coordinator store's `zk-gateway-from-rec-step3.md`) read the
first format, each node as hm96's inner digest under `default_key`. That format does not suit V*'s circuit, which commits
each opening's `out` as a registered row. With it, `RecOpen` would have to compute hm96 on every opening: two private SHA-512
compressions (116,240 ANDs), the key product and a salt port. b98ea02f9 commits each node as a registered row instead
(`top_rows`, `commit_top = commit_rows(top_rows(top), salts)`), with `TOPS = "hm96-sha512/v1/node-row"`. A test pins it to
`Registered.commit`'s `b ‖ c`.

Climbing to the committed tops then costs `RecOpen` no hashing of its own. The verifier builds a registered value from the
coin server's `b ‖ c`, and each opening's `out` reads the row of the node it climbs to. rec-step3 reports `RecOpen_v3` at 25
compressions (LANES = 64, H = 8) against v2's 29. The gateway pays one more CPU SHA-512 a node (18 → 29 µs). The rest of the
layout is rec-step3's as it stands:

- the JSON keys: `roots[table].top` and `salts`, and each round's `caps` and `cap_salts`;
- a fresh salt for each copy of level 0;
- the schedule pin, `y = 0` and the stop on refusal.

When the branches meet, rec-step3 switches `rec_vstar.tops` and `rec_outer.TopValue` to these keys.

**What "the outer circuit climbs to the committed tops" still needs, which waits for rec-step2/3:**

- `rec_outer` registers each level's tops as a value (`rec-top-L<l>`) under the gateway's salts, in place of the clear cap
  nodes;
- the verifier checks that value's root against an entry it builds from the coin server's `b ‖ c`;
- each `RecOpen`'s expected-node read becomes a read of that row.

None of that touches this branch's gateway.

## The gateway as a Lean program, on #1237's `FlockAudit`

This is the interface on [#1237](https://github.com/danielreuter/verity/pull/1237) (`cursor/lean-drives-1-95d4`, 81ec13c9).
`FlockAudit.Prog α` is a program as data:

- `ask` takes a `Req` (channel, canonical bytes, the longest reply it takes);
- `coin n` draws randomness;
- `ret` returns.

`runM` interprets a program, `replay` checks a recorded transcript, and `Frame` is the one reader. The auditor is one such
program. The gateway would be a second, the developer's: `gateway : GwOwn → Prog GwVerdict`. Its environment is the two
parties it does not control, the GPU worker and the auditor's live endpoint. Its coin nodes are its own randomness.

**What it holds before the run** (`GwOwn`):

- the statement (circuit, instances, public file), by content key through `archive`;
- the profile;
- the host witness.

**Coin nodes** (never answered by a worker):

- every tree's salts (level 0's `LeafSalts` key, and trees 1..R');
- the level-0 hiding `Level0Zk`;
- the pads `h` and `mu`;
- `zk_finish`'s randomness;
- the inner phase's node and row salts.

**Requests and answers.** Each is a `Frame`; each bound is exact, or the statement's proof size.

| channel | request | answer | the gateway's rule on the answer |
|---|---|---|---|
| `archive` | a content key | the object | held to its key (`Auditor.fetch`) |
| `device` | `load`: the witness's key, the level-0 salts' key, `Level0Zk` | ack | none |
| `device` | `root` | the level-0 cap | equal to the recheck's, else `levelZeroRoot` |
| `device` | `round r` with round r−1's coins | round r's frames | algebraic phase: the skeleton, then the pads added; opening: equal to the shadow's, else `opening r f` |
| `device` | `proof` | `(R1csProofLigerito, Commitment)` | every exposed value the one passed, `final_c'` the gateway's, the commitment the recheck's, the opening the shadow's, nonces 0 |
| `auditor` | `Hello`'s public part, `Commit`, each round's frames as the gateway fixed them, the proof | the round's coins (the skeleton's count) or the verdict | the count; nothing else is read |
| inner `device` | the M0 prover's next request (`Hello`, `Commit`, `Open`, a round, `Link`, `Finish`) | the gateway's answer (coins, from `auditor`) | the pinned schedule; `Link`'s `y` zero |
| inner `auditor` | the schedule's public part, the salted node and row commits (`b ‖ c`) | coins | the count |

**Refusals**, one constructor each. Each carries today's string (`GATE-REFUSED: …`, `PROVER-STOPPED: …`), so a Lean run and a
Rust run of the same session refuse with the same bytes:

- outer: `levelZeroRoot`, `skeleton r f what` (label, op, kind, length, coin count), `opening r f`, `exposed i`, `finalC`,
  `commitment`, `nonces`, `early` (a proof before the opening ends), `selfCheck` (`zk_finish`'s batched constraint);
- inner: `hello`, `roots`, `open stream`, `round i`, `finish`, `linkY`.

A refusal is the program's `ret`, and nothing is sent after it. (`tree top` is V*'s refusal, not the gateway's: the gateway
makes the salted tops itself.)

**What it would prove**, in the shape of `auditor_draws_once`:

- `refusal_is_last`: after a refusal, no request on `auditor`. This is a syntactic fact of the program.
- `gateway_no_free_choice`: for every `device` environment, the bodies the run sends on `auditor` are the honest device's run's
  bodies, cut where it refused, up to the pads. The statement is a bijection of the coin tape (each pad shifted by the
  device's deviation on the value it masks) under which the two views agree before the cut. The device's only choice is the
  cut. It needs two named assumptions:
  - the pads' commitment hides (hm96's statistical bound);
  - the inner proof's view is simulatable from the wire values and the coins (§8's simulator).

**Why I did not write it in Lean now.** The program around the checks is small: the table above, the skeleton, the
comparisons, `zk_finish` and the inner phase's salting. But the recheck and the shadow are a CPU Ligerito prover: `commit_zk`
over the whole witness (2^28 to 2^32 words for V*'s statements), plus the opening's basis fold and levels 1+. `flock-verify`
has only the verifier's side. A Lean prover at that size is a larger program than everything else here, and it would run on
the session's critical path.

The choice is Daniel's, because it moves the trusted base:

- **(a)** the shadow as a third channel, `pcs`, answered by today's Rust (`commit_zk` and the opening), its honesty a named
  assumption until a Lean prover exists. With (a), the gateway program is about the size of `Auditor.lean`.
- **(b)** the Lean prover.

## What's left before the gateway is the Lean program

1. Daniel's choice of (a) or (b).
2. The `device` and `auditor` framing as `FlockAudit` frames. Today the device is an in-process callback (`rounds`, `hook`,
   the returned proof), and the auditor is the live TCP stream.
3. The skeleton (`gate::skeleton`, from `zkv::replay`) and `zk_finish`, in Lean.
4. The inner gateway (`rec_live`, Python today) as the same program's inner phase: the schedule check, the row commitments and
   `Link`'s `y`.
5. `refusal_is_last` and `gateway_no_free_choice`, with the two assumptions as named `Prop`s and entries in the package's
   `upstream` watch list.

## Merging

The branch changes files under `backends/flock/` (`live/src/gate.rs`, `flock-circuit.rs`'s gate, `rec_live`, `rec_vstar`,
the pod script, the live PROTOCOL), so it needs a red-team grant and a `check` with lean-agreement. It adds or changes no
circuit Definition, template or Boolean lowering, so there is no `circuit-check` report to give. Tests:
`backends/flock/tests` `-k 'rec or live or pod or gate'` gave 71 passed and 7 skipped. That needs `research data
fetch-fixtures` first, for `test_rec_algebra`'s fixtures. The Lean ones ran serially, because the Lean-verifier tests race on
one build directory under xdist.
