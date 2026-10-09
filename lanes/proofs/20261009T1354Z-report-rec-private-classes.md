---
id: proofs/20261009T1354Z-report-rec-private-classes
campaign: private-circuit
lane: proofs
kind: report
status: done
repo: verity
origin: [agent:bc-ab22ea8f-7188-52ea-b8be-e580764a0419]
---


# rec-private: the private-circuit recursion, run of record (lane rec-v0)

For the proofs coordinator (bc-8416bc72). Times are Pacific (PDT); machine stamps stay UTC.
Status: done at 6:10 AM PDT (13:10Z). Every run below has finished.

## Outcome

**Lean accepts the recursion in both classes.** For the small class `UniversalUnit_v1{16,16,8}` (64 instances) and the
large class `UniversalUnit_v1{1024,1024,512}` (8 instances), Lean's `flock-verify verify --zk` accepted all six of V*'s
statements (L0, L1, L2, L3, alg-p0, alg-p1). Each was proved behind the outer firewall as a part of one recursive session,
the firewall released each part, and Lean's core-firewall accepted each release. `lean_of_record` is **accepted** in
both runs, with nothing refused.

`cursor/zk-shared-rows-95d4` moved after the runs started (`b1b604bd7` to `41ada9c94`, which merges main, including
main's new `RecResiduals.check`). I merged it and re-verified every recorded outer session with the Lean that tree builds
(`r20261009-124326-6c83`). Each part of both classes gets the verdict it got in its own run, honest parts and cheating
provers alike.

**One form is refused, and it is the real class's.** That same Lean refuses V*'s algebra parts of a 12-claim statement,
which is the layout of the real class's staging (`stage_class.py`: the unit as the program's one Call, 5 regions).
On the 16,16,8 validation of that path, alg-p0 and alg-p1 are refused at setup:
`circuit rec-residuals/m25-k22-c12-p0: unit rec-residuals/m25-k22-c12-p0: residual 16 alone reads more than 64 regions
or 128 sha512x3 slots`. Its L0–L3 are still accepted. V*'s Python cuts parts at `rec_residuals.MAX_SLOTS = 160`, which is
enough for the 12-claim algebra's widest residual (130 slots), while Lean's `RecResiduals.MAX_SLOTS` is 128. I widened
nothing. Both classes of record use the program-row layout (3 regions, 8 claims), which Lean accepts.

**Four of the five cheating provers are refused by Lean at a named check**, never at the form refusal, and counted
`caught`. The fifth, a private circuit outside the class, is accepted, as predicted: that is finding (b).

| cheating prover | where Lean refuses it | the check |
|---|---|---|
| (a) faulty unit, prover's self-check skipped | alg-p0 | `zk inner: the batched constraint fails (⟨c, Y⟩ ≠ t + β τ)` |
| (b) a description outside the class | nowhere: alg-p0 and alg-p1 accepted | finding (b) |
| (c) a description that doesn't open the registration ("other") | alg-p0 | `zk inner: the batched constraint fails` |
| (d) an inner message that doesn't open its salted commitment (flipped top) | L1 | `setup: registered reads: port out: table row 0 does not open rec-top-L1's registered root at position 0` |
| (e) other coins | alg-p0 and alg-p1 | `zk inner: the batched constraint fails` (both parts) |
| extra: level-3 forged top | L3 | `opening: ring-switch claim 12 mismatch` |
| extra: the wired cheater (layer 1 reads a made-up input) | V*'s fold, `InnerFold.lean --program` | `setup: links: cut wire [240, 248) from unit 0 to unit 8: the reader's row p1 is not the writer's committed output row (their b ‖ c differ)` (large: `[30720, 31232) from unit 0 to unit 2`) |

Every row holds in both classes, at the same check.

For (a) and (c), alg-p1 is accepted on its own: those cheaters' nonzero residuals all fall in part 0. A verifier that
accepts only when every part is accepted refuses them at p0, which is how `rec_private_summary.py` now counts a cheating
prover (`cheaters`: caught when any of its parts is).

**The ZK server's two tests pass in both runs.**
- A coin that doesn't open the challenger's commitment is refused. Lean's firewall contract, on the run's own transcript
  with one coin swapped, gives `circuit/rep0 round 1: coins that do not open the challenger's commitment`; the honest
  transcript is accepted. The firewall's case suite (28 challengers) agrees with its contract on every case.
