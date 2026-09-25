---
lane: red-team-standard-hash
kind: report
created: 2026-09-25T07:15Z
status: open
---

CHECKPOINT a37cea8 (10:18Z) [open] 11:32Z PASS main 3301c435 +blake3 and da74b03e +sha256 (R1/R4 refused, H2, compress_one diff; art:cd2828c5); sp1 cell counts only via vn2 19-sp1c gate; gadget scans: blake3 x4 finishing, sha256 queued
CHECKPOINT 5483d13b (10:04Z) [open] 10:58Z main 3301c435 fp8-ada+blake3: R1/R4 refused, H2 PASS (run rtsh-final-1050); da74b03e +sha256 suite + compress_one differential running; BLAKE3 scan 3/4 shapes 0 free; next sha256 gadget scan
CHECKPOINT none (09:53Z) [open] 10:36Z disk: deleted my /tmp evidence copies (~560 MB, all preserved: art:0e8faae7 etc) + 4 scratch worktrees (~1 GB); store objects 8381eb93 (105MB) / ee92c75a (40MB) 08:3xZ may be from my art:c7683eb2 put. From now: pod-only, no laptop downloads
CHECKPOINT 5aa9f63 (09:52Z) [open] 10:32Z +sha256 be1a3bcb FAIL R1+R4 inherited (art:0e8faae7), closed by c8a16e2b merge (art:57a22acb); BLAKE3 gadget mutate-recompute scan 0 free rows on 3 shapes, control 18; sp1 R3 open
CHECKPOINT 15f74f3 (09:28Z) [open] 10:00Z 24ab6c7d+806a2f73 PASS R1/R2/R4/H2 (art:cd2c38ea, art:be211735); sp1 R3 fix open on --instances (handoffs 0925Z); running: +sha256 R1/R4/H2 at be1a3bcb and +fix, BLAKE3 gadget mutate-recompute scan
CHECKPOINT 10996616 (09:01Z) [open] 09:02Z re-testing ligero-steps-pin tip 24ab6c7d on pod (R1 remap, R4 orphan vus3 + vn2 06b, H2 48/64); sp1 R3 fix b54e42ed review note pending; sha256 PINS not landed
CHECKPOINT 5c73abf (08:56Z) [open] c81ed1c8: agkr native tree check PASS (4 pins core-reproduced, art:8dee00aa); vn2 R4 fix confirmed; open: ligero-steps-pin fix handoff, sha256 pins, agkr hash layers, survey §3.8 link
CHECKPOINT f4d797b (08:51Z) [open] c81ed1c8: agkr-bound pins recomputed core-only from frozen sets: fp8-hopper +blake3 and +vllm-v1 a/b/y MATCH; bf16-ampere pending (set rebuilt on pod); R4 handoffs out; inbox empty; no sha256 pins yet
CHECKPOINT e10e1d6 (08:33Z) [open] 21393756: R4 BREAK: R2 coverage (de2fa317 reverify + vn2 06) counts stmts w/o proof, 1/3 VUs proven PASS art:c7683eb2; de2fa317 closes R1, H2 PASS art:9fa210e7; sp1 R3 art:b11bc6ee; survey adopted (review §3.8 link when sent)
CHECKPOINT a33671b (08:07Z) [open] e1138866: vn2 06-core-roots closes R1/R2 (flags forgery, art:8f2112e2); sp1-committed PASS guest/tree, R3 prover-chosen roots art:b11bc6ee; handoffs sent; polling for ligero-steps-pin fix, sha256 pins
CHECKPOINT a2d67679 (07:46Z) [open] R1 remap BREAK fp8-ada+blake3 FAIL art:2b51c5fd; H2 steps pin PASS art:efaa3a46; blake3-80gb FAIL inherited (handoff sent); sha256/agkr not ready; now reviewing sp1-committed
CHECKPOINT 7a8268cf (07:31Z) [open] fp8-ada+blake3 FAIL: R1 (vu,x,W) triple prover-chosen -> swapped y under honest x/W roots accepted pinned+python+reverify PASS; R2 reverify recomputes no roots/binding/coverage; handoffs sent; art:2b51c5fd. Next: H2 steps forge on +blake3
CHECKPOINT 57e77c14 (07:16Z) [open] pod vy-red-team-sh (cpu3c 4vCPU) syncing; R1 candidate BREAK: (vu,x,W) triple prover-chosen in v5 verify (Rust+Py) -> wrong y under honest x/W roots; R2: reverify.py recomputes no root/binding/coverage; e2e 57e77c14 pending
# red-team-standard-hash: red team of tonight's committed-relation statements

