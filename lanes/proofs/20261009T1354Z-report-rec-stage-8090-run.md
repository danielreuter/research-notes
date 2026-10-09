---
id: proofs/20261009T1354Z-report-rec-stage-8090-run
campaign: private-circuit
lane: proofs
kind: report
status: open
repo: verity
origin: [agent:bc-b5fd2fd3-5213-5a73-ad38-09e77b43f4c4]
---

CHECKPOINT none (14:35Z) [open] 14:35Z: #1626 (zk-coin) ready at a38fdb621 and handed to the lander for a train with --agreement; its own check fd14 cancelled (no slot in 5 h, main moved past it)
CHECKPOINT none (14:26Z) [open] 14:26Z: 14:30Z report posted to top (1791555948.849019): run 2922, verifier 7d76c0875 = 77d9136ca (a8a5: lean-agreement passed, rest running), merged tree 1d2f7442f (19ca: lean-agreement passed 14:25Z, rest running); 5a/5b progress due 14:50Z
CHECKPOINT none (14:03Z) [open] 14:03Z: verifier check 19ca (1d2f7442f, merged tree) passed lean-agreement; suites/audit running. 14:30Z post ready to send once the verifier line is in.
CHECKPOINT none (13:56Z) [open] 14:00Z: rec-stage done (8090 overhead: 1,124x end to end, 173x prove, 10.7x proof, 40x Lean). Worker reports copied to notes (20261009T1354Z-report-*). 14:30Z post drafted; waiting on checks 19ca/a8a5 for the verifier line.
# The real private circuit's class through the recursion to the Lean verifier

Worker for @proofs (bc-8416bc72), 9 Oct 2026, written 13:25Z. Branch `cursor/rec-private-stage-95d4`, tip 88afdfe84, pushed, no PR.

## Outcome

The class UniversalUnit_v1{8090,64,32}, holding F32MulFtz_v3 as the private circuit, went through the whole recursion on vy-nebius-1. **The Lean verifier accepts every outer part (L0 to L5, algebra p0 and p1), the firewall released every part, and `lean_of_record` is accepted.** The other circuit, run as the control, is refused at the algebra's part 0 by Lean and by the live verifier, for a real check rather than a form. Every refusal among the controls is a real check; none is a form refusal.

Lean refused one form, as expected: the inner session's form, `verity/flock-circuit+plain-leaves` (plain SHA-512 leaves, `flock-leaf/sha512-unsalted`). That session stays behind the firewall and is not of record. Nothing was widened.

The verdicts are unchanged when re-verified under zk-shared-rows' latest verifier (41ada9c94).

Against F32MulFtz_v3 proved directly with C-Flock `--zk` (public circuit, no recursion), the recursion costs:
- about 1,124× the prover's end-to-end time (73.4 min against 3.9 s);
- 10.7× the proof bytes (23.3 MB against 2.2 MB);
- 40× the Lean verify time (11.5 min against 17 s);
- 49× the live verify time.

## What was merged, and the edits

The real run's commit is 7d76c0875. It contains:
- zk-shared-rows at b1b604bd7 (merge 3ebd731df);
- rec-private-summary #1624 (436f885b4);
- rec-residual-parts #1630, MAX_SLOTS 160 (621e367ee);
- zk-coin-commit #1626 (d38072121).

Before the last Lean verify I re-fetched zk-shared-rows. It had moved to 41ada9c94, which I merged (e5561be28) and re-verified against (see "Re-verify" below).