- No salt is used twice across the firewall record. The small run has 797 distinct of 797 salts and coin openings (604
  tape salts, 193 coin openings), and the large run 805 of 805 (608 and 197). The pads are distinct too: 3,744 of 3,744
  in each run.

**Overhead against the same private circuit proved directly with C-Flock `--zk`** (Lean accepts that too):

| | small class (16,16,8) | large class (1024,1024,512) |
|---|---|---|
| direct: prove | 1.16 s | 1.02 s |
| direct: proof | 1,664,228 B | 1,722,004 B |
| direct: Lean verify | 15.7 s | 15.7 s |
| recursion: inner + outer prove | 98.2 s (85×) | 130.7 s (128×) |
| recursion: also V*'s staging and fold | 700 s (600×) | 913 s (895×) |
| recursion: outer proofs | 12,239,320 B (7.4×) | 12,255,832 B (7.1×) |
| recursion: Lean verify, six sessions | 507 s (32×) | 488 s (31×) |

The baseline was proved again on the merged tree (`r20261009-124351-9216`), and Lean accepts it there too.

**The real class** (F32MulFtz_v3 at {8090,64,32}): 87 now takes `STAGED=` of that staging's layout. It ran end to end at
16,16,8, and the Lean of the runs accepted all six parts. The Lean of the merged tree refuses its two algebra parts, as
described above. The command is in "The real class". Its registration salts are not OS draws: they are SHAKE-256 of one
key drawn once from the OS (`secrets.token_bytes(32)`) and never recorded. Neither the staging run nor its directory is
on node 1, so I could not check them.

## Runs (vy-nebius-1, `research run`, all PRESERVED)

| run | art | what |
|---|---|---|
| `r20261009-111638-6720` | `art:72e5b7387b344e56d44f7c542eeb220c010b5c14ffd3417294e919b22696f4ff` | **small class, run of record**: `87-rec-private.sh CLS=16,16,8 N=64` at `73c8c10b7`, every part behind the firewall, every control (1:07:30 wall) |
| `r20261009-111658-80e4` | `art:90d88fcf0cd5697ad12b22c3283c9b8dc6cc0dda405e93861b3744a9b85ee508` | **large class, run of record**: `87-rec-private.sh CLS=1024,1024,512 N=8 NW=2` at `73c8c10b7`, the same (1:40:05 wall) |
| `r20261009-123531-477c` | `art:c61fd3f95b66921c0a4f6c2b950a0a6ccb5c9d3005494bddac8e90f0dd1a89af` | the baseline: `91-rec-private-baseline.sh` at `c95435dee`, each class's private circuit as a public circuit, C-Flock `--zk`, Lean accepts |
| `r20261009-114213-2f10` | `art:9922a39246fc967d74c5dc2a63949d3c5bce8e4924a2b4c3a4ada306e5e3ce73` | the real class's path at 16,16,8: `stage_class.py` (the F32MulFtz staging's script), then `87 STAGED=` (single statement, 12 claims); the Lean of the runs accepts all six parts |
| `r20261009-124326-6c83` | `art:3557f92d14d613bc9bce7ce496b62fec5e6a84485db1ab877dee7a8338a6971e` | `92-rec-private-reverify.sh` at `932fcb4db` (zk-shared-rows `41ada9c94` merged): that tree's Lean on the three runs' recorded outer sessions |
| `r20261009-124351-9216` | `art:b286d051959347427ff4832059cc53cdd2e1c2466b10002808b961104897e310` | the baseline again at `932fcb4db`: Lean accepts both classes |
| `r20261009-113241-4025` | `art:de3f62565c1f3d56e89e830442c86ec8ba183b87332fb5c75a4858727d00b401` | first baseline: Lean refused at `partition: the circuit's template unit-class/…-packed is not one the query lists` (fixed in `bfcae3588`) |
| `r20261009-123213-91f3` | `art:ba5d8732c7aae52422667f9338267c5fd337fa540d0bcc5eb107e5ddd182b380` | second baseline: Lean refused `a shared-row public file (header shared_rows)` (fixed in `c95435dee`) |

## Verdicts per part

Both classes, honest, each part behind the outer firewall as part of recursive session `r0000`:

