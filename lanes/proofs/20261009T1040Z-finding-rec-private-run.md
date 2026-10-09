---
id: proofs/20261009T1040Z-finding-rec-private-run
campaign: recursive-private-circuits
lane: proofs
kind: finding
status: open
repo: danielreuter/verity
origin: cursor/rec-private-0419 @ aa7d02088 (off main 56e4e65e8); runs r20261009-071837-ec42, r20261009-075410-8f0d, r20261009-081632-94d3
---

# rec-private: a hidden circuit description as the recursion's inner statement (lane rec-v0)

For the proofs coordinator (bc-8416bc72). Times are Pacific (PDT); machine stamps stay UTC.
Status: done at 3:40 AM PDT (10:40Z). The small class finished at 1:30 AM PDT (08:30Z); the large class (1024,1024,512),
the largest that fits C-Flock's format cheaply, finished at 3:22 AM PDT (10:22Z). The real class cannot be staged (see
"The real class").

## Outcome

The small class `UniversalUnit_v1{G=16,N_IN=16,N_OUT=8}` ran end to end on vy-nebius-1. A hidden circuit description was staged as
the inner statement. Its inner session went through the firewall, and V*'s fold and staging ran under the class's cap.
Each of V*'s six statements was proved with `--zk`, then verified by Lean `verify --zk` and the live build. **No
verifier accepts on main, and no run can make one accept.** Every V* statement reads registered values, so it is a
shared-row public file, and `Flock.ProvedScope` refuses that form. The honest result is therefore "every check passed,
refused for its form only", from both Lean and the live build, for all six statements. Because the firewall releases a
part only on an accepting verdict, the recursive session itself stops at its first part, L0.

All three controls (plus one extra) are refused by Lean at a check that runs before the form refusal. That is the
refusing stage the task asked for:

| control | Lean's refusal (stage) | live build (`without_refusal`) |
|---|---|---|
| a different circuit description of the class, V*'s algebra part 0 | `zk inner: the batched constraint fails (⟨c, Y⟩ ≠ t + β τ)` | the same |
| `--wired`'s cheater (layer 1 reads a made-up input) | V*'s fold `InnerFold.lean --program`: `setup: links: cut wire [240, 248) from unit 0 to unit 8: the reader's row p1 is not the writer's committed output row (their b ‖ c differ)` | `statement --links` refuses the public file before any session: `cut wire from instance 0's output row to instance 8's row p1 …` |
| `rec_inner.py forge --what top` (flipped tree top), level 1 | `setup: registered reads: port out: table row 0 does not open rec-top-L1's registered root at position 0` | `zk inner: the batched constraint fails` |
| (extra) `rec_vstage --forge top`, level 3 | `opening: ring-switch claim 12 mismatch` | `opening: RingSwitch(ClaimMismatch)` |