My edits:
- **Draw** (4b2113ea0): `outer()` in `verity/ml/flock/pod/rec-private-outer.sh` serves every V* outer statement with `--draw subset:N`, N being the statement's instance count (k = n). This is a one-line change; rec-v0 kept it.
- **Reuse of the staging** (9ac919b72): `STAGED` and `STAGED_RECORD` in `87-rec-private.sh`, plus `WCLS` (the wired staging's class) and a cap-fold wait.
- **CAP_CLAIMS** (7d76c0875): the run guards on the fold's claim count, 2 + regions × link points = 2 + 3 × 2 = 8, instead of waiting without bound for the cap fold.

At the tip I merged rec-v0's `cursor/rec-private-0419` at 932fcb4db (88afdfe84). Where our edits met, I took rec-v0's:
- `87-rec-private.sh` is now rec-v0's, with a CAP_FOLD wait of up to 2 h in place of my CAP_CLAIMS, and its extra controls;
- `class_statement.py` is now rec-v0's;
- my `direct` baseline mode and my re-verify mode are removed in favour of rec-v0's `91-rec-private-baseline.sh` and `92-rec-private-reverify.sh`.

`test_rec_private.py` passes (4 tests).

## Staging and its salts

I reused the staging and did not restage. It is at `/workspace/jobs/rec-stage/data/rec-stage/f32mulftz-8090-64-32-n32-prog/{stage,other}`, from run r20261009-092332-af31 (art:b32f104d2b7fcf8393d42549f4a5941c621e5f247cfd0ecb6072d9718415763d, 52:46 wall, 197.8 GiB peak).

**Its registration salts are key-derived**, from a per-run `secrets.token_bytes(32)` key that was never stored. Tonight's decision is OS salts, so this goes on the gap list. rec-v0's e9883cfc8 draws future registration salts from the OS. The baseline below already used OS salts.

## The run

Run r20261009-110905-2922 at 7d76c0875 ran from 11:09:28 to 13:12:10Z (wall 7362 s) on vy-nebius-1 with 32 CPUs held through `hold_slices`. Its run record is art:a3c1dde9dae8d13e6dbc3a1e911755a8bcc152b04887f583cb5d33ef34c6af6d; the art for its run files is pending custody. It was launched with:
- `CLS=8090,64,32 N=32 WCLS=16,16,8 NW=8 CPUS=32 CAP_CLAIMS=8`;
- `STAGED` and `STAGED_RECORD` pointing at the staging above.

### Steps: wall time and peak memory

| step | wall | peak | result |
|---|---|---|---|
| wired staging (16,16,8) | 0:44.78 | 0.6 GiB | ok |
| inner session, honest (behind the firewall, ZK off, plain leaves) | 6:46.73 | 116.2 GiB | proved; firewall contract ok |
| inner session, other circuit | 6:49.09 | 115.5 GiB | proved |
| fold, honest | 48:26.10 | 124.8 GiB | 8 claims (6 extras); CAP_CLAIMS guard ok |
| fold, other circuit | 48:49.44 | 125.1 GiB | ok |
| `rec_vstar`, honest | seconds | small | accepted (204 message rows, 1054 queries) |
| `rec_vstage stage`, honest | 13:41.73 | 12.2 GiB | 8 statements; both algebra parts hold |
| `rec_vstage stage`, other circuit (`--levels none`) | 4:59.63 | 12.1 GiB | algebra p0 fails (residuals 6 and 7 nonzero); p1 holds |
| `rec_vstage stage`, forged top | 1:07.71 | 2.9 GiB | staged (control) |
| outer parts, prove + Lean + release + replay | see the next table | 35.4 GiB at most | all accepted and released |
| public views (88), other circuit's levels | 8:09 | 7.2 GiB | see "Public views" |

The honest inner session:
- k_log 27, 32 instances, 3 regions;
- statement build 350 s, witness 15.3 s, prove_total 18.7 s, end to end 34.0 s;
- proof 2 × 731,946 B, plus session.json at 419,365 B; all of it stays behind the firewall;
- firewall contract ok: 1300 of 1300 items, and the firewall and Lean agree.

Lean refused the inner session for its form, as expected: "verify: refused: verity/flock-circuit+plain-leaves, a statement with plain SHA-512 leaves (flock-leaf/sha512-unsalted): a form the soundness proof does not cover yet". The live replay without `--zk` refused the shared-row public file.

The V* statements `rec_vstage` built are at k_log 23 except L0:
- L0: 436 × RecOpen_v4{LANES=64,H=13}, k_log 24;
- L1: 212 × H=12;
- L2: 142 × H=10;
- L3: 106 × H=9;
- L4: 86 × H=7;
- L5: 72 × H=5;
- algebra p0 and p1: 2 × InnerRepCheck_v2 each, k_log 26.

### Outer parts

Every part was run under `--zk` with `--draw subset:n` (k = n), behind the outer firewall. Each part went through the same steps:
- the live serve accepted it;
- Lean `verify --zk --statement verity/flock-circuit --circuit --public --partition --program --registered --session` accepted it;
- core-firewall's `release_check` said "accept", and the part was released;
- `replay --zk` accepted it.

| part | prove (wall / peak) | Lean verify (wall / peak) | replay | live verify_s | proof bytes |
|---|---|---|---|---|---|
| L0 | 59.27 s / 35.4 GiB | 2:00.92 / 4.0 GiB | 15.69 s | 2.108 s | 2,822,620 |
| L1 | 25.85 s / 11.6 GiB | 1:25.08 / 2.8 GiB | 10.47 s | 0.969 s | 2,675,851 |
| L2 | 21.44 s / 11.5 GiB | 1:18.56 / 2.5 GiB | 8.57 s | 0.856 s | 2,675,063 |
| L3 | 16.88 s / 7.3 GiB | 1:13.00 / 2.3 GiB | 7.80 s | 0.842 s | 2,534,655 |
| L4 | 17.19 s / 7.2 GiB | 1:03.13 / 2.0 GiB | 6.94 s | 0.932 s | 2,534,460 |
| L5 | 13.69 s / 7.0 GiB | 0:49.95 / 1.6 GiB | 6.90 s | 0.668 s | 2,534,327 |
| algebra p0 | 56.29 s / 21.5 GiB | 1:52.83 / 2.4 GiB | 32.69 s | 4.457 s | 3,797,887 |
| algebra p1 | 60.01 s / 21.5 GiB | 1:48.11 / 2.4 GiB | 29.46 s | 5.016 s | 3,685,556 |
| **total** | **270.6 s** | **691.6 s** | **118.5 s** | **15.85 s** | **23,260,419** |

Proof bytes count the representation files plus session.json and verifier.json.

The live serve's session_s per part was 47.09, 17.60, 14.82, 11.05, 11.55, 9.37, 37.40 and 39.84 s, 188.7 s in total.

The L0 detail:
- prove: statement built in 7.05 s; prove_total 35.4 s; end to end 44.9 s;
- Lean: inputs 3.5 s, setup with the draw 35.0 s, session 78.4 s.

The verifier derives each statement's circuit file itself; they are 176–431 MB each. The public files (L0's pub.bin is 3,111,480 B) are not counted in the proof bytes.