| part | statement | firewall | core-firewall | Lean `verify --zk` | live build |
|---|---|---|---|---|---|
| L0 | `RecOpen_v4{LANES=64,H=8}` ×436 | release | accept | accepted | accepted |
| L1 | `RecOpen_v4{16,7}` ×212 | release | accept | accepted | accepted |
| L2 | `RecOpen_v4{16,5}` ×142 | release | accept | accepted | accepted |
| L3 | `RecOpen_v4{16,4}` ×106 | release | accept | accepted | accepted |
| alg-p0 | `InnerRepCheck_v2` ×2 (residuals 0–9) | release | accept | accepted | accepted |
| alg-p1 | `InnerRepCheck_v2` ×2 (residuals 10–12) | release | accept | accepted | accepted |

Lean's partition note for each, for example L0: `units derived: Q_template_instance v0 over the verifier's program (436
units); the statement's 436 units are instances of RecOpen_v4{LANES=64,H=8}`. Each session carries the verifier's draw
(`--draw subset:N`, every unit), since Lean refuses a session without one (D12).

The inner statement itself (plain leaves) stays out of Lean's scope, as designed: `verify` refuses it at setup with
`verity/flock-circuit+plain-leaves … a form the soundness proof does not cover yet`. V* is its verifier: `rec_vstar`
accepts the inner session and `InnerFold.lean` folds it (exit 0).

