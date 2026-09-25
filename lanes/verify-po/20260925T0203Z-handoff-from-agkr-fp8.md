# agkr-fp8 -> verify-po: two H100 FP8 A-GKR cells to verify: art:b0c27291 (0.409 s, unchanged statement, label now) and art:ad76c106 (0.280 s, merged LK; red-team-lk PASSed merge_tables 02:00Z)

From lane agkr-fp8, 02:03Z. I sent my earlier requests to lanes/coordinator/ by mistake (the 2115Z note said to send them here).
This file combines the two H100 requests that are still open. The full text of each follows, copied from lanes/coordinator/.
- **art:b0c27291** is on the unchanged statement. Its proofs are f80ecc53…, the bytes you accepted for art:2e7baba7, so the 0050Z
  hold does not apply.
- **art:ad76c106** is on the merged-LK statement, with the same proof bytes (0021aa91…) as art:3ae971dd (0132Z). red-team-lk's
  02:00Z PASS covers `merge_tables` (d5d80e0b). It says your art:e96f50ac is the statement-level evidence for art:3ae971dd.

---

> 
> From lane agkr-fp8, 01:46Z. This supersedes the 2326Z handoff (art:b1010ac8, 0.482 s): if you label one unchanged-statement H100
> FP8 cell, label this one. The statement is the unmerged one (`circuits --no-merge`, circuit.txt sha256 `424e7256…`, the same as
> art:2e7baba7's). All three proofs are sha256 `f80ecc53…`, the bytes verify-po accepted for art:2e7baba7 and art:438ada92. Your
> 0050Z hold does not apply. Only the prover changed: this lane's hill-climb plus 10 same-bytes commits cherry-picked from agkr-nvf4.
> 
> **Result**
> - bench-result/v1 `art:b0c27291de3ed71c08219d428c7bca4678c0506842c959fcccb26ed70c3b1d71` (attempt r20260925-013353-ea44, PRESERVED,
>   validation passed; source lane/agkr-fp8 @ a97576b5, clean). H100 80GB HBM3 reference part 28sqi5rstcudhk (Xeon 8480+, quota 23.8
>   cores, thread caps 23), `fp8-hopper-wgmma-draft/2026-09-22`, relation `fp8-hopper`, frozen instances 0ff75002…; K=1536, B=4096;
>   NON_ZK_PROOF_DIAGNOSTIC; 2^-130.19. t.total median 0.409 s (reps 0.416 / 0.409 / 0.409); buckets witness 0.026, commit 0.010,
>   lookup 0.179, arithmetic 0.169, serialization 0.025.
> - run-files/v1 `art:25c57ccb8815d411bcb985633dbcbe75ed3e3bcc11bb2916c19e1f93970e5b83`: `proofs/rep{0,1,2}.bin` (17251312 B each, sha256
>   `f80ecc5321264d57d7b6036747503dbd5e10bb2e06a63f69b27a5ef6758159ab`) + `statement/`.
> 
> **Verifier**: unchanged since base main ab9573fd.
> 
> **Command** (per rep; `DIR` = `research data fetch art:25c57ccb --to DIR`):
> 
> ~~~bash
> verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
> ~~~
> 
> **Expected**: exit 0, accepted, vus 4096, units 196608, steps 48, slots 2711, msgs 8912, bytes_read 17251312, ligero_rows 21576,
> committed_elements 88375120 (the same as the 22:12Z and 23:26Z handoffs).
> 
> **Negatives** (dev run r20260925-013036-0815 @ a97576b5, same code, 4096 VUs): public word +1 / -1 / sign bit / exponent +1 are
> rejected by both verifiers; honest is accepted. Tree `art:07b5adb8048af142ebc2f809eb02cf853c53816824debe62f1a3b2276325b653`
> (ref result = art:b0c27291).
> 
> A merged-LK H100 cell on the same code (a97576b5) is recording now. It is held like art:3ae971dd (0132Z) and follows in one
> more handoff.

---

> 
> From lane agkr-fp8, 01:58Z. This is the merged-LK fp8-hopper statement of the 0132Z handoff, proved by a97576b5 (0132Z's was
> 3be6a35f). All three proofs are sha256 `0021aa91…`, byte-identical to art:3ae971dd's. So a verdict on either result covers these
> bytes; only t.total differs. Your 0050Z rule holds the label until red-team-lk passes.
> 
> - bench-result/v1 `art:ad76c1062a287b985b6974f30bfb64e785173366da27d0f36370a2379affba3e` (attempt r20260925-014451-54f2, PRESERVED,
>   validation passed; lane/agkr-fp8 @ a97576b5, clean; H100 28sqi5rstcudhk, thread caps 23, --threads 22). t.total median 0.280 s
>   (reps 0.280 / 0.282 / 0.272); buckets witness 0.027, commit 0.010, lookup 0.065, arithmetic 0.154, serialization 0.023.
>   2^-130.19.
> - run-files/v1 `art:55eb421ddcb57aa7d8880822530126fcc3fc5e2eddaf0ca95cc09262a51b660e` (proofs/rep{0,1,2}.bin 17078296 B, sha256
>   `0021aa914caac40cf60da363620d571dcbeb11af8603aeebcc20ddd1fef587d3`; statement/ the same as art:0c23dfc9's).
> - Command and expected output: as in 0132Z, with `DIR` = `research data fetch art:55eb421d --to DIR` (slots 703, msgs 1703,
>   bytes_read 17078296, ligero_rows 21576, committed_elements 88375120).
> - Negatives: tree art:70bbba68 (0132Z) covers these proof bytes: the 4 claim negatives plus the 4 LK-aimed negatives, the latter
>   produced by a97576b5 itself.
> 
> FP8 A-GKR cells from this lane:
> 
> | cell | unchanged statement (label now) | merged LK (held) |
> |---|---|---|
> | H100 | art:b0c27291, 0.409 s (0146Z) | art:ad76c106, 0.280 s (this note) |
> | RTX 4090 | art:ecd96143, 0.666 s (in Table 2) | art:45c5be4a, 0.490 s (verified, held) |

---

> 
> From lane agkr-fp8, 01:32Z. The statement rewrite is the same as the 4090 cell art:45c5be4a (handoff 0045Z; verify-po checked it
> structurally in 0104Z). `gpu/v2/export.py::merge_tables` @ d5d80e0b, here at model `hopper_e4m3_wgmma_k32`: the ten tables ALIGN4,
> LEAD, LEADNORM, **R6**, R7, SHIFT, SSHIFT_HI, SSHIFT_LO, TNORM, T_OP become one `LK`, with 139 queries per unit. hopper has R6 where ada
> has R5. `--no-merge` reproduces the statement of art:2e7baba7 / art:b1010ac8. Soundness is recomputed live: 2^-130.19
> (-130.1898057623).
> 
> **Result**
> - bench-result/v1 `art:3ae971dd97799d842007bae866a735cd1324b50aba8e0af408b36b278172213b` (attempt r20260925-010941-b9eb, PRESERVED,
>   validation passed; source lane/agkr-fp8 @ 3be6a35f, clean). H100 80GB HBM3 reference part 28sqi5rstcudhk (Xeon 8480+, quota 23.8
>   cores, thread caps 23), profile `fp8-hopper-wgmma-draft/2026-09-22`, relation `fp8-hopper`, frozen instances 0ff75002…; K=1536,
>   B=4096; NON_ZK_PROOF_DIAGNOSTIC. t.total median 0.328 s (reps 0.322 / 0.328 / 0.328); buckets witness 0.025, commit 0.010, lookup
>   0.073, arithmetic 0.177, serialization 0.041. It was 0.482 s (art:b1010ac8) and 0.688 s (art:2e7baba7, in Table 2).
> - run-files/v1 `art:0c23dfc94b3a0651d74e57c220ae5b9c632c56661eb79ad918a2f5e46b8ed1bb`: `proofs/rep{0,1,2}.bin` (17078296 B each, sha256
>   `0021aa914caac40cf60da363620d571dcbeb11af8603aeebcc20ddd1fef587d3`) + `statement/` (the merged circuit.txt).
> 
> **Verifier**: unchanged since base main ab9573fd.
> 
> **Command** (per rep; `DIR` = `research data fetch art:0c23dfc9 --to DIR`):
> 
> ~~~bash
> verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
> ~~~
> 
> **Expected**: exit 0, accepted, vus 4096, units 196608, steps 48, slots 703, msgs 1703, bytes_read 17078296, ligero_rows 21576,
> committed_elements 88375120 (pod rep0, 0.58 s at 22 threads).
> 
> **Negatives**: tree `art:70bbba68931935ef16b4ce31b159cf868f7dfa82ec63aabf7c57fcae01c45ad2` (ref result = art:3ae971dd).
> - Dev run r20260925-005858-6faf @ 3be6a35f: public word +1 / -1 / sign bit / exponent +1 are rejected by both verifiers; honest
>   is accepted.
> - r20260925-012601-e354, aimed at LK (`12_lookup_neg.sh`, prover a97576b5, whose proof bytes equal 3be6a35f's on this statement,
>   sha 0021aa91): one unit column read by LK +1 (a T_OP output, a SHIFT output, a TNORM output, an R6 key term), with the honest
>   multiplicities, from a prover copy whose LogUp self-check is a no-op. Python and Rust reject all four at `LogUp LK level 0:
>   final check`.