The large class `UniversalUnit_v1{G=1024,N_IN=1024,N_OUT=512}` (4,203,010 ANDs per instance, 3,943 times the small
class's) ran the same pipeline (run `r20261009-081632-94d3`) and gave the same result. Every honest statement was
refused for its form only, L0 was released by the firewall and then stopped the session, and each control was refused
at the same stage as in the small class.

Its costs are those of the small class. Both caps have inner m 27, so V*'s four RecOpen circuits are byte-identical
across the two classes, and the inner and outer proofs are the same size (except alg-p0's, 0.8% larger). G enters only
the prover's staging of the inner circuit and V*'s fold (see "Costs").

The real class, a 2^22-cell vLLM proof unit, gives a universal unit of 2^40.0 ANDs. That is about 2^14 times the most
C-Flock's circuit format holds per instance. See "The real class".

## Runs (vy-nebius-1, `research run`, all PRESERVED)

| run | art | what |
|---|---|---|
| `r20261009-071837-ec42` | `art:4bf2b4dab103bef15e262300b0bffabd77f5fd96c0c1c92475b2aad2164466b9` | `87-rec-private.sh CLS=16,16,8 N=64 NW=8` at `bf77df4bf`: staging, inner sessions, firewall, fold, V* staging, L0 behind the firewall, every control |
| `r20261009-075410-8f0d` | `art:452b10c907e84c379a6613027fb628a06dc24d17311468ab55ccc5bed4761071` | `89-rec-private-direct.sh` at `aa7d02088` on run 3's staging: all six honest V* statements proved outside the recursive session, L0's release rechecked by Lean's core-firewall, the two circuit descriptions' public views |
| `r20261009-082708-3a83` | `art:91ecc472738345642a79c40d302fa3c380d503f2ab18a35f1fcaff3a04c45818` | read-only: the unit header and META of the inner circuit and of every V* circuit (the scope rules after the shared-row refusal) |
| `r20261009-081632-94d3` | `art:4e556be877f61642f150d15b598ce79192e4cce1ad4d5ae1879aacd28aa3aadb` | `87-rec-private.sh CLS=1024,1024,512 N=8 NW=2` at `aa7d02088`, the largest class that fits: everything run 3 does, L0 behind the firewall, the five later parts direct, every control, the two circuit descriptions' public views (2:06 wall) |
| `r20261009-065306-f385` | `art:547fcc437d39c081c47fb4b7063f6faef86f0c1c905f98013b6bd53639abb3ae` | failed at the wired inner session (missing `--links`), fixed in `706459a06` |

circuit-check reports: `art:6a3f393b9d680431ae95f5f911152e01e32d7690664afec5245fed68a9f0a622`.
- `UniversalUnit_v1{G=16,N_IN=16,N_OUT=8}`: ok, 0 failures, 0 warnings.
- The program-row wrapper `ProgramRow[UniversalUnit_v1{…}]_v1` (`rec_inner.program_unit`, used unregistered): 0 failures, 1 unpinned warning.

Each run's `out/summary.json` (`rec_private_summary.py`) holds every verdict quoted here.

## The class and its sizes

- **Inner statement.** `program_unit(UniversalUnit_v1{16,16,8})`: a random circuit description of 12 gates (8 ANDs) over 12 inputs,
  padded to the class. The circuit description's `op`/`src`/`out` bits are one registered row that every instance opens; `x` is one
  row per instance; the outputs are hidden rows.
  - Instance shape: 64 instances, two per block (32 blocks); k_log 22, m 27, plain leaves (`flock-leaf/sha512-unsalted`).
  - Unit: 1,066 ANDs (equal to `and_count`), 3,329 rows, 17,848 nonzeros, one input group.
  - Files: circuit 55.65 MB, public file 28,418 B. Shared rows: `p0` (x) 64, `p1` (the program) 1, `out` 64.
- **V*.**
  - Cap: `instances=64,claims=8,k_log=22,vus_per_block=2`.
  - Statements: `RecOpen_v4{LANES=64,H=8}` ×436, `{16,7}` ×212, `{16,5}` ×142 and `{16,4}` ×106 (L0 to L3), and
    `InnerRepCheck_v2` ×2 for each algebra part (p0: residuals 0–9; p1: residuals 10–12).
  - Circuit sizes: 332, 216, 176, 158, 420 and 404 MB.
  - Every unit reads one input group, has no tail stage, has unit_log ≤ 22 and uses `hm96-sha512/row/v1` rows (run 3a83).
    So in these fields, the shared-row form is the only rule V*'s statements fail.
- **Wired.** Four layers of the same class, 8 instances each.
  - Topology: `c[0:16]`, `c[16:24] + u0[0:8]`, `u0[0:8] + u1[0:8]`, `u2[0:8] + c[24:32]`.
  - 32 links; 9,473 unit rows.

The large class, run 5:
- **Inner statement.** `program_unit(UniversalUnit_v1{1024,1024,512})`: a random circuit description of 768 gates (406 ANDs) over
  768 inputs, padded to the class (256 padding gates).
  - Instance shape: 8 instances, one per block; k_log 24, m 27, plain leaves.
  - Unit: 4,203,010 ANDs (equal to `and_count`), 4,251,649 rows, 93,592,652 nonzeros.
  - Files: circuit 774.1 MB, public file 5,522 B. Shared rows: `p0` 8, `p1` 1, `out` 8.
  - Hiding the circuit description costs 4,104.5 ANDs per gate of the class: about 2W per gate (a selector over W = N_IN + G =
    2,048 wires for each of a gate's two inputs). That is 10,352 times the circuit description's own 406 ANDs. The small class's
    overhead is 66.6 ANDs per gate.
- **V*.**
  - Cap: `instances=8,claims=8,k_log=24,vus_per_block=1`.
  - Statements: the same templates and instance counts as the small class: `RecOpen_v4` ×436, ×212, ×142 and ×106,
    and two `InnerRepCheck_v2` parts of 2 instances.
  - Circuits: L0 to L3 are byte-identical to the small class's (same sha512); the algebra parts differ, since they
    are built from the cap (421.6 and 404.4 MB, against 420 and 404 MB).
- **Wired.** Four layers, 2 instances each (8 units), 2,048 input bits; the circuit is 786.1 MB with 8 link triples.

## Verdicts

Honest, each V* statement proved outside the recursive session (run 4), and L0 behind the firewall (run 3):

| part | live (`without_refusal`) | Lean `verify --zk` | live replay |
|---|---|---|---|
| L0 (behind the firewall) | accepted, so every check passed | refused for its form only | the form refusal |
| L0, L1, L2, L3, alg-p0, alg-p1 (direct) | accepted (each) | refused for its form only (each) | the form refusal (each) |

The form refusal reads `refused: a shared-row public file (header shared_rows): a statement form the soundness proof
does not cover`. Lean puts it last, when nothing else fails; the live build always puts it in place of the reason and
keeps the real verdict in `without_refusal`.

Run 5 (large class) gives the same table: L0 behind the firewall and L1 to alg-p1 direct, each accepted by the live
build with the refusal lifted, refused for its form only by Lean, and the form refusal on replay. Its inner session
passed Lean's firewall contract on 1,008 of 1,008 items, and `rec_vstar` accepted it (896 queries, 160 message rows).
Lean's core-firewall accepted L0's release (1,910 items). The firewall record is the small class's: the session opened,
the inner part finished, L0 was stopped by the challenger's verdict, and L1 to alg-p1 were refused.

- **Inner session (run 3).**
  - V*'s reference `rec_vstar` accepts it: 896 queries, 156 message rows, plain leaves.
  - `InnerFold.lean` exits 0.
  - Lean `verify` of the inner statement itself refuses it at setup: `verity/flock-circuit+plain-leaves, a statement
    with plain SHA-512 leaves (flock-leaf/sha512-unsalted): a form the soundness proof does not cover yet`.
- **Firewall.**
  - The recursive session `r0000` opened with the parts L0 to alg-p1.
  - Lean's firewall contract (`flock-firewall`, `firewall_agree.py`) agrees with the live firewall on 996 of the 996 items
    the inner session released.
  - L0 behind the outer firewall: the send check passed and the proofs left. The challenger's verdict (the form refusal)
    made L0 the session's stop, and L1 to alg-p1 were each refused: `recursive session r0000 stopped at L0: the firewall
    serves nothing more of it`.
  - Lean's core-firewall (`verity/firewall-release/v0`) on L0's transcript and the record before it: **accept**
    (1,910 items, outer phase). This is the firewall's own decision before the send, so it agrees with the live record.
    (Run 3's own check was rejected on non-canonical params JSON; run 4 rechecked it after the fix in `bf77df4bf`.)

Controls (run 3), with what each one is:

- **A different circuit description.**
  - Construction: the registered circuit description with its last padding no-op gate changed to `(XNOR, 0, 0)`. Its outputs are the
    same, so only the program row differs. It was proved against the registered statement, and V*'s algebra was staged
    over its session at the registered statement's fold. The outer sessions were sent even though the witness fails
    (`FC_ZK_SELF_CHECK=skip`).
  - alg-p0: refused by both Lean and the live build, `zk inner: the batched constraint fails`.
  - alg-p1: passes every check. Its three residuals hold for this session. The algebra holds only when every part does
    (`rec_residuals.parts`), and the recursive session reaches p1 only after p0, so p0 is the refusing stage.
  - The live replay of this inner session against the registered statement also refuses it, at
    `record: R7: session parameters … differ from the verifier's`: the session parameters' link σ binds the public file.
- **The wired cheater.**
  - Construction: layer 1 reads a made-up input. Bits 8 and 16 are flipped; the wire is broken in 8 instances and the
    circuit's output is wrong in 6.
  - Both verifiers refuse it in Linking at setup (the table).
  - The honest wired statement passes the same fold (exit 0). Without the verifier's program, the fold refuses even the
    honest one: `setup: META links: Linking needs the verifier's own program and partition`.
  - This control's Lean refusal comes from V*'s fold (`InnerFold.lean`, the setup Lean's `verify` runs), not from a Lean
    `verify --zk` of an outer session: no V* statement is staged over a session that fails Linking.
- **The flipped top.**
  - Construction: `forge --what top`, `circuit/rep0` round 60's top 0.
  - V*'s reference and checked staging refuse it by name: `FIREWALL-REFUSED: tree top: circuit/rep0 round 60's top 0
    does not open its commitment`.
  - A prover that skips its own checks (`rec_inner.py flipped`) staged level 1, which Lean refuses at its registered reads
    (the table).
- **Replay.** For every control, the live replay's `UPSTREAM` line carries only the form refusal: `replay` in
  `flock-circuit.rs` drops `without_refusal`. A few lines would fix it. I left it, since it is C-Flock's Rust (rebuild,
  `lean-agreement`), and Lean and the `LIVE` line already name each refusing check.

Controls in run 5 (large class), each refused at the small class's stage:
- **A different circuit description.** V*'s staging finds its algebra failing (`rec_vstage` exits 1: p0's residuals 6 and 7 are
  nonzero in both reps, p1 holds). Then:
  - other-alg-p0: Lean and the live build give `zk inner: the batched constraint fails (⟨c, Y⟩ ≠ t + β τ)`.
  - other-alg-p1: passes every check, as in the small class.
  - The live replay of its inner session against the registered statement: `record: R7: session parameters … differ`.
- **The wired cheater.** Bits 512 and 1024 were flipped, so the wire is broken and the output is wrong in 2 of the
  8 units.
  - `statement --links`: `cut wire from instance 0's output row to instance 2's row p1 …`.
  - `InnerFold.lean --program`: `setup: links: cut wire [30720, 31232) from unit 0 to unit 2: the reader's row p1 is not
    the writer's committed output row (their b ‖ c differ)`, exit 1.
  - The honest wired fold exits 0 (2:25), and without the program it exits 1.
- **The flipped top** (`circuit/rep0` round 62's top 0, level 1).
  - Lean: `setup: registered reads: port out: table row 0 does not open rec-top-L1's registered root at position 0`.
  - Live: `zk inner: the batched constraint fails`.
  - `rec_vstar` and checked staging: `FIREWALL-REFUSED: tree top: circuit/rep0 round 62's top 0 does not open its
    commitment`.
- **The forged top, level 3.** Lean: `opening: ring-switch claim 12 mismatch`; live: `opening: RingSwitch(ClaimMismatch)`.

## Costs

### Small class

Inner session (run 3, CPU, honest): 1.19 s to prove (two reps, 0.64 s and 0.55 s; 1.32 s end to end); proof 2 × 531,938
= 1,063,876 B; prover peak 1.52 GB.

V*'s statements, each proved `--zk` (run 4, plain mode, 32-CPU slice):

| part | k_log | instances | prove s | e2e s | proof B (2 reps) | prover peak GB | live verify s | Lean verify wall | replay wall |
|---|---|---|---|---|---|---|---|---|---|
| L0 | 24 | 436 | 28.23 | 32.87 | 2 × 1,088,410 | 28.8 | 2.11 | 1:50.3 | 0:09.3 |
| L1 | 23 | 212 | 7.89 | 8.98 | 2 × 1,022,114 | 8.3 | 1.16 | 1:27.9 | 0:05.4 |
| L2 | 23 | 142 | 7.77 | 8.81 | 2 × 1,022,114 | 8.2 | 0.88 | 0:52.4 | 0:04.9 |
| L3 | 23 | 106 | 4.65 | 5.29 | 2 × 963,098 | 5.0 | 0.77 | 0:49.5 | 0:04.4 |
| alg-p0 | 26 | 2 | 11.87 | 12.86 | 2 × 1,028,474 | 13.5 | 5.50 | 2:40.2 | 0:24.6 |
| alg-p1 | 26 | 2 | 17.30 | 18.92 | 2 × 995,450 | 13.4 | 6.24 | 2:34.5 | 0:24.3 |
| **total** | | | **77.7** | **87.7** | **12,239,320** | 28.8 (max) | **16.7** | **10:14.7** | **1:12.7** |

- L0 behind the firewall (run 3): 34.84 s to prove (37.91 s end to end), peak 32.6 GB, Lean 1:39.7.
- Staging V* (`rec_vstage stage`, run 3): 10:48 wall at 12.45 GB, of which 178 s and 132.5 s build the two algebra
  circuits. The fold (`InnerFold.lean`): 10.3 s.
- Universal staging: 0:34. Wired staging: 0:42.

**Overhead against the inner session:**
- Proving: 65× (77.7 s vs 1.19 s).
- Proof bytes: 11.5× (12.24 MB vs 1.06 MB).
- Prover side including V*'s staging and the fold: about 620× (736 s vs 1.19 s).
- Lean's verification of V*'s six sessions takes 10:15. The inner statement has no Lean verification to compare against
  (plain leaves are refused).

### Large class (run 5)

Inner session (CPU, honest): 2.29 s to prove (two reps, 1.20 s and 1.09 s; 2.93 s end to end); proof 2 × 532,002 =
1,064,004 B; prover peak 5.05 GB.

V*'s statements, each proved `--zk` on the same 32-CPU slice. L0 was proved behind the firewall, the rest directly:

| part | k_log | instances | prove s | e2e s | proof B (2 reps) | prover peak GB | live verify s | Lean verify wall | replay wall |
|---|---|---|---|---|---|---|---|---|---|
| L0 (firewall) | 24 | 436 | 44.04 | 47.19 | 2 × 1,088,410 | 32.4 | 2.58 | 1:56.8 | 0:09.3 |
| L1 | 23 | 212 | 10.61 | 11.57 | 2 × 1,022,114 | 8.3 | 1.34 | 1:41.7 | 0:08.2 |
| L2 | 23 | 142 | 14.34 | 16.17 | 2 × 1,022,114 | 8.2 | 1.29 | 1:27.7 | 0:07.1 |
| L3 | 23 | 106 | 8.61 | 9.76 | 2 × 963,098 | 5.0 | 1.14 | 1:18.7 | 0:04.8 |
| alg-p0 | 26 | 2 | 10.55 | 11.55 | 2 × 1,036,730 | 13.5 | 4.26 | 1:50.8 | 0:23.1 |
| alg-p1 | 26 | 2 | 11.20 | 12.46 | 2 × 995,450 | 13.4 | 4.80 | 1:47.2 | 0:17.2 |
| **total** | | | **99.4** | **108.7** | **12,255,832** | 32.4 (max) | **15.4** | **10:03.0** | **1:09.7** |

- Staging V* (`rec_vstage stage`): 9:43 wall at 12.47 GB (121.5 s and 149.3 s for the two algebra circuits). The fold:
  1:39, against 10.3 s for the small class, since it reads the 774 MB inner circuit.
- Universal staging: 22:31 at 26.8 GB. Wired staging: 43:13 at 26.0 GB, of which 891 s is the Python check that the
  program evaluates as the circuit descriptions do.

**Overhead against the inner session:**
- Proving: 43× (99.4 s vs 2.29 s).
- Proof bytes: 11.5× (12.26 MB vs 1.06 MB).
- Prover side including V*'s staging and the fold: about 340× (781 s vs 2.29 s).
- Lean's verification of V*'s six sessions: 10:03.

### What the two classes show

The two classes differ 3,943 times in ANDs per instance, but each cost is set by m (27 for both), not by G:
- The inner proof is the same size (532,002 B against 531,938 B), and proving takes 2.29 s against 1.19 s. The small
  class pads 64 instances of 3,329 rows into the same 2^27 committed bits.
- V*'s four RecOpen circuits are byte-identical. Its proofs are the same size to the byte, except alg-p0's (8,256 B
  more a rep).
- The outer prove times differ by up to 1.85× on identical circuits (L2: 7.77 s, then 14.34 s). The node was shared,
  and L0 here ran behind the firewall (6.6 s more than direct in the small class). The outer totals, 77.7 s and
  99.4 s, are therefore the same cost within run-to-run noise.
- G enters only where the inner circuit is built or read: universal staging (0:34, then 22:31), wired staging (0:42,
  then 43:13) and the fold (10.3 s, then 1:39). V*'s staging is G-independent (10:48, then 9:43).

So the overhead ratio falls only when the inner session's m grows. Under caps for m 26 to 31, V* has 4 to 6 RecOpen
levels plus 2 algebra parts (`rec_shape.outer`). The format caps an instance at 2^27 bits (`K_MAX`), so a larger class
can't make one instance larger than that: m grows only with more instances.

## What's public and what leaks

Run 4's public views (`88-rec-private-public.sh`) compare two circuit descriptions of the class. They share x and the salt key by
design, so that only the circuit description differs:

- **The class and n.**
  - Public: (G, N_IN, N_OUT), n, k_log, vus_per_block and m.
  - The inner circuit is byte-identical for both circuit descriptions (same sha512), and so is each of V*'s six circuits.
- **The inner public file (28,418 B).** It differs only in `frame_v3.roots.p1`, the program row's root: 64 of 17,280 body
  bytes, 187 bytes in all. The x and output roots are equal across the two because the salt key, x and outputs are.
- **Proof sizes do not depend on the circuit description.**
  - Inner: 2 × 531,938 B for both circuit descriptions.
  - The other circuit description's alg-p0 and alg-p1 proofs are the honest ones' sizes.
- **V*'s public files.**
  - They differ in every root, and L0 to L3's also in `registered.*.paths` and `registered.out.positions`.
  - L0 to L3's file sizes differ between the two sessions; the algebra parts' don't. The positions come from the coins,
    which are on the auditor's tape. So I read the size difference as the coins', not the circuit description's. The run doesn't
    separate the two: it has no second session of the same circuit description.
- **The registration is linkable.**
  - The program's root is registered once, so every session of a circuit description carries the same `p1` root, and anyone who saw
    a circuit description's registration recognizes its sessions.
  - The salts are a function of one key. Whoever holds that key can open every row.
- **The wired topology is public.** It is the verifier's links file: which unit's output feeds which unit's input,
  `c[16:24] + u0[0:8]` and so on. It is a property of the circuit, not of the class.
- **The firewall record.** It publishes the parts, the session id, and each part's slot, stop and refusal, with their
  times.
- **The large class (run 5) shows the same views.**
  - The inner public file (5,522 B) differs only in `frame_v3.roots.p1`: 63 of 2,272 body bytes, 183 bytes in all.
  - The inner circuit, V*'s six circuits and every proof size are the same for both circuit descriptions (inner 2 × 532,002 B).
  - L0 to L3's public files differ in size, while the algebra parts' (55,312 B and 49,558 B) don't.
  - Within one m, V*'s RecOpen circuits don't depend on the class either (byte-identical across the two classes). The
    algebra circuits and the inner circuit do, but the class is public by design.
- **Not separated: timing channels.** Run 5 gives one sample per circuit description on the same circuit: the inner prove takes
  2.29 s for the registered circuit description and 2.52 s for the other. That is well inside the 1.85× spread of identical outer
  circuits across runs on the shared node, so the run neither shows nor rules out a timing channel.

## Assumptions the statements make that the runs show don't hold

Checked against the soundness theorem ("one theorem over everything the Lean verifier accepts") and against
rec-private-lean's privacy and registration statements (`RecursiveCircuitPrivate`, `…PrivateLeaves`,
`RecursiveRanRegistered`).

1. **The Lean verifier accepts V*'s statements. On main it accepts none.**
   - Registered reads need shared rows (`tables` in `FC.write`), so every V* statement is a shared-row public file, and
     `ProvedScope.check` refuses it.
   - `RecursiveSound` therefore has no executable instance on main, and the firewall's release rule (release only on
     accept) stops every recursive session at its first part.
   - The inner statement is out of scope too: plain leaves, and a shared-row file (x and the program are shared rows).
   - This is the blocker. It lifts only when the soundness proof covers shared-row registered reads (and plain inner
     leaves), and per the 4 Oct ruling the verifier gains no form ahead of its proof.
2. **The registration's salts are uniform and independent (`regLeaves`: `r : Fin nr → Salt`).**
   - The run's registration salts are SHAKE-256 of one 32-byte key, the set, the port and the row
     (`circuit.stage_salts` with a key).
   - V*'s outer proofs' leaf salts are a ChaCha20 expansion of one fresh 256-bit OS key per proof (META `salt_source`).
   - `HashDerivedKeyHm96` is about a uniform salt. No premise under `Security/` covers SHAKE-256 or ChaCha20 as a PRF or
     PRG; A4 `prf/sha-512` covers only `verity.randomness`'s streams.
   - So the statement needs such a premise, or the stager needs OS salts (`key=None`).
3. **One registration, one session.**
   - The experiment draws a fresh registration salt for its one session. A deployment reuses a registration across
     sessions, and the run shows the program root identical in every session of a circuit description.
   - Linkability across sessions isn't covered, and a multi-session statement would have to state it as a leak.
4. **The sizes are class-determined.**
   - This holds for the inner circuit, its public file's size, the proof sizes and V*'s circuits.
   - V*'s L0 to L3 public files vary in size with the coins. That is consistent with a simulator that reads the tape,
     but `nh` and V*'s public inputs must be stated as functions of the class and the tape, not of the class alone.
5. **V*'s claims are the inner's.**
   - The extra claims and each rep's comb are computed by `InnerFold.lean`, a test-side executable outside every theorem,
     and its output is V*'s staging input.
   - A wrong fold is caught only if V*'s algebra refuses it. The "different circuit description" control shows it does for that
     case, but no theorem says the fold is V*'s.
6. **The wired topology is fixed by the class.** It isn't: the links file is per circuit, and it is public.
7. **The circuit format reaches the class.** `UniversalUnit_v1` is quadratic in G, and `K_MAX = 27` caps an instance
   near 2^26 ANDs (see "The real class").

Two shape constraints the run met, which are not assumptions:
- V* takes at most 4 inner regions. That is why the circuit description is one row (`program_unit`); the unit itself would give
  5 regions' 12 claims, past `rec_residuals.MAX_SLOTS`.
- The wired circuit needs N_IN = 2 N_OUT.

## The real class

- **Its size.** For the largest vLLM proof unit, the proofs lane's route-P pricing
  (`note:proofs/20261009T0731Z-finding-routep-under-vstar`, same `and_count`) gives:
  - a 2^22-cell unit (G 1,048,472, N_IN 4,075): 1.11e12 ANDs (2^40.0);
  - a 2^27-cell unit: 6.4e14 (2^49.2).
- **The format's ceiling.**
  - C-Flock's circuit format holds an instance of at most 2^27 bits a block (`circuit.K_MAX`), about 2^26 unit rows. The
    universal unit packs at about 1.04 rows an AND (274,433 rows for 263,810 ANDs at 256,256,128).
  - So the largest class is near G = N_IN = 4,700 (for example 4096,2048,1024 at 2^25.25 ANDs). The real class is about
    2^14 times past that before V* is involved.
- **The largest class that runs cheaply.** 1024,1024,512 (4,203,010 ANDs, 2^22.0) with 8 instances: k_log 24, m 27 and
  a 4-level V*. That is run `r20261009-081632-94d3` (1:16 to 3:22 AM PDT), whose costs are the small class's (see
  "Costs"). The next sizes up multiply staging, not proving:
  - Python builds the universal circuit at about 32 s per 100k ANDs (22:31 for 4.2M ANDs, 26.8 GB).
  - 2048,2048,1024 (2^24 ANDs, k_log 26) would take about 1.5 hours and over 100 GB to stage, if time and memory grow
    linearly with ANDs. I didn't run it.
- **The class @circuits was to send.** It hadn't reached me by 3:30 AM PDT. The pricing above uses the proofs lane's
  route-P note, with the same `and_count`. Any vLLM proof unit of 2^22 cells or more is past the format's ceiling
  as a single universal instance, so no run can be made at that class with this construction.

## Code

Branch `cursor/rec-private-0419` off `origin/main` `56e4e65e8`, head **`aa7d02088`** (pushed, eight commits, not
merged). The PR is yours to open.

- `verity/ml/flock/tests/lean/InnerFold.lean`: `--program`, the verifier's own program for the setup's Linking check.
- `verity/ml/flock/pod/rec_inner.py`:
  - `universal`, `wired`, `flipped`, `program_unit` and `differ`;
  - the wired staging keeps `links.json` (the verifier's) and `no-links.json` (the cheater's session).
- `verity/ml/flock/pod/87-rec-private.sh`: the whole run.
- `verity/ml/flock/pod/rec-private-outer.sh`: V*'s outer sessions in three modes (behind the firewall, sent as a
  forgery, plain), and `release_check` (Lean's core-firewall on canonical JSON).
- `verity/ml/flock/pod/88-rec-private-public.sh`: the public views of two circuit descriptions.
- `verity/ml/flock/pod/89-rec-private-direct.sh`: the parts the firewall stops, on an earlier staging.
- `verity/ml/flock/pod/rec_private_summary.py`: `summary.json`.
- `verity/ml/flock/tests/test_rec_private.py`: 2 passed at `aa7d02088` (one slow: two circuit descriptions staged and their public
  files compared). Lint: `ruff check` passes on the Python.

## Notes for you

- **The VM's disk.** This VM's disk filled to 78 MB free at 08:24Z, mostly other lanes' worktrees under `/tmp` (122 GB,
  12 GB of it `pytest-of-ubuntu`). I ran `research data evict --target-free-gb 6 --runs`, which removes only local copies
  already preserved, and touched nothing of anyone else's. It is now about 12 GB free. `research run` refuses to start
  under its disk floor, so the next lane on this VM may need to clean `/tmp`.
- **Notes.** `RESEARCH_NOTES_TOKEN` isn't set on this VM, so no `note:` was published. This file is the record; copy it
  into the notes if anyone else needs it.
- **Nothing was posted to Slack.**