V*'s staging over each cheating prover's session (the algebra's residuals, part by part, rep 0 and rep 1), the same in
both classes:

| cheating prover | p0 nonzero residuals | p1 nonzero residuals |
|---|---|---|
| (a) faulty | [1, 8, 9], [1, 8, 9] | none |
| (c) other | [6, 7], [6, 7] | none |
| (e) other coins | [0] in rep 0 | [0, 1] in rep 0 |
| (b) outside | none | none |

### The cheating provers, as built

- **(a) Faulty unit.** `rec_inner.py faulty`: instance 0's output row one bit off in the prover's file. The inner prover
  checks nothing; the outer sessions are sent though the witness fails (`FC_ZK_SELF_CHECK=skip`).
- **(b) Outside the class.** `rec_inner.py universal --outside`: a description whose gate reads a wire computed after it
  (small: gate 1 reads wire 31, which gate 15 computes; large: gate 0 reads wire 2047, computed by gate 1023). The
  universal unit evaluates gates in order, so it reads that wire's value before it is computed, and the description
  runs as some member of the class. Its outputs differ from what the description means in 33 cases (small) and 3 (large).
  Registered as its own statement, every check passes. **Finding (b):** every description of the class's width is a
  member of the class, so "a private circuit outside the class" is not a statement any verifier here can refuse. The
  class has to be defined as "any description of this width, read in gate order", or the description needs a
  well-formedness check that the unit proves.
- **(c) Other.** The registered private circuit with an unread no-op gate changed, so its outputs are the same and only
  the circuit's description differs. Proved against the registered statement.
- **(d) Flipped top.** `rec_inner.py forge --what top` (`circuit/rep0` round 60's top 0). V*'s reference and checked
  staging refuse it by name: `FIREWALL-REFUSED: tree top: … does not open its commitment`. A prover that skips its own
  top checks (`rec_inner.py flipped`) stages level 1, which Lean refuses at its registered reads.
- **(e) Other coins.** `rec_inner.py forge --what challenge` on a copy of the honest session: rep 0's first challenge coin
  one bit off, in the session and in the coin record alike.

## The ZK server's tests

- **Coins that don't open the commitment** (`rec_private_coins.py`, the firewall's Lean contract `flock-firewall`):
  - the run's honest transcript: accepted, 996 items released (large: 1,008);
  - the same transcript with `circuit/rep0` round 1's coin swapped: refused, `circuit/rep0 round 1: coins that do not
    open the challenger's commitment` (136 items released before it; 193 rounds committed).
  - `firewall_agree.py --cases`: 28 challengers, the live firewall and its contract agree on all, no misses.
- **No salt used twice** (`rec_private_summary.py` `salts`, over the firewall's transcripts: the inner session and the six
  outer parts):

  | run | tape salts | coin openings | pads | salts and openings together |
  |---|---|---|---|---|
  | small `6720` | 604 / 604 | 193 / 193 | 3,744 / 3,744 | 797 / 797 |
  | large `80e4` | 608 / 608 | 197 / 197 | 3,744 / 3,744 | 805 / 805 |
  | real-class path `2f10` | 608 / 608 | 197 / 197 | 3,736 / 3,736 | 805 / 805 |

  (distinct / total.)

## Costs and overhead

### Small class (`r20261009-111638-6720`, 32-CPU slice)

- Universal staging 0:29.8 (0.57 GB). Inner session (CPU): 1.98 s to prove (two reps), wall 0:03.65, 1.53 GB peak; proof
  2 × 531,938 B. Fold (`InnerFold.lean`) 9.6 s. V*'s staging (`rec_vstage stage`) 9:51.9 at 12.45 GB.

| part | k_log | prove s | prove wall | proof B (2 reps) | peak GB | live verify s | Lean verify wall |
|---|---|---|---|---|---|---|---|
| L0 | 24 | 33.67 | 0:55.3 | 2,176,820 | 36.4 | 1.92 | 1:47.8 |
| L1 | 23 | 9.27 | 0:20.6 | 2,044,228 | 11.8 | 0.85 | 1:05.3 |
| L2 | 23 | 9.74 | 0:19.0 | 2,044,228 | 11.5 | 0.91 | 0:54.2 |
| L3 | 23 | 6.82 | 0:15.2 | 1,926,196 | 7.2 | 0.78 | 0:50.0 |
| alg-p0 | 26 | 18.41 | 1:00.5 | 2,056,948 | 22.5 | 5.02 | 1:57.2 |
| alg-p1 | 26 | 18.31 | 0:58.8 | 1,990,900 | 22.4 | 4.27 | 1:52.7 |
| **total** | | **96.22** | **3:49.5** | **12,239,320** | 36.4 (max) | **13.76** | **8:27.2** |

### Large class (`r20261009-111658-80e4`)

- Universal staging 2:00 (5.2 GB). Inner session: 4.06 s to prove (two reps), wall 0:20.3, 5.26 GB; proof 2 × 532,002 B.
  Fold 1:40.9 (it reads the 774 MB inner circuit). V*'s staging 11:21.6 at 12.47 GB.

| part | k_log | prove s | prove wall | proof B (2 reps) | peak GB | live verify s | Lean verify wall |
|---|---|---|---|---|---|---|---|
| L0 | 24 | 47.44 | 1:11.4 | 2,176,820 | 36.6 | 2.14 | 1:42.9 |
| L1 | 23 | 15.07 | 0:26.5 | 2,044,228 | 11.9 | 0.96 | 1:03.4 |
| L2 | 23 | 11.89 | 0:22.7 | 2,044,228 | 11.6 | 0.93 | 0:51.4 |
| L3 | 23 | 8.50 | 0:17.4 | 1,926,196 | 7.2 | 0.88 | 0:47.9 |
| alg-p0 | 26 | 21.35 | 1:05.7 | 2,073,460 | 22.6 | 5.35 | 1:53.0 |
| alg-p1 | 26 | 22.41 | 1:06.3 | 1,990,900 | 22.5 | 5.24 | 1:49.4 |
| **total** | | **126.66** | **4:30.1** | **12,255,832** | 36.6 (max) | **15.50** | **8:07.8** |

### The baseline (`r20261009-123531-477c`): the same private circuit, proved directly

`rec_inner.py direct`: the registered private circuit (same description, same x) as a public Boolean Definition, its
`n` instances one batch (`population_program`) under `Q_template_instance`, staged by `class_statement.stage` with
C-Flock's salted leaves, every row an instance's own and every salt from the OS; one `--zk` session with the verifier's
draw. Lean `verify --zk`: accepted (`units derived: … 64 units … instances of RecPrivateDirectG16N16O8S0_v1`), and the
live build accepts.

| class | instances | ANDs a unit | k_log, m | prove s (2 reps) | prove wall | proof B | live verify s | Lean verify wall |
|---|---|---|---|---|---|---|---|---|
| 16,16,8 | 64 | 2 | 22, 26 | 1.16 | 0:04.4 | 1,664,228 | 0.40 | 0:15.7 |
| 1024,1024,512 | 8 | 173 | 22, 25 | 1.02 | 0:04.6 | 1,722,004 | 0.50 | 0:15.7 |

A unit computes only the private circuit's outputs that aren't input bits, pruned to what they read: 2 ANDs (small, a
description of 8 ANDs) and 173 (large, 406). The universal unit that hides the description is 1,066 and 4,203,010 ANDs.

### Overhead

| | small | large |
|---|---|---|
| prove, inner + outer, against direct | 98.2 s / 1.16 s = **85×** | 130.7 s / 1.02 s = **128×** |
| prover side with V*'s staging and fold | 700 s = **600×** | 913 s = **895×** |
| proof bytes (V*'s six proofs) | 12.24 MB / 1.66 MB = **7.4×** | 12.26 MB / 1.72 MB = **7.1×** |
| Lean verify (six sessions, serial) | 507 s / 15.7 s = **32×** | 488 s / 15.7 s = **31×** |
| live verify | 13.8 s / 0.40 s = 34× | 15.5 s / 0.50 s = 31× |

V*'s staging (Python) dominates the prover side: 85% of it in the small class and 75% in the large. Its cost is set by
the inner session's m (27 in both classes), not by the class: V*'s four RecOpen circuits are byte-identical across the
two classes, and so are their proofs' sizes.

## Components

| component | where | language | who trusts it |
|---|---|---|---|
| inner prover | M0 `flock-circuit prove` (`verity/ml/flock/live`), `FC_COINS=os`, plain leaves | Rust | only the prover, for its own hiding; its proof is V*'s witness, checked by V* |
| ZK server and firewall | `verity_flock.rec_live` (the proxy and the challenger's coin server), `verity_flock.firewall`; the release of record `verity/ml/flock/live/src/release.rs`; its contract `flock-firewall` and the release decision `core-firewall` (`verity/core/service/firewall`) | Python, Rust, Lean | the prover, for hiding: nothing leaves unless the firewall releases it; the Lean contract and core-firewall recheck its decisions, outside the soundness theorem |
| V*'s builder | `verity_flock.rec_vstage`, `rec_shape`, `rec_residuals`, `rec_outer` | Python | the verifier, with no theorem covering it: Lean checks the statements it builds (`RecOpen.check` holds a `rec-open/…` unit to the verifier's net; after the last merge `RecResiduals.check` does the same for a `rec-residuals/…` unit) |
| `InnerFold.lean` | `verity/ml/flock/tests/lean/InnerFold.lean`, test-side | Lean | the verifier: it computes V*'s claims and each rep's comb from the inner session, outside every theorem |
| outer prover | M0 `flock-circuit prove --zk` behind the firewall | Rust | the prover, for zero knowledge |
| Lean verifier of record | `flock-verify verify --zk` (`verity/core/service/flock`), proved by `flock_verify_sound` (`Security/Proofs/Flock/Soundness/Discharge/FailClosed/One.lean`) | Lean | the verifier, proved sound for everything it accepts |
| stager | `rec_inner.py universal` (`verity_flock.universal_stage`, `class_statement.stage`); for the real class `benchmarks/private_circuit/stage_class.py` | Python | the prover (it commits the registration); the verifier trusts only the registered root |
| challenger | the coin server in `rec_live`: coins from `os.urandom`, each committed (`hm96.fresh_salt` salts) before the prover's message | Python | the verifier's randomness |

## `lean_of_record` per run

| run | lean_of_record | parts | controls caught |
|---|---|---|---|
| small `6720` | **accepted** | L0–alg-p1 accepted, none refused | forged-top, flipped-top, other, faulty, other-coins; outside accepted (b) |
| large `80e4` | **accepted** | L0–alg-p1 accepted, none refused | the same as the small run's |
| real-class path `2f10` (16,16,8, `CONTROLS=0`) | **accepted** by the Lean of the run; the merged tree's Lean refuses alg-p0 and alg-p1 (128 slots) | L0–alg-p1 accepted | forged-top, flipped-top, other-coins contract |
| old run 5 `r20261009-081632-94d3` | **not accepted** | L0 `Lean refused: form not covered`; L1–alg-p1 `Lean: no verdict` (the firewall stopped the session at L0) | flipped-top-L1, forged-top-L3, other-alg-p0 caught; other-alg-p1 the form refusal |

Old run 5, read by today's `rec_private_summary.py`: `CHEATERS` forged-top, flipped-top and other caught (its three
controls, each refused at a named check before the form); `SALTS` 608/608 tape salts, no coin openings in its
firewall transcripts, 636/636 pads. Run 5 predates the shared-row registered form in Lean, which is
why its L0 was refused for its form.

## The real class

- **The staging.** `r20261009-071233-329e` was to stage `UniversalUnit_v1{8090,64,32}` (66,841,560 ANDs) with plain
  leaves into `/workspace/jobs/pc-stage/keep/F32MulFtz_v3/8090-64-32` on node 1. Neither that run nor the directory is
  on any machine research knows (`research inspect`, and probe run `r20261009-113443-0d2b`). The notes checkpoint says
  "full-class plain-leaves staging r20261009-071233-329e running (107 GB at 18 min, done ~10:25Z)". So I could not read
  it and did not wait on it.
- **Its salts.** From the code it ran (`benchmarks/private_circuit/stage_class.py` at `537059b83`, on
  `origin/cursor/universal-unit-staging-8c79`, still that branch's head): `salt_key = secrets.token_bytes(32)`, then
  `class_statement.stage(..., salt_key, packed=True)`. Every registration salt is SHAKE-256 of that one OS-drawn key,
  the set, the port and the row (`circuit.stage_salts` with a key); the key is never recorded. They are not per-salt OS
  draws, as our runs' are (`key=None`). Assumption 2's gap covers both.
- **Its layout.** The unit itself as the program's one Call (no program row): 4 input ports, so 5 regions and 12 claims,
  and `circuit.txt`, `inst-N.bin`, `pub-N.bin` in the directory, with no partition object and no other statement.
- **87 takes it** (`5b008a0b9`): `STAGED=DIR` with `DIR/circuit.txt` links the statement in, builds the partition object
  the circuit binds (`rec_inner.py partition`, refusing a digest that differs), reads N from `pub-N.bin`, and folds the
  cap from the honest session (no other statement). It ran end to end at 16,16,8 in `r20261009-114213-2f10`: cap
  `instances=8,claims=12,k_log=22,vus_per_block=1`, and the Lean of that run accepted all six parts.
- **The Lean of the merged tree refuses its algebra.** `RecResiduals.check` (from main, through zk-shared-rows
  `41ada9c94`) refuses alg-p0 and alg-p1 of that statement: `residual 16 alone reads more than 64 regions or 128
  sha512x3 slots`. The real class's staging has the same layout (12 claims), so the command below will reach the same
  refusal at its algebra parts, even though L0–L3 will be accepted. There are two ways out, and neither is mine to take
  today:
  - restage the real class with the program as one registered row (`rec_inner.program_unit`: 3 regions, 8 claims), as
    both classes of record are staged; or
  - Lean's `RecResiduals.MAX_SLOTS` becomes 160, like V*'s Python, but only once its proof covers 160 (the verifier gains
    no form ahead of its proof).
- **The command** (not run; 2 CPU slices, the wired section at a small class):

  ```
  research run --on vy-nebius-1 --project verity --source <a checkout of cursor/rec-private-0419> --cwd source --timeout 12h \
    --campaign private-circuit -- bash verity/ml/flock/pod/87-rec-private.sh \
    STAGED=/workspace/jobs/pc-stage/keep/F32MulFtz_v3/8090-64-32 CLS=8090,64,32 CONTROLS=0 WCLS=16,16,8 NW=8 \
    TAG=f32mulftz-8090-64-32
  ```

  The inner session is about 2^26 rows an instance (k_log 27); the fold reads a circuit of roughly 12 GB, so that is
  the step to watch for memory.
- **Its direct baseline.** The other lane's `90-rec-stage.sh MODE=direct` (`rec_stage.py direct`, `1ed7592ed`) stages
  with `class_statement.stage` packed and shared rows, as my first baseline did. Lean will refuse that at the partition
  check, then at the shared-row form. `class_statement.stage(..., names_definition=True, share_rows=False)` with a
  population program (`c95435dee`) is the fix.

## Gap list

1. **Assumption 2: V*'s outer leaf salts** are a ChaCha20 expansion of one fresh 256-bit OS key per proof (`zk_hooks.rs`
   `LeafSalts`), not uniform independent salts. No premise under `Security/` covers ChaCha20 as a PRG. Not changed in
   C-Flock, as asked. The registration salts are now OS draws in our runs (`rec_inner`, `key=None`), but the real class's
   staging derives them from one unrecorded key (SHAKE-256), which needs the same kind of premise.
2. **Finding (b):** every description of the class's width is a member of it (see (b)). A "private circuit outside the
   class" is accepted at every check.
3. **Part-wise acceptance.** A cheating prover whose residuals all fall in one part has its other part accepted on its
   own (other-alg-p1, faulty-alg-p1). The recursion needs every part accepted: in the run, the firewall's record (one
   recursive session, its parts in order) and `lean_of_record` (accepted only when all six are) enforce it. I did not
   check that rec-private-lean's statement reads acceptance the same way.