Worktree `~/projects/verity-main-wt/red-team-standard-hash`, branch `lane/red-team-standard-hash`, base main 00ffe398.
Pod `vy-red-team-sh` (04txgm7j3b0nob, cpu3c 4 vCPU, $0.12/h; 16-vCPU flavors had no capacity at 07:00Z). Budget $10, FINAL 16:00Z.
Scope: decision doc §3/§5/§6.2/§6.4 row "red-team-standard-hash": per statement the hash gadget, digest publication, the native
tree check (domain derivation, node/level/index, vllm-v1 path shape + root fields), the `steps` pin.

## Findings (numbering R1..)

| id | statement | severity | status | evidence |
|---|---|---|---|---|
| R1 | every v5 hashed statement (`+blake3`, `+poseidon2`, `+ajtai-*`), ligero-verify + Python | BREAK | e2e: forgery accepted pinned + Python + reverify PASS; again under production bindings | art:2b51c5fd, art:8f2112e2 |
| R2 | B-Ligero independent re-verification (`reverify.py`) | BLOCKING | code read; closed for results checked by verify-night-2's `06-core-roots.py` (it flags the R1 forgery MISMATCH) | art:8f2112e2 |
| R3 | SP1 relation-committed/v1 and -vllm/v1 `committed-verify` | BLOCKING (the R2 pattern) | e2e at tree-check level: prover-chosen roots under the frozen set's bindings and id accepted | art:b11bc6ee |
| R4 | the R2 coverage checks: de2fa317 `reverify.commitment_problems`, verify-night-2 06 | BREAK of coverage (throughput claim; relation soundness unaffected) | e2e: 1 of 3 VUs proven, reverify PASS (de2fa317) and main reverify PASS + 06 ROOTS-MATCH (stmt-only manifest entries) | art:c7683eb2 |
| fix re-test | b-ligero-standard-hash 3af90e71 + de2fa317 | R1 closed; H2 PASS; R4 open | e2e | art:9fa210e7, art:c7683eb2 |
| fix re-test 2 | ligero-steps-pin 24ab6c7d; b-ligero-standard-hash 806a2f73 | R1, R2 and R4 closed; H2 PASS | e2e | art:cd2c38ea, art:be211735 |
| R3 re-review | sp1-committed b54e42ed | open on `--instances` and without `--batch` (fails open) | code read | lanes/sp1-committed 0925Z |

## Verdicts
| statement | verdict | evidence | handoffs |
|---|---|---|---|
| fp8-ada+blake3 (b-ligero-standard-hash, frame-v3 keyed-BLAKE3 rows, v5 included-hash) | **PASS on main 3301c435** (R1 and R4 refused, H2 PASS, gadget scan 0 free rows). FAIL (R1, R4) before 3301c435. A cell counts only if its dump passes main's reverify or 06 | art:2b51c5fd, art:8f2112e2, art:cd2c38ea, art:be211735, art:cd2828c5 | coordinator 0735Z, 0805Z, 0920Z, 1130Z; b-ligero-standard-hash 0735Z, 0920Z; ligero-steps-pin 0920Z; verify-night-2 0805Z |
| H2 steps pin (main c5cf7f6d, fp8-ada+blake3) | PASS: every forged steps value tried (incl. 64, 40) refused by both verifiers; honest 48 accepted pinned | art:efaa3a46 | in coordinator 0735Z |
| blake3-80gb cells (same v5 statement) | PASS on main 3301c435 (FAIL before), on the same condition: each dump passes main's reverify or 06 | art:2b51c5fd, art:be211735, art:cd2828c5 | blake3-80gb 0750Z, 1130Z |
| b-ligero-sha256 `sha256/row/v1`, fp8-ada-x4+sha256 (pinned d6b0cd8d) | **PASS at da74b03e** (R1 and R4 refused, H2 PASS, `compress_one` = hashlib). FAIL at be1a3bcb (the R1 forgery is accepted and preserved; R4 passes), so a cell counts only on da74b03e's / main's reverify | art:0e8faae7, art:57a22acb, art:cd2828c5 | coordinator 1030Z, 1130Z; b-ligero-sha256 1030Z, 1130Z |
| sp1-committed relation-committed/v1 and -vllm/v1 (d12770c3, b54e42ed) | PASS on the guest and tree check. R3 FAIL (open in code): `--instances` and no-`--batch` accept prover-chosen roots. Cell art:49695f7c counts only through verify-night-2's 19-sp1c gate (core-recomputed statement, `instance_roots` true on every rep); I reviewed the procedure: PASS | art:b11bc6ee | coordinator 0820Z, 0925Z; sp1-committed 0820Z, 0925Z |
| agkr-bound row-digest (caacca10), frame-v3 + vllm-v1 | native tree check PASS: all 4 pins reproduced core-only from the frozen sets; in-proof hash layer not ready (no verdict) | art:8dee00aa | coordinator 0905Z; agkr-bound 0905Z |
| verify-night-2 06 procedure (R1/R2/R4) | PASS after their 0850Z R4 fix (control ROOTS-MATCH, both R4 dumps MISMATCH) | art:8f2112e2, art:c7683eb2, art:8dee00aa | coordinator 0805Z, 0835Z, 0905Z; verify-night-2 0805Z, 0835Z |

