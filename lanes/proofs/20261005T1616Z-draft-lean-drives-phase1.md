---
id: proofs/20261005T1616Z-draft-lean-drives-phase1
campaign: flock
lane: proofs
kind: draft
status: open
repo: danielreuter/verity
origin: bc-ef589682-953d-5e18-be76-d46a3dd7cb43 (lean-drives-1, for the proofs coordinator bc-8416bc72)
---

# Lean drives, phase 1: the auditor's Lean program owns the unit draw and the round coins

Daniel's ruling (2026-10-05, 8:53 AM PDT): each party's Lean program runs its main loop, and Python, Rust and CUDA are
workers that answer its requests. Phase 1 asks whether the auditor's program can own the one-stage audit's unit draw
(`benchmarks/one_stage/a0.py`'s flow) and every live session's round coins. If it can, three assumptions leave the run:
`DrawFileZK`, `RecordCustodyZK` (= `RecordsLiveZK` ∧ `DrawFileZK`), and A6 (`uniform/flock-coin-server`).

**Answer: yes, in four PRs, with no blocker for the first.**

* PR 1 removes `DrawFileZK` for a0's flow. The program draws once (`Draw.drawWith` over its own coins, which is A3), sets
  up the statement at its own draw, and refuses a record whose draw is not its own.
* PR 2 lets the program read every live frame.
* PR 3 has the program build and open the coin tree. A6 leaves, and A3 plus hm96's hiding hybrid replace it.
* PR 4 has the program render the record. `RecordsLiveZK` then becomes a theorem about the program.

Costs, measured on a 4-core VM:
* Framing costs about 6 ms per session, against the server's 0.69 s.
* A pure-Lean coin tree costs 0.75 s per session on 4 cores (2.9 s on one), against the server's 0.69 s for the whole
  session today. That is the one real cost, and decision D3 asks Daniel about it.

The rest of this note covers the seven points of the brief in order.

## 1. What moves, and what each worker then answers

Today (option B), Python and Rust drive the run:

| step | today's owner | today's randomness |
|---|---|---|
| registration (R.record / R.check / R.matches_public) | `a0.py` (Python) | none |
| unit draw | `flock-circuit serve` at `Register` (Rust `unit_draw::draw`, /dev/urandom), or `--draw-file` written by `flock-verify draw` | /dev/urandom or Lean's `drawOS` |
| coin tree (key, coins, salts) at `Hello` | `flock-circuit serve` (Rust `coin_tree.rs`) | /dev/urandom (A6) |
| round openings, live verdict, `session.json` | `flock-circuit serve` | none |
| verdict of record | `flock-verify verify --archive` reads the draw from the record (`recordDraw`) | none |
| audit record and profile | Python (`one_stage.audit.audit_record`) | none |

In `flock-verify verify`, U1 compares the record's draw with a statement built from that same draw. So whoever wrote the
record chose the draw, and `DrawFileZK` is the assumption that this was the verifier's own draw.

After phase 1 (option A), one Lean program, `flock-audit`, runs the loop. Every arrow is a frame on a worker's
stdin/stdout:

1. **Register.** The program asks the developer worker to register. The worker answers with the content keys (SHA-512)
   of the circuit, the public file and the tables, plus the population. The program reads those files by content from the
   archive, as `verify --archive` does. The worker can name files, but cannot change what a key resolves to.
2. **Draw, once.** The program calls `Draw.drawWith (fun _ need => coins need) law pop`. `drawWith` is generic in its
   monad, so this is the verifier's existing sampler, unchanged. Each `coins` node runs `IO.getRandomBytes` under
   `Prog.run` (A3, identical to `drawOS`). No path of the program has a second draw (§3 of the tests).
3. **Session.**
   * PR 1: the program asks the serving worker for a session at the draw it sends. That worker is a Python wrapper of
     `flock-circuit serve --draw-file <the program's draw> --zk` and `prove`. It answers with the session's record and
     proof files, and the program reads them by content.
   * PRs 2-4: a relay worker carries the prover's TCP frames. The program answers `Hello` with its own coin tree's root
     and key (PR 3) and each `Round` with its own opening (PR 3). It stores the proofs.
4. **Verdict.** The program builds the statement at its own draw (`Stmt.setupTables … (some D.toJson) …`, the same call
   `Main.buildSession` makes) and decodes the record. U1 compares the record's draw against the program's own, so the
   check now does real work. Then it runs `Zk.verify` and prints `VERDICT {...}`. From PR 4 on, the record is the one the
   program rendered from its own transcript.
5. **Audit record.** In phase 1 this stays in Python, as a worker that reads only the program's verdict line. Moving the
   profile into Lean belongs to a later phase.

What each worker answers, all of it untrusted:

| worker | language | answers | PR |
|---|---|---|---|
| developer | Python (M0's `verity_flock.circuit` staging) | `register` → content keys and population | 1 |
| serving | Python wrapper of Rust `serve --draw-file` + `prove` | `session(draw)` → record and proof files | 1 (retired by 2-4) |
| relay | Python, about 60 lines | the prover's TCP bytes ↔ frames | 2 |
| prover | Rust `flock-circuit prove`, unchanged | the live protocol (`Req` frames) | 2 |
| audit | Python (`one_stage.audit`) | `audit(verdict)` → audit record and profile | 1 |

## 2. Wire format

* **Framing.** One framing everywhere: an 8-byte big-endian length, then that many bytes
  (`run-model-draft-7bd6:exe/RunModel/Frame.lean`). Each request carries a reply bound, and the program refuses a frame
  longer than its bound before reading it.
* **Bodies are canonical bytes, with one Lean reader each.**
  * Requests to and answers from workers are canonical JSON (`Flock.canon`: compact, sorted keys, integers only). The
    program re-canonicalises each answer and refuses any answer that is not already canonical, so a worker cannot slip
    two encodings of one value past it.
  * Live-protocol frames (PR 2) are Rust's `Req`/`Resp` encodings as they are: tag byte, u32 little-endian integers,
    u32-length-prefixed byte strings. One Lean reader and writer, `FlockAudit/Wire.lean`, is pinned by vectors that
    Rust's `Req::encode` writes. The Rust prover stays unchanged.
* **No trusted second parser.** The program never acts on a value that a worker parsed for it. Files are read by
  content key and parsed by the verifier's own readers (`HmRow.parse`, `loadPublic`, `Record.decode`).

## 3. Where the code lives under the ruling

* **The program.** A new lib `FlockAudit` and exe `flock-audit` in the verifier's Lake package
  (`backends/flock/verifier/lean/`), beside `Flock` and `Main`. They reuse `Flock.Draw`, `Flock.Zk` and `Flock.Record`,
  and change neither `Flock/*` nor `Main.lean`.
  * The verifier of record's acceptance stays untouched while #1179 (fail-closed) and #1192 (canonical V1) change it.
  * `lean-audit.json` gains the `FlockAudit` root and its `partial def`s (the frame and worker loops) under `escapes`.
* **`Prog` and `Frame`.** They live in `FlockAudit/` until a second party's program needs them. Then they move to the
  draft's `primitives/<p>/lean/` (decision D2).
* **Workers.** Under `backends/flock/verifier/workers/` as Python, with the run's copy of a0's flow in
  `benchmarks/one_stage/a0_lean.py`. Neither imports `Security/` or `FlockSoundness`; the analysis never runs.
* **Protocol packages.** These import only the stdlib, `verity` and themselves, so the Flock auditor stays with Flock.
  The one-stage protocol's own logic (`verity.protocols.verification.sampled_proofs.one_stage`) is unchanged.

## 4. Assumptions: which leave, which arrive

**Leave:**

* **`DrawFileZK dj law pop` (PR 1).** The run instantiates `dj S := (drawOf law pop S).toJson`, which is what the program
  sets up at. The hypothesis `hdj : ∀ S, dj S = (drawOf law pop S).toJson` then holds by the program's definition.
  `drawFileZK_of_toJson` (stratified) and `drawFileZK_of_toJson_subset` (subset, used by `zk_session_soundJ_custody_json`)
  already prove `DrawFileZK` from it, on main in `Discharge/ZkLink/DrawOkJson.lean`. `RecordCustodyZK` shrinks to
  `RecordsLiveZK`.
* **The record-carries-the-draw conjunct of `RecordsLiveZK` (PR 1).** `recordDraw (wr S R o).record = some (dj S)`
  becomes a check: the program refuses any other record (U1 against its own draw).
* **A6, `uniform/flock-coin-server` (PR 3).** The tree's key, coins and salts come from the program's `coins` nodes,
  which are A3. Two more facts are needed: the tree's binding, which follows from `cr/sha-512` (already assumed), and
  hm96's hiding hybrid for the zero-knowledge statements, `N·2^-256` with N = (1+2J)·256 (decision D4).
* **The rest of `RecordsLiveZK` (PR 4).** That the proofs and rounds in the record are the live session's becomes a
  theorem: the record the program renders is a function of `Prog.replay`'s transcript.

**Arrive.** Each is listed with what it already shares with today's verifier:

* **A3 covers more bytes.** The `Prop` is the same, with a larger `Lb`: per session, 256 B of key, 3·256·512·16 B =
  6.29 MB of coins and 3·256·192 B of salts, as Rust's /dev/urandom draws today.
* **Lean's compiler and runtime.** These are already trusted, since the verifier of record is a compiled Lean
  executable. The new parts of the runtime surface are `IO.Process.spawn`, pipe reads and writes, and `Task.spawn` if the
  tree is built in parallel. This can be named once, `lean/compiled-runtime`; it is not new in kind.
* **The interpreter adds no assumption.** `Prog.run` with a recording `Io` produces a transcript on which `Prog.replay`
  returns the same verdict. This is a theorem over an abstract `Io`, stated and proved in PR 1. Worker answers are
  adversarial bytes in the model, so no fact about the workers is needed.
* **The frame reader adds no assumption.** Its obligations are that it returns at most `max` bytes, that
  `Frame.decode (Frame.encode b) = b`, and that it reads each reply only from that request's worker. All three are
  provable. A reader bug can only choose answer bytes, which the adversary chooses anyway.
* **Process isolation is the same assumption as today.** No worker writes the program's memory or another worker's pipe.
  Today's model already needs the live verifier's process to be separate from the prover's. Workers run as separate OS
  processes, with no shared memory.
* **Liveness only.** A worker that never answers stalls the run. There are no timeouts, because no test depends on wall
  time; an operator kills the run, and the verdict is refused.

## 5. The statement and the proofs to change

These are scheduled by the coordinator after #1179 and #1192 land; none of them is in PR 1.

* **`FailClosed/One.lean` (#1179's `flock_verify_sound`).** `SoundZ` and `SoundZJ` (and `SoundZH`/`SoundZHJ`) quantify
  over `dj`. For the run, `dj` becomes the program's `fun S => (drawOf law pop S).toJson`, and the `RecordCustodyZK`
  hypothesis becomes `RecordsLiveZK` alone.
  * The J-table subset case is `zk_session_soundJ_custody_json`, which exists on main.
  * The one-table stratified case needs its sibling, built from `drawFileZK_of_toJson` (a few lines in
    `Composed/Custody.lean`).
* **The run's statement.** The accepted verdict is `flock-audit`'s rather than `flock-verify verify`'s. The draw in
  `Law.execOS src law pop` is the program's (`drawWith` at `IO.getRandomBytes`), under A3 as today.
* **After PR 3.**
  * A6 leaves `ASSUMPTIONS.md`.
  * `ViewZ`/`ViewZHJ` take hm96's hiding (D4).
  * The coin tree's binding, the root fixing every coin before any message, is proved from `cr/sha-512` as a theorem
    about `FlockAudit.CoinTree.check (build k c s) = ok`.
* **After PR 4.** The `hRec : RecordsLiveZK I dj wr` hypotheses of `SoundZ*` are discharged by
  `records_live_of_program` (`wr` defined from `Prog.replay`), and `RecordCustodyZK`/`RecordCustodyZKJ` retire from
  `Assumptions/Zk.lean`.
* **Proofs that change.**
  * `Composed/Custody.lean`, `CustodyJ.lean` and `CustodyJJson.lean` become callers with `hdj := fun _ => rfl`.
  * `Assumptions/Zk.lean` changes as above.
  * `FailClosed/One.lean`'s `SoundZ*` hypotheses change.
  * `ASSUMPTIONS.md` rows change.
  * The `lean-audit.json` pins of those theorems change. Each changed record needs a named statement reviewer.

## 6. Measured cost per session against its rounds

The session is fixture `sessions/drawn/l0000-1401916` (RoPE d64, subset 16 of 32, `--zk`, one table):

* 2 reps × 100 rounds;
* 195,168 B of round content, the largest round 22,064 B;
* two proofs of 865,130 B;
* the server's `handle_s` 0.694 s, and Lean's `verify_s` 0.461 s;
* about 210 requests per session.

| cost | measured | per session | against |
|---|---|---|---|
| a frame, Lean ↔ Python pipes (draft, 4-core VM) | 8 B 9.4 µs median (p99 13 µs); 64 KiB 37 µs; 2.5 MiB 2.9 ms | about 200 × 20 µs + 2 × 1 ms ≈ **6 ms** | 0.694 s server: <1% |
| the unit draw (`drawWith` over `coins`) | one `getRandomBytes` of 2k·width+64 bytes | well under 1 ms | — |
| coin randomness from `getRandomBytes` | 6.29 MB in 24 ms (this VM) | **24 ms** | — |
| Lean coin tree at `Hello`: 3 streams × 256 rounds × 513 chain SHA-512s = 393,984 calls of about 137 B | pure-Lean `Flock.Sha512.hash`: 7.4 µs/call single-threaded (**2.92 s**); 4 `Task.spawn`s **0.75 s** (1.9 µs/call) | **0.75 s on 4 cores** | 0.694 s server today: the tree roughly doubles the verifier side's time |
| leaves and nodes (768 hm96 leaves, about 1.5K nodes) | about 4 SHA-512s per leaf | about 25 ms | — |
| round openings (check the prover's path, PR 3) | (rounds_log + streams_log) + 2 SHA-512s per round | 200 × about 12 × 7 µs ≈ 17 ms | — |

The bench is a scratch Lean exe on `Flock/Hash.lean` (`for` over 768 blocks of 512 coins, chain as in `coin_tree.rs`);
the code is not committed. The tree's 768 chains are independent, and four tasks gave 3.9× on four cores, so it scales
with a pod's cores. That remains the one non-negligible cost, and it is D3.

## 7. Order of PRs

1. **`FlockAudit` with the unit draw** (this lane, `cursor/lean-drives-1-95d4`). It contains:
   * `Prog`, `Frame`, `Worker`;
   * the auditor (`register`, one draw, `session`, setup at its own draw, U1 against its own, `Zk.verify`, verdict);
   * the `flock-audit` exe;
   * the developer, serving and audit workers;
   * `benchmarks/one_stage/a0_lean.py`.

   Its tests: the honest run accepts; a second draw is impossible by construction (a theorem that the post-draw program
   has no coin node) and a worker asking for one is refused; a tampered answer (a record at another draw, a renamed
   file, an over-long or non-canonical frame) is refused. It removes `DrawFileZK` for that flow.
2. **The live wire in Lean.** `FlockAudit/Wire.lean` (the `Req`/`Resp` codec, pinned by Rust-written vectors) and the
   relay worker. The program sees every frame. In this PR the Rust server still serves the coins, as a worker it relays
   to, so A6 stays.
3. **The coin tree in Lean.** `coin-tree/hm96-sha512/v2`'s build, open and check, cross-checked against
   `coin_tree.rs` on vectors with a fixed tape. The program answers `Hello` and every `Round` itself, and A6 leaves.
4. **The record from the program.** The program renders `session.json` from its transcript, and `flock-verify verify`
   accepts it (a cross-check against the verifier of record). `RecordsLiveZK` becomes a theorem.
5. **Statement PRs** (scheduled by the coordinator after #1179 and #1192):
   * (a) `SoundZ*` at `dj` = the program's draw, with `RecordCustodyZK` → `RecordsLiveZK`, as soon as PR 1 lands;
   * (b) A6 and `hRec` out, after PRs 3-4.

## Decisions for Daniel

None of these blocks PR 1; each has a recommendation.

* **D1, placement.** `FlockAudit` and `flock-audit` as a new lib and exe in the verifier's Lake package, beside and not
  inside the verifier of record, or a new Lake package under `backends/flock/audit/lean/` that requires the verifier by
  path. **Recommend the same package**: no Lake plumbing, the audit covers it through one more root, and `Flock/*` and
  `Main.lean` stay untouched.
* **D2, `Prog`/`Frame`.** Keep them in `FlockAudit/` until a second party's program needs them, or move them now to
  `primitives/run/lean/`. **Recommend waiting.**
* **D3, the coin tree's cost** (0.75 s per session on 4 cores in pure Lean). The options:
  * (a) pure Lean, parallel over streams and rounds, accepting the cost;
  * (b) an `@[extern]` native SHA-512, which is faster but adds trusted C, checked only by vectors;
  * (c) a coin-tree v3 sized to the session's actual coins per round rather than a 512-coin block, which is a spec
    change on both sides.

  **Recommend (a)** for PR 3, measured on node 1's cores, with (c) revisited only if sessions get shorter than the tree.
* **D4, hm96 hiding.** The hybrid step (`N·2^-256`, N = (1+2J)·256) stays argued by hand in the ZK statements' docs, or
  becomes a named `Prop` in `Assumptions/Zk.lean` that `ViewZ*` take as a hypothesis. **Recommend the named `Prop`**: it
  is what the run then rests on in place of A6, and naming it lets `tools/lean/upstream.py` watch for a proof.