4. **V*'s builder and `InnerFold.lean` are outside every theorem** (components table). Lean holds each statement's unit
   to the verifier's net, but nothing proves the fold or the staging inputs are the inner session's.
5. **V*'s Python and Lean disagree on an algebra part's room.** Python's `rec_residuals.MAX_SLOTS = 160` and Lean's
   `RecResiduals.MAX_SLOTS = 128`. Statements at 8 claims fit both, but 12-claim statements (the real class's layout) are
   staged by V* and then refused by Lean. One of the two has to change; which one is the owner's decision.
6. **The live build's replay** of the inner session still says `a shared-row public file` (it has no `--registered`
   form for plain inner leaves); Lean is the verifier of record, so this is cosmetic.

## Code

Branch `cursor/rec-private-0419`, pushed, no PR. This round's commits:
- `586b83bc2` the baseline: `rec_inner.py direct` and `91-rec-private-baseline.sh`;
- `5b008a0b9` 87 takes `STAGED=` of a statement staged alone (`stage_class.py`'s layout) and `rec_inner.py partition`;
- `aba7649c1` `rec_private_summary.py`: `cheaters` (a cheating prover caught when any part is) and the wired cheater's
  fold refusal as a control;
- `bfcae3588`, `c95435dee` the baseline in the form Lean covers: `class_statement.stage` gains `names_definition` (META
  names the Definition, as a wired statement's does) and `share_rows` (False: every instance's rows its own);
- `da3fc03e4` merge of `cursor/zk-shared-rows-95d4` at `41ada9c94` (it moved from `b1b604bd7`, bringing main);
- `932fcb4db` `92-rec-private-reverify.sh`: Lean of this tree again on earlier runs' recorded outer sessions.
- Earlier this round: `e9883cfc8` (OS registration salts, `--outside`, `faulty`), `aedc3aff4` (merges), `73c8c10b7` (the
  controls, `rec_private_coins.py`, the salts check).

Tests: `verity/ml/flock/tests/test_rec_private.py`, 4 passed (two slow: two private circuits' public files compared; the
direct staging of the registered private circuit). `ruff check` passes on the changed Python.

New files to tell you about: `verity/ml/flock/pod/rec_private_coins.py`, `verity/ml/flock/pod/91-rec-private-baseline.sh`,
`verity/ml/flock/pod/92-rec-private-reverify.sh`; new subcommands `rec_inner.py direct` and `rec_inner.py partition`; 87's
`STAGED=` single-statement layout.

## Re-verification on the merged tree (`r20261009-124326-6c83`)

The Lean that `932fcb4db` builds (zk-shared-rows `41ada9c94` merged), on each part's recorded session and statement:

| run | parts | now, against the run's own verdict |
|---|---|---|
| small `6720` | all 16 (6 honest, 10 cheating) | the same verdict for every part: 6 honest accepted; faulty-p0, other-p0, other-coins-p0/p1, flipped-top-L1 and forged-top-L3 refused at the same checks; faulty-p1, other-p1 and outside-p0/p1 accepted |
| large `80e4` | the 14 recorded by 12:43Z (outside-p0/p1 came later) | the same verdict for every part |
| real-class path `2f10` | 8 | L0–L3, flipped-top-L1 and forged-top-L3 the same; **alg-p0 and alg-p1 now refused** (128 slots) |

Its Lean walls ran eight at a time on one 16-CPU slice, so they are not costs; the costs tables use each run's own
serial walls. `out/reverify.json` in the run holds every verdict.