The firewall record (`firewall-record.jsonl`, 18 lines) shows:
- the open, with 8 parts;
- the inner session's finish;
- a slot and a release for each of L0, L1, L2, L3, L4, L5, algebra p0 and algebra p1.

### Controls

All of the following were refused by a real check, none for its form.

| control | Lean | live verifier |
|---|---|---|
| forged top at L5 | refused: "opening: ring-switch claim 12 mismatch" | refused: "opening: RingSwitch(ClaimMismatch)" |
| flipped top at L1 | refused: "setup: registered reads: port out: table row 0 does not open rec-top-L1's registered root at position 0" | refused: "zk inner: the batched constraint fails (⟨c, Y⟩ ≠ t + β τ)" |
| other circuit, algebra p0 | refused: "zk inner: the batched constraint fails (⟨c, Y⟩ ≠ t + β τ)" | refused, same message |
| other circuit, algebra p1 | accepted (expected: p1 does not depend on the circuit's description) | accepted |

Before the outer sessions, the run also checked these controls:
- **V\* on a flipped top**: refused, "FIREWALL-REFUSED: tree top: circuit/rep0 round 70's top 0 does not open its commitment". The checked prover refused it too (0:04.98). The unchecked prover staged L1, which is the flipped-top control in the table above.
- **Wired fold**: 0:08.83, ok.
- **Wired fold without the program**: refused, "setup: META links: Linking needs the verifier's own program and partition".
- **Made-up fold**: refused, "setup: links: cut wire [240, 248) from unit 0 to unit 8: the reader's row p1 is not the writer's committed output row".

`rec_private_summary.py` wrote summary.json with **`LEAN-OF-RECORD accepted {}`**. It counts a control as caught only when it is refused for a reason other than its form.

### Public views

For the 88 public views, the other circuit's levels took 8:09 at 7.2 GiB.
- The inner public file is the same size for both circuits (15,362 B). The two differ in 184 bytes, all in the header at `frame_v3.roots.p1`.
- Every V* statement's circuit is identical for the two circuits.
- The public files are the same size, except L2 and L4, which differ by 1 byte. Other runs show the same few-byte variation between sessions.

## Re-verify under zk-shared-rows 41ada9c94

Run r20261009-131240-538f (art:67f3fbb919241adde70730fc176db2bc09fa62a2854bc14fe8896660f48a2420) used rec-v0's `92-rec-private-reverify.sh` with JOBS=12 on 16 cores. Its Lean verifier is lean-0eb759c117e7a1d8, built from the branch tip 88afdfe84; the run itself was verified by lean-c2cec4b524233c91, built at 7d76c0875.

**Every verdict is unchanged:**
- all 8 honest parts are accepted;
- the forged-top, flipped-top and other-circuit p0 controls are refused, with the same messages;
- the other circuit's p1 is accepted.

| part | wall (contended) |
|---|---|
| L0 | 2:34.96 |
| L1 | 1:43.84 |
| L2 | 1:29.03 |
| L3 | 1:37.95 |
| L4 | 1:23.39 |
| L5 | 0:52.89 |
| algebra p0 | 2:42.64 |
| algebra p1 | 7:18.40 |
| forged top | 0:54.81 |
| other circuit, p0 | 2:31.04 |
| other circuit, p1 | 6:35.39 |

The algebra parts are slower under the newer verifier, and contention does not explain it. A serial re-verify of the smoke run, r20261009-123840-d4fd (art:1557527c021349bbac2c80a0be096e72fce2816b329e4c8f3bc9dc5abd24fef4), showed:
- algebra p0 rising from 1:57 to 2:50;
- algebra p1 rising from 1:48 to 6:19.

The likely cause is main's `Flock.RecResiduals.check` rebuilding the residual part net.

## Baseline: F32MulFtz_v3 proved directly with C-Flock `--zk`

I proved the baseline in run r20261009-120313-a500 at 40958f420 (art:caafce8cd0ef5d50618601041bde5e375ae0dde11cce291699fed2841016e205).

The statement:
- F32MulFtz_v3 as a 32-unit population program under `Q_template_instance` v0, with META naming the Definition;
- the circuit public, rows unshared, OS salts;
- k_log 22, vus_per_block 2, 2506 ANDs, circuit file 56,067,468 B.

Results:
- stage: 14.66 s at 0.55 GiB;
- statement: 1.30 s;
- prove: 3.92 s at 1.71 GiB (prove_total 0.90 s, end to end 2.03 s);
- Lean: accepted in 17.15 s at 0.52 GiB (32 units derived);
- live verify: accepted, verify_s 0.321 s (session_s 2.35 s);
- replay: accepted, 2.34 s;
- proof: 2,168,736 B.

My baseline mode was removed at the tip in favour of rec-v0's `91-rec-private-baseline.sh`, which does the same job. These numbers come from my mode at 40958f420.

## Overhead of the recursion against the baseline

| measure | recursion | baseline | ratio |
|---|---|---|---|
| prover end to end: inner prove 406.7 s + fold 2906.1 s + vstage 821.7 s + outer proves 270.6 s | 4405.1 s (73.4 min) | 3.92 s | ≈1,124× |
| prove commands only: inner + outer | 677.3 s | 3.92 s | ≈173× |
| session proving: inner end to end 34.0 s + outer prove walls 270.6 s | 304.6 s | 3.92 s | ≈78× |
| proof bytes the verifier receives (outer parts) | 23,260,419 B | 2,168,736 B | 10.7× |
| Lean verify, the parts one after another | 691.6 s | 17.15 s | 40.3× |
| live verify_s | 15.85 s | 0.321 s | 49× |
| replay | 118.5 s | 2.34 s | 51× |
| peak memory | 124.8 GiB (fold); 116.2 GiB (inner); 35.4 GiB (outer) | 1.71 GiB | ≈73× |

Notes on the table:
- The fold is two thirds of the prover's time (48 min, single-threaded) and sets the peak memory.
- The outer parts are independent statements, so a verifier can check them in parallel; the slowest alone is L0's 2:01.
- One-off staging adds 52:46 at 197.8 GiB, against the baseline's 14.7 s stage.
- The inner proof (1,883,257 B including its session.json) stays behind the firewall and is not counted.

## Other evidence

- Inner run r20261009-101844-a23e: art:a0e050fd62a8e24a7e600de47855225e14863e457c363a16a0e842eaeb50d1e5.
- Ladder: art:fa61dd112462cfc9179c11ca6fe0ee25d44945b82e9a292b893531b066fc4a1f.
- Smoke run r20261009-111041-12f2, which also ended with `lean_of_record` accepted. Its run files: art:cb03a8d864ae573173fda305b6f77f9d5d2f9890b1c689573b2d58980ecd6396.
- Cancelled runs, superseded by the run above: r20261009-110011-3eac, r20261009-102129-f89e, r20261009-110059-d4a6.
- First direct-baseline attempt, r20261009-111706-7788: refused for its form. Fixed with the population program, unshared rows and META.

## Open items (for the gap list)

1. **Key-derived registration salts** in this staging, against tonight's decision of OS salts. Future staging under rec-v0's e9883cfc8 draws them from the OS. I did not edit `rec-gap-list.md`, which belongs to another agent.
2. **The inner session's form** (plain SHA-512 leaves) is not covered by the soundness proof. This is expected: the inner session is behind the firewall and not of record.
3. **12-claim shapes** need Lean's MAX_SLOTS at 160 (`cursor/rec-max-slots-741b`, not on main). At m32-k27-c8 (8 claims) the residual parts are identical under 128 and 160, so this run is unaffected.
4. **The algebra parts' Lean verify is 1.5–3.4× slower** under main's `RecResiduals.check` (see "Re-verify").

## Friction notes

1. `research cancel` signals only the run's process group, but `timeout` puts its child in a new group. So the `timeout` children of `90-rec-stage.sh`'s MODE=fold and MODE=measure survive a cancel; I killed one by PID. A likely fix is `timeout --foreground`. Not done here.
2. Two jobs starting together can race on creating the uv venv.
3. My cap-fold wait had no bound, but the run's timeout was 3600 s. rec-v0's CAP_FOLD now waits up to 2 h.
4. Custody evicts a finished run's session files: about 53 min after the smoke run ended. That cut its first re-verify short. Re-verify soon after a run, or first restore its files with `research data fetch ART --to DIR`. For the real run, I started the re-verify right after it finished.
