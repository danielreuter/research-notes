# A-GKR H100 FP8 (fp8-hopper) 0.409 s on the UNCHANGED statement (no hold): verify art:b0c27291, proofs byte-identical to the verified art:2e7baba7

From lane agkr-fp8, 01:46Z. This supersedes the 2326Z handoff (art:b1010ac8, 0.482 s): if you label one unchanged-statement H100
FP8 cell, label this one. The statement is the unmerged one (`circuits --no-merge`, circuit.txt sha256 `424e7256…`, the same as
art:2e7baba7's). All three proofs are sha256 `f80ecc53…`, the bytes verify-po accepted for art:2e7baba7 and art:438ada92. Your
0050Z hold does not apply. Only the prover changed: this lane's hill-climb plus 10 same-bytes commits cherry-picked from agkr-nvf4.

**Result**
- bench-result/v1 `art:b0c27291de3ed71c08219d428c7bca4678c0506842c959fcccb26ed70c3b1d71` (attempt r20260925-013353-ea44, PRESERVED,
  validation passed; source lane/agkr-fp8 @ a97576b5, clean). H100 80GB HBM3 reference part 28sqi5rstcudhk (Xeon 8480+, quota 23.8
  cores, thread caps 23), `fp8-hopper-wgmma-draft/2026-09-22`, relation `fp8-hopper`, frozen instances 0ff75002…; K=1536, B=4096;
  NON_ZK_PROOF_DIAGNOSTIC; 2^-130.19. t.total median 0.409 s (reps 0.416 / 0.409 / 0.409); buckets witness 0.026, commit 0.010,
  lookup 0.179, arithmetic 0.169, serialization 0.025.
- run-files/v1 `art:25c57ccb8815d411bcb985633dbcbe75ed3e3bcc11bb2916c19e1f93970e5b83`: `proofs/rep{0,1,2}.bin` (17251312 B each, sha256
  `f80ecc5321264d57d7b6036747503dbd5e10bb2e06a63f69b27a5ef6758159ab`) + `statement/`.

**Verifier**: unchanged since base main ab9573fd.

**Command** (per rep; `DIR` = `research data fetch art:25c57ccb --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 196608, steps 48, slots 2711, msgs 8912, bytes_read 17251312, ligero_rows 21576,
committed_elements 88375120 (the same as the 22:12Z and 23:26Z handoffs).

**Negatives** (dev run r20260925-013036-0815 @ a97576b5, same code, 4096 VUs): public word +1 / -1 / sign bit / exponent +1 are
rejected by both verifiers; honest is accepted. Tree `art:07b5adb8048af142ebc2f809eb02cf853c53816824debe62f1a3b2276325b653`
(ref result = art:b0c27291).

A merged-LK H100 cell on the same code (a97576b5) is recording now. It is held like art:3ae971dd (0132Z) and follows in one
more handoff.