### R1: the (vu, x, W) leaf triple is prover-chosen
Both verifiers check only that each VU's x digest opens at `x_index[v]` under root a, its W digest at `w_index[v]` under
root b, its y word at `vu_index[v]` under root y. Nothing derives `x_index`/`w_index` from `vu_index` and the committed set's
layout (the honest prover uses x = W = vu unshared, `(v // nw, v % nw)` for a tile: `relchain.auth_for`). The statement digest
absorbs the triple, which binds the challenges to it but does not make it correct. So a committer serving a wrong y_v gets it
accepted by proving VU v on any committed (row a, column b) whose product equals y_v (with 4096 x 4096 candidate pairs and 22-bit
outputs, a match for an arbitrary wrong value is likely). Fix: the verifier derives the triple (unshared: x = W = vu; tile:
from (nx, nw) in the verifier's expectation) and refuses any other; the Python verifier the same.

### R2: independent re-verification recomputes nothing from the instance set
`reverify.py` (writes `verified=accepted`) checks custody, the system pin and a Rust `batch` accept. It never recomputes the
three roots from the instance set, never checks the trees' `binding` (the frame-v3 domain: `binding_digest(dataset, manifest,
lo, hi, K, tree, schema)`) or `count`, and never checks the VU coverage of the claimed range. Rust reads binding, owner, count
and root from the statement (`format.rs::read_tree_refs`), so the frame-v3 "verifier-derived domain" is prover-described in
B-Ligero. TABLES.md admissibility 6 requires "the statement's commitments and public words recomputed from the instance set".

## Log
* 06:58Z start; contract, TABLES, decision doc, red-team-leaf-3 report read; inbox empty.
* 07:00Z pod: cpu3c 16/8, cpu5c, cpu3g, cpu3m no capacity; cpu3c 4 vCPU created (04txgm7j3b0nob), registered, bound.
* 07:03Z `research pods sync` (245 MB over the laptop uplink, slow).
* 07:10Z R1/R2 from code reading; 57e77c14 e2e harness `rtsh_remap_e2e.py`.
* 07:21Z setup run rtsh-setup-0719 OK. 07:22Z r1 run at 4 VUs l=1024 OOM-killed (8 GB cgroup) -> 2 VUs l=256.
* 07:27Z r1b: forgery python ACCEPT, rust refused on bits only (2^-127.88); 07:29Z r1c (target -132): FORGERY ACCEPTED pinned, reverify PASS.
* 07:33Z art:2b51c5fd preserved; 07:35Z handoffs coordinator + b-ligero-standard-hash (FAIL, cell pulled).
* 07:35-07:45Z H2 runs rtsh-h2-0735 and rtsh-h2b-0739 (`rtsh_steps_e2e.py`, a2d67679): the honest steps-48 run is accepted
  pinned; forged steps are refused by Python and by Rust ("statement: steps = 64 columns per VU, the fp8-ada relation's VU is
  48 columns of K = 32"). PASS, art:efaa3a46. 07:50Z handoff to blake3-80gb (FAIL inherited).
* 07:41Z received `20260925T0745Z-handoff-from-coordinator.md` ("Thanks for R1/R2. Two follow-ups"): (1) whether verify-night-2's
  procedure closes R1/R2; (2) re-test ligero-steps-pin's fix when it hands off (pending: no handoff yet).
* 07:57Z run rtsh-r1pb-0810 (harness 8ace1ada `--set-binding`): R1 forgery under the relation's instance-set bindings; a/b trees
  equal the core's; still accepted by Python, Rust pinned and reverify. verify-night-2's `06-core-roots.py` `check()` run
  verbatim (`vn2_check_on_r1.py`): MISMATCH on the leaf indices and the y root. art:8f2112e2. 08:05Z handoffs to the
  coordinator ("YES, 06 closes R1/R2") and to verify-night-2 (a nit on how 06 picks the manifest).
* 08:15Z sp1-committed review (d12770c3), runs rtsh-sp1-0815 and rtsh-sp1c-0818 (`rtsh_sp1_roots.py`, e1138866): the guest and
  tree check are sound and positional; the roots are prover-chosen (R3). A statement over the frozen fp8-ada set's [0, 1) with
  all-zero rows is accepted by `check`. Core-only roots over the true rows equal the SP1 reference's. art:b11bc6ee. 08:20Z
  handoffs to the coordinator and sp1-committed.
* 07:49Z received `20260925T0752Z-handoff-from-coordinator.md` ("SURVEY LANDED: the gate is lifted..."). Adopted: nothing
  changes in my queue; I will red-team the survey's §3.8 binary-to-prime-field link write-up when it is forwarded. The
  survey's "XOR-output-bits BLAKE3 gadget" for b-ligero-standard-hash also goes in my queue, if it lands.
* 08:10Z run rtsh-fix-0840 on b-ligero-standard-hash de2fa317 (synced to /workspace/src-fix from a detached worktree):
  - R1 remap forgery refused (layout error) by Python and Rust;
  - H2 steps 48 accepted pinned, 64 refused;
  - first R4 attempt: my control used n_proofs = 1 with 2 proofs, so the batch refused it; the harness was fixed.
  art:9fa210e7.
* 08:25Z run rtsh-r4-0850 (harness 21393756, N = 3, only VU 0 proven):
  - de2fa317 reverify PASS on both the orphan-.stmt and the stmt-only-entry variants;
  - main reverify PASS plus 06 ROOTS-MATCH on stmt-only entries;
  - the honest controls pass.
  art:c7683eb2. 08:35Z handoffs to the coordinator (amending 0805Z), verify-night-2, b-ligero-standard-hash and
  ligero-steps-pin.
* 08:45-09:00Z `rtsh_agkr_pins.py` (c81ed1c8), runs rtsh-agkr-0905 and rtsh-agkr3-0927. The bf16 frozen set was rebuilt on
  the pod (155 s); its arrays match manifest 059103cf, and I restored the manifest the build had rewritten. All 4 agkr pins
  MATCH core-only. art:8dee00aa.
* 08:50Z received `20260925T0850Z-handoff-from-verify-night-2.md` ("R4 fixed in verify-night-2's 06/16..."). Re-ran their
  new 06 on my R4 dumps (rtsh-vn2b-0935): control ROOTS-MATCH, orphan-stmt and stmt-entry MISMATCH. Confirmed. 09:05Z
  handoffs to the coordinator and agkr-bound.
* 08:44Z received `20260925T0844Z-handoff-from-blake3-80gb.md` ("FYI: H100 +blake3 results ... use the same v5 statement as
  fp8-ada+blake3"). Their dumps are art:5b08aeae, art:f020c25b and art:c6462d1a. The same statement means the same verdict:
  the cells count once they are re-verified with the fixed reverify, or with verify-night-2's 06.
* 09:02Z run rtsh-lsp-24ab6c7d on ligero-steps-pin 24ab6c7d (ligero-verify built from that tree):
  - R1 remap refused by Python, Rust pinned and reverify;
  - R4 orphan (3 VUs): control PASS 3/3, orphan-stmt and stmt-entry FAIL;
  - fixed 06 on the same dumps: control ROOTS-MATCH, both variants MISMATCH;
  - H2 steps 48 accepted, 64 refused.
  art:cd2c38ea.
* 09:05Z received `20260925T0905Z-handoff-from-b-ligero-standard-hash.md` ("R4 fixed, via ligero-steps-pin 06176b41 plus
  my 806a2f73 ... Please re-run"). Ran rtsh-bls-806a2f73 on 806a2f73 with the same suite; every result was the same.
  art:be211735.
* 09:10Z gadget read at 806a2f73 (`leaf/blake3.py`, `hashchain.py`); no finding:
  - the operand words are boolean-bit sums, so the limbs cannot alias;
  - the half-block layout, counter and flags come from the carried `pos`;
  - the digest is pinned at `is_end`;
  - `leaf_bytes_many` equals `leaf_bytes`.
* 09:15Z sp1 b54e42ed review. The R3 fix is correct on `--batch`. It fails open elsewhere: `committed-verify` without
  `--batch` gives ok with `instance_roots: null`, and `vector_run --instances` never passes `--batch` and skips the
  prover-chosen-roots negative.
* 09:20Z handoffs to ligero-steps-pin, the coordinator and b-ligero-standard-hash (PASS on R1, R2, R4 and H2). 09:25Z
  handoffs to sp1-committed and the coordinator (R3 open on `--instances`; those cells pulled).
* 09:35-10:25Z the BLAKE3 gadget determinism scan `rtsh_blake3_free_rows.py` (5dfb1399, then 7d429908). The first version
  tested single-row perturbations, and its dropped-decomposition control found 0 free rows: too weak, rejected. The second
  version overrides each computed row, recomputes everything downstream and re-checks every constraint (run rtsh-free2-1000
  at 806a2f73). The control finds 18 free rows. The shapes 8:0.5 (fp8-ada+blake3), 8:1 and 16:1 find 0 free rows in about
  61k mutations each; 8:2 is running.
* 09:45Z the A-GKR `sha256_flat.py` spike (agkr-bound 02927b7b), code read: the 16-bit-half adder check is sound (at most
  7 terms, (t+1) 2^16 < p). It is not a statement yet.
* 09:52Z run rtsh-sha-0952 at b-ligero-sha256 be1a3bcb, fp8-ada-x4+sha256: R1 REPRODUCED (forgery accepted by Python, Rust
  pinned and reverify PASS), R4 REPRODUCED, H2 PASS. art:0e8faae7.
* 10:15Z run rtsh-shafix-1015 at be1a3bcb + ligero-steps-pin c8a16e2b (local merge 1cfdb92f, not pushed): R1 and R4 refused,
  H2 PASS. art:57a22acb. The first attempt reused be1a3bcb's binary: the trees share one CARGO_TARGET_DIR and rsync keeps
  the older mtimes. The script now touches the sources and refuses a binary identical to be1a3bcb's. The earlier lsp and
  bls builds were real rebuilds (distinct binaries). 10:30Z handoffs to b-ligero-sha256 and the coordinator (FAIL; cells
  pulled).
* 09:46Z received `20260925T0946Z-handoff-from-coordinator.md` ("Laptop disk at 2.6 GiB: no laptop downloads, builds or new
  worktrees"); read at 10:33Z. By then I had made two worktrees (09:45Z) and pulled evidence tars. 10:35Z I deleted my
  /tmp copies (all preserved) and the 4 scratch worktrees, bringing free space from 2.7 to 4.6 GiB, and reported it in a
  checkpoint. Since then everything is pod-only: pod trees come from `git diff` applies, and only evidence of a few hundred
  KB comes back for `data put`.
* 09:57Z received `20260925T1000Z-handoff-from-coordinator.md` ("The §3.8 bit-link review moved to a new lane,
  red-team-link: drop it from your queue"). Dropped. I have no link notes; the A-GKR sha256_flat adder read is not link
  work.
* 10:35Z received blake3-80gb's `20260925T0935Z-handoff-from-blake3-80gb.md` ("FYI: A100 bf16-ampere+blake3 result on the
  fixed tree (a80ebc31)"). Same statement; covered by the main verdict.
* 10:50Z run rtsh-final-1050 on main 3301c435 (fp8-ada+blake3) and da74b03e (fp8-ada-x4+sha256). The pod trees are git diff
  applies, with blob hashes equal to ls-tree (0 of 3112 / 3116 mismatched). R1 and R4 refused, and H2 PASS, on both.
  `compress_one` vs `compress_np`: 20,000 cases, 0 mismatches; leaf_bytes(_many) vs hashlib: 256 rows, 0. art:cd2828c5.
* 11:05Z sp1-committed follow-up. The lane is FINAL at b54e42ed with no reply to 0925Z, and the fail-open is still in the
  code. I reviewed verify-night-2's `19-sp1c-verify.sh` for art:49695f7c: it closes R3 by construction (core-recomputed
  statement, `vk_pinned` True, `instance_roots` True on every rep, adopt negative). Their result is not seen yet.
* 11:30Z handoffs to the coordinator, b-ligero-sha256 and blake3-80gb (PASS on main / da74b03e).
