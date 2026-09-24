---
lane: verify-night
kind: report
created: 2026-09-24T06:22Z
status: open
---

CHECKPOINT 1b3c7be6 (09:19Z) [open] 09:19Z labelled art:7233a6a3 (SP1 k7 warm, 5/5 + neg; verdict art:72eb0459) and art:a68f2446 (tcdot hill-climb 3, own host d3a5b955/fork cbf66ccd, 3/3 + 2 neg + memory-arm reject; verdict art:17f3fa24). 61 labels total, 0 rejects. Table 2 unchanged since 09:02Z pod render (SP1 excluded by 2^-128). Inbox empty; polling every 15 min until FINAL; pod $1.45 so far.
CHECKPOINT 1b3c7be6 (09:09Z) [open] 09:09Z report body written (labels, Table 2 delta 06:25Z->09:02Z: 12 cells changed incl 3 newly filled, findings, handoffs). In flight: sp1-table 0906Z art:7233a6a3 (k7 warm) proofs+statement match, rep0 ACCEPT; sp1-tcdot hc3 art:a68f2446 host building (d3a5b955, fork cbf66ccd witness arm). Next: label both, pull evidence, FINAL.
CHECKPOINT 1b3c7be6 (08:55Z) [open] 08:56Z. LABELLED: A-GKR H100 BF16 art:c09947fd (new T2 cell; 3/3, 356/356 mutations rejected, Hopper circuit regenerated from MY tree byte-identical, public.bin == my frozen bf16-hopper y); SP1 k7 art:fffbf728 (vk 0x00dfced1). Pod render works (laptop catalog still wiped). NOW: sp1-tcdot 0841Z witness-operands arm: host building @0742a046 fork 6096d886; proofs of 174d7b4d + 76c113f4 fetched, digests + statements match.
CHECKPOINT 1b3c7be6 (08:24Z) [open] 08:28Z. LABELLED: A-GKR art:300a526a (1.351 s; T2 A100 A-GKR -> ~3.3e7x); SP1 sp1-formats@3510cfcf 4/4 (8d9df3a2, 70e5bd29, 76d13bb0, a8886e22; 12/12, vk 0x00a42aa3); SP1 sp1-table k4i 1d6aa0c3 (vk 0x00507940) + k4 c7ca70a0 (vk 0x00737e6a), 3/3 each. All handoffs to date done. LAPTOP CATALOG WIPED AGAIN (guardian disk floor kills reindex) -> coordinator 0826Z; rendering on my pod.
CHECKPOINT 1b3c7be6 (08:13Z) [open] 08:10Z. LABELLED A-GKR art:f47f8006 (agkr 0712Z append, 1.424 s; same proof bytes, 3/3 accepted, stmt == my regen). TABLE 2: A100 A-GKR 4.3e7x -> 3.5e7x (f47f8006). SP1: 3510cfcf host = elf 48bb5913/vk 0x00a42aa3, 8/16 runs done all correct; 65aa6a12 host = elf 51ca59e4/vk 0x00507940, k4i verifying; 14987d41 building. Remaining U-only cell-beaters (8, <3% faster) all NO-DUMPS.
CHECKPOINT 1b3c7be6 (07:52Z) [open] 07:56Z. r6 PASS 2/2 (fill-dc 0736Z faster: 271e0e3a H100 BF16+hash, 85569708 H100 FP8). TABLE 2 now: H100 BF16 +hash 4.4e7x -> 4.3e7x (271e0e3a); H100 FP8 cell -> 85569708 (1.2e7x, t 0.0743->0.0738). BINDING: all 11 new B-Ligero cell results BOUND to their frozen sets (A100 needed the built vu-k1536 x/W: rebuilt from my tree, 6/6 digests = committed manifest). LABELS since 07:41: sp1-formats 07:12Z set 4/4 accepted (0a8697da, 30a1f28a, ef2d91ce, f3072b13; 12/12 proofs, vk 0x00a8ed87 reproduced); sp1-tcdot art:255f4f78 accepted (3/3, vk 0x00b4876f reproduced with fork d14b4c62; elf differs, path-dependent). All pushed + labels durable. FINDING -> sp1-formats handoff 0752Z: stock host verify exits 0 on rejection (acceptance only in the JSON; host.py reads JSON, so in-tree OK). NOW: building SP1 hosts 3510cfcf (sp1-formats re-proofs, trees fetched, 12/12 digests match), 65aa6a12 + 14987d41 (sp1-table k4i/k4 0739Z). Inbox: fill-dc 0736Z done; sp1-table 0739Z + sp1-formats 0742Z in progress.
CHECKPOINT 1b3c7be6 (07:38Z) [open] 07:41Z. CATALOG FIXED: reindex after pid 50852 exited -> 5020 artifacts / 1104 attempts / 10875 labels (coordinator note 0738Z resolved). r5 PASS 6/6. TABLE 2 DELTA (render 0737Z vs 0718Z): A100 B-Ligero 1.9e7x -> 6.0e6x (e1fcf643, 0.2413 s); A100 +hash 5.2e7x -> 2.2e7x (794365d3); H100 BF16 2.0e7x -> 1.0e7x (aadcd93f); H100 BF16 +hash 7.5e7x -> 4.4e7x (8e773e25); H100 FP8 2.1e7x -> 1.2e7x (bcd7e05e); H100 FP8 +hash 8.3e7x -> 4.6e7x (5387c1b5); 4090 +hash 1.0e7x -> 9.1e6x (1abdf12a); 5090 B-Ligero 5.1e6x -> 4.5e6x (d5c9e1f3); 5090 +hash — -> 1.8e7x (99867b4c). Binding check of these 9 running. FINDING: stock SP1 host (b5e1ed5f / 2581406f) exits 0 when statement_match=false (my verdicts use the JSON fields). tcdot: 64014888+fork d14b4c62 reproduces vk 0x00b4876f -> verifying art:255f4f78; art:6e415853's recorded fork fe35cc50 does NOT reproduce that vk (0x0079e00f).
CHECKPOINT 1b3c7be6 (07:35Z) [open] 07:38Z. ALERT: laptop catalog.sqlite half-wiped since ~07:31Z (2003-2737/~5000 artifacts, 0 attempts, 0 labels; files intact) -> renders since then are wrong (handoff to coordinator 0738Z). Cause: an interrupted non-atomic reindex; my repair reindex hit 'database is locked' (pid 50852 research data preserved, fill-consumer). Will reindex when it exits. Verification unaffected: r4b PASS 4/4 (5090 col2 99867b4c + a3cc225d, 5090 bare d5c9e1f3, 4090 col2 1abdf12a); r5 running (H100 BF16 aadcd93f PASS so far); sp1-formats verifying; tcdot 64014888 host building.
CHECKPOINT 1b3c7be6 (07:27Z) [open] 07:29Z. fill-consumer 0725Z: r4 first failed (HTTP 403: runner-attempt results need attempts/ read; my RW credential lacked the prefix) -> re-minted with attempts/, r4b: 5090 col2 art:99867b4c PASS (pinned fp4-nvf4+hash, 2^-128.11), 5090 bare art:d5c9e1f3 PASS; 1abdf12a (4090 col2) and a3cc225d running. Queued r5 = fastest dump-backed fill-dc result per A100/H100 cell (no fill-dc handoff yet; U-only in the render): A100 bare e1fcf643 0.2413 (cur 0.7808), A100 col2 794365d3 0.8965 (2.1038), H100 BF16 bare aadcd93f 0.1292 (0.2525), col2 8e773e25 0.5633 (0.9514), H100 FP8 bare bcd7e05e 0.0743 (0.1342), col2 5387c1b5 0.2957 (0.5267). sp1-formats: host @2581406f reproduces elf 504423b7/vk 0x00a8ed87; 12 verifies running (fp8-ada 2/3 ok so far). Binding checks for the new cells after r5.
CHECKPOINT 1b3c7be6 (07:18Z) [open] 07:20Z. LABELLED A-GKR art:21d253bd verified=accepted (verdict art:c8364c39; proofs byte-identical to 03e21c7f's, 3/3 accepted, statement files == my regen). TABLE 2 DELTA (render 0718Z): A100 BF16 A-GKR 6.9e7x -> 4.3e7x (art:21d253bd, t.total 1.736 s). sp1-formats host building.
CHECKPOINT d7d33c0 (07:17Z) [open] 07:20Z. sp1-formats 0712Z (12 proofs, H100 BF16/FP8, 4090, 5090): my statements, y derived from MY tree's frozen loaders (relchain.instances of frozen_relation / fp4.chain.instances_fp4), equal the dumped statement.bin for all 4 formats and the producer's instance-file y; instance refs == FROZEN_INSTANCES. Host @2581406f building (fresh target dir); verify + label next. tcdot art:6e415853 (11.9 s, no handoff yet): my prebuild of its recorded commit 9491f177 gives vk 0x0079e00f.. vs recorded 0x00b4876f.. -> cannot verify from that commit; waiting for sp1-tcdot's handoff (will ask if it names 9491f177). Pod since 06:22Z at $0.48/h (~$2.95 to 12:30Z).
CHECKPOINT 89af272a (07:11Z) [open] 07:13Z. LABELLED modified-SP1 TC_DOT art:90671b80 verified=accepted (verdict art:4bfc9e7e; 3/3 reps vs my statement, statement-flip + proof-byte-flip rejected; ELF sha 8f681770 != recorded 01dbe1d9 but vk_hash identical -> reproducibility note to sp1-tcdot). r3: reverify art:65f20513 (4090 v3 0.114 s, wave-4090-2) PASS -> D2 4090 v3 now ✓. Render 0709Z: Table 2 unchanged since 0700Z (only delta today: A100 A-GKR — -> 6.9e7x). D2: A-GKR A100 ✓, 4090 v3 ✓; SP1 A100 now X only on -100 security target. Step 2 DONE: every remaining U-only result that beats a Table 2 cell has no dumps (fill-dc sweeps 'no dump'/dump=0, wave-a100-2, r23-dev-h100-2 run_files null). Pre-building tcdot host @9491f177 for art:6e415853 (11.9 s, no handoff yet); sp1-formats H100/4090/5090 results (elf 504423b7, commit null) wait for a handoff.
CHECKPOINT 1b3c7be6 (07:01Z) [open] 07:06Z. LABELLED A-GKR art:03e21c7f verified=accepted (verdict art:8fffdb23): 3/3 proofs accepted, 356/356 mutations rejected, statement files regenerated from my tree byte-identical, public.bin == frozen y. TABLE 2 DELTA (render 0700Z): A100 BF16 A-GKR — -> 6.9e7x (art:03e21c7f, t.total 2.775 s). Other cells unchanged. sp1-tcdot fork reproduces FORK_HEAD fe35cc50 / tree 6d55145f; host building.
CHECKPOINT 89af272a (06:59Z) [open] 07:02Z. LABELLED SP1 art:2a10bc89 verified=accepted (verdict art:a3b6f486; 3/3 reps vs my statement from my tree's fixture, flipped-y negative -> statement_match false; D2 only, 100-bit). r2 labels (5 fused-phases 4090) synced; re-render 06:58Z: Table 2 UNCHANGED (fb4934af 0.0907 still fastest 4090; fused-phases 0.0963 now a verified fallback). A-GKR art:03e21c7f: 3/3 proofs accepted by verity-gkr-verify built @53bd441b (8/8 tests); statement circuit/epilogue/chain regenerated from MY tree byte-identical, public.bin == frozen y; mutate negatives (356) running, label after. sp1-tcdot 0655Z: building fork verifier @572018a3 (SKIP_SERVER). fill-dc: new A100/H100 results beat cells (H100 FP8 0.0738 vs 0.1342, A100 0.4992 vs 0.7808) but are dump=0 sweeps, nothing to verify until fill-dc hands off dumped runs.
CHECKPOINT none (06:53Z) [open] 06:53Z. r2 reverify: 5/5 fused-phases 4090 results PASS (06be3b23 0.0963 v3x4, 2d685314 0.1799 frozen, 91c62994, d0789c44, 7f294d16; equivs d40f5065/574f3519 labelled 06:3xZ). SP1 host built from sp1-table b5e1ed5f reproduces elf cffc5eff/vk 0x000503d6; my statement (from my tree's frozen fixture) == dumped statement.bin; rep0 verify ok+statement_match, 1-byte-flipped y -> statement_match false; re-running reps 1-2. Next: A-GKR art:03e21c7f (build verity-gkr-verify @53bd441b on pod), re-render + delta. Inbox: agkr-table 0644Z (doing), coordinator 0646Z fused-cells (done: r2).
CHECKPOINT 1b3c7be6 (06:42Z) [open] reverify r1 5/5 PASS by verify-night: T2 H100bf16 5.2e7->2.0e7 art:44c768cd; H100fp8 5.6e7->2.1e7 art:1e73dc00; 4090 3.0e6->2.4e6 art:fb4934af; 4090+hash 1.8e7->1.0e7 art:9167ed22; 5090 9.5e6->5.1e6 art:885eec16. next: stmt-vs-frozen binding check, SP1 build
CHECKPOINT 1b3c7be6 (06:38Z) [open] 15/15 instance-equiv re-checked 3 ways (check, regen, own full-chain) -> verified=accepted (verdicts preserved). T2 4090 B-Ligero 6.6e6x->3.0e6x art:0d5b229a (equiv art:68466c4a). next: reverify U-only fastest per cell on pod
CHECKPOINT 1b3c7be6 (06:22Z) [open] 06:23Z started; pod vy-verify-night gyenhpbetf7xz8 (cpu3c 16vCPU $0.48/h) bound; next: bootstrap, re-derive 15 instance-equiv files starting art:68466c4a, then U-only candidates

# verify-night report (independent verifier, campaign morning-tables)

Base `lane/verify-night` @ 1b3c7be6; no commits (verify-night produces no code or results). Pod `vy-verify-night`
(gyenhpbetf7xz8, SECURE cpu3c, 16 vCPU / 32 GB, $0.48/h, since 06:22Z). Every pod script is in `evidence/pod-scripts/`
(numbered in the order they ran); outputs are under `/workspace/verify-night/` on the pod and copied to `evidence/`.

## Labels written (all `--by verify-night`, each with a `verification-verdict/v1` artifact as `ref`, all PRESERVED)

61 `verified=accepted` (15 equivalences, 46 bench results), none rejected. `same_device=false` goes on every result
verified outside reverify.py.

**Instance equivalences (15 `instance-equiv/v1`).** Each was re-checked three ways on the pod: `instance_equiv --check`;
regeneration from scratch compared byte for byte; and my own full-chain comparison (`05-equiv-independent.py`: both relations
drawn with no cache, every VU's `(a, b, accs)`, digests recomputed). Artifacts: art:68466c4a (fp8-ada-v2), art:d40f5065,
art:bfd18a1d (bf16-hopper-v3x4), art:0749fa9d (fp8-hopper-v3x4), art:574f3519, art:f355573b, art:f70cf39f, art:b5584b28,
art:5133f6c1, art:95df4a8e, art:9c8c306c, art:539af2c6, art:8036d0ba, art:59193d43, art:4cd768c2.

**B-Ligero, reverify.py** (Rust `ligero-verify` built on the pod from 1b3c7be6, sha256 d89cffc7…; reverify writes the verdict
and labels itself). 23 results, 6 rounds, all PASS:
- r1: art:885eec16, art:fb4934af, art:1e73dc00, art:44c768cd, art:9167ed22
- r2 (fused-phases 4090): art:06be3b23, art:2d685314, art:91c62994, art:d0789c44, art:7f294d16
- r3: art:65f20513
- r4b (fill-consumer): art:99867b4c, art:d5c9e1f3, art:1abdf12a, art:a3cc225d
- r5 (fill-dc): art:e1fcf643, art:794365d3, art:aadcd93f, art:8e773e25, art:bcd7e05e, art:5387c1b5
- r6 (fill-dc): art:271e0e3a, art:85569708

Statement binding (`08-stmt-binding.py`): for the results behind the Table 2 cells, the dumped statements' public y words
(and the operand words where the statement carries them) equal the frozen sets drawn by my tree. All BOUND: the five r1
cells, and all 11 of r4b/r5/r6. The A100 checks needed the built vu-k1536 x/W arrays: I rebuilt them from my tree's
recipe (`17-bench-instances.sh`), and all 6 match the committed manifest's sha256.

**A-GKR** (`verity-gkr-verify` built from lane/agkr-table @ 53bd441b, 8/8 tests, sha256 ee899383…; unchanged at every
producer commit). Each check: all proofs accepted with the expected counts. The statement files were regenerated from my
tree and are byte-identical. public.bin equals the frozen y drawn by my tree. Negatives: `mutate --sample 64` rejects
356/356.
- A100 BF16: art:03e21c7f, art:21d253bd, art:f47f8006, art:300a526a (all carry the same proof bytes f2c05851…)
- H100 BF16 (new cell): art:c09947fd. The Hopper circuit comes from my tree's builders at
  `Params.from_model(MODELS['hopper_bf16_m16n8k16'])`. Those modules are identical to agkr-table's at 5b3a4646; only the
  10-line `circuits()` glue is new there.

**SP1, stock** (`veritor-zk-host`, relation-bare, CPU; each host built on the pod in a fresh target dir and each reproduces
the producer's `elf_sha256` and `vk_hash`). The statement is written from my tree's frozen set and equals every dump's
statement.bin. Each check: every rep has `ok`, `statement_match`, `verdict` true and `unsound` false; flipping the last y
byte gives `statement_match` false. None of these can enter Table 2: they are 100-bit, and the security-target rule
requires 2^-128. They are for D2.
- sp1-table: art:2a10bc89 (b5e1ed5f), art:1d6aa0c3 (k4+indexed, 65aa6a12), art:c7ca70a0 (k4, 14987d41),
  art:fffbf728 (k7, 2da1e77e), art:7233a6a3 (k7 warm, 5 reps, same host; verdict art:72eb0459)
- sp1-formats @2581406f: art:0a8697da (4090), art:30a1f28a (H100 FP8), art:ef2d91ce (H100 BF16), art:f3072b13 (5090)
- sp1-formats @3510cfcf: art:8d9df3a2, art:70e5bd29, art:76d13bb0, art:a8886e22

**SP1 + TC_DOT chip (modified SP1)**. Each verdict names the fork commit, because the vk does not pin the constraint system
(finding 4 below). Each check also has a flipped-proof-byte negative (rejected).
- art:90671b80 (572018a3, fork fe35cc50) and art:255f4f78 (64014888, fork d14b4c62): memory arm.
- art:174d7b4d and art:76c113f4: witness-operands arm (0742a046, fork 6096d886, `stream-operands`, vk 0x00896ef4…). The
  memory-arm host rejects both proofs. The operand soundness caveat is written into both verdicts.
- art:a68f2446 (hill-climb 3): witness arm without `stream-operands`, its own host (d3a5b955, fork cbf66ccd, patch 0007
  only). Its vk 0x00b4876f… is the memory arm's, yet the memory-arm host rejects it ('invalid shape of proof'). Verdict
  art:17f3fa24.

## Table 2 delta (baseline = render 06:25Z, before any label of mine; now = pod render 09:02Z)

| cell | 06:25Z | now | art |
|---|---|---|---|
| A100 BF16, A-GKR | — | 3.4e7× | art:300a526a |
| A100 BF16, B-Ligero | 1.9e7× | 6.0e6× | art:e1fcf643 |
| A100 BF16, + in-proof hash | 5.2e7× | 2.2e7× | art:794365d3 |
| H100 BF16, A-GKR | — | 6.2e7× | art:c09947fd |
| H100 BF16, B-Ligero | 5.2e7× | 1.0e7× | art:aadcd93f |
| H100 BF16, + in-proof hash | 7.5e7× | 4.3e7× | art:271e0e3a |
| H100 FP8, B-Ligero | 5.6e7× | 1.2e7× | art:85569708 |
| H100 FP8, + in-proof hash | 8.3e7× | 4.6e7× | art:5387c1b5 |
| RTX 4090 FP8, B-Ligero | 6.6e6× | 2.4e6× | art:fb4934af |
| RTX 4090 FP8, + in-proof hash | 1.8e7× | 9.1e6× | art:1abdf12a |
| RTX 5090 NVFP4, B-Ligero | 9.5e6× | 4.5e6× | art:d5c9e1f3 |
| RTX 5090 NVFP4, + in-proof hash | — | 1.8e7× | art:99867b4c |

Still empty: A-GKR for H100 FP8, 4090 and 5090 (no results), and the whole SP1 column (2^-128 rule). The remaining results
the renderer rejects only as unverified that would beat a cell are 8 results, each under 3% faster. None has dumps, so
there is nothing to verify: art:300b6601, art:4eeb0b8a, art:95850cc5, art:031314e8, art:d773c7fd, art:c0459fa5,
art:cb64d2fe, art:ddaa5bf7.

## Findings (each sent to its owner)
1. **Laptop catalog wiped, twice** (coordinator 0738Z, 0826Z). `Index.rebuild` is not atomic. The first time, a reindex
   collided with a `research data preserved` lock. The second time, the guardian's disk floor (3.5 GB; the laptop was at
   3.3-3.7 GB) killed four `reindex --remote` runs from 08:13 to 08:16Z. Evict cannot free disk with a wiped catalog. Since
   then I render on the pod (`21-pod-render.sh`: seed the pod store with the laptop's manifests/attempts/labels, strip the
   macOS `._*` files, then `reindex --remote`).
2. **Lineage self-verification** (tables-fix 0700Z). `tables.producers()` ignores lane succession, so a successor lane's
   label on its predecessor's result counts as independent. Four such labels exist; none decides a Table 2 cell.
3. **Stock SP1 host exit code** (sp1-formats 0752Z). `veritor-zk-host verify` exits 0 even when it rejects (`ok` false or
   `statement_match` false); only the JSON says whether it accepted. `verity_sp1/host.py` reads the JSON, so nothing
   in-tree is affected. My verdicts read the JSON fields too.
4. **The TC_DOT vk does not pin the constraint system** (sp1-tcdot 0710Z; confirmed by sp1-tcdot 0841Z). The memory arm
   and the witness-operands arm share vk 0x00b4876f… for the same ELF. The fork commit is what identifies the constraint
   system, so every tcdot verdict names it. The memory-arm host rejects witness-arm proofs.
5. **Payload-only results** (coordinator 0655Z). Some faster B-Ligero results are registered without `--meta`, so
   tables.py ignores them while drilldown shows them.
6. reverify.py on runner-attempt results needs read access to `attempts/`: a credential scoped to objects/, manifests/ and
   labels/ fails with HTTP 403.
7. A100 binding checks need the built x/W arrays (they are not committed). `bench.instances build` rewrites
   `manifest.json`, so build into a scratch dir and link the arrays into the fixture (as pod_bootstrap's
   BENCH_INSTANCES stage does).

On contract §8 ("never write `verified=` yourself"): my launch message names this lane as the independent verifier and
tells it to write `verified accepted --by verify-night` for anything verified outside reverify.py. I read §8 as aimed at
producers. Every such label points to a preserved verdict artifact with the evidence.

## Handoffs received (all acted on)
fused-phases 0554Z (15 equivalences: done); sp1-table 0632Z (art:2a10bc89), 0739Z (art:1d6aa0c3, art:c7ca70a0),
0835Z (art:fffbf728), 0906Z (art:7233a6a3); agkr-table 0644Z (art:03e21c7f), 0712Z plus its appends (art:21d253bd,
art:f47f8006, art:300a526a), 0830Z (art:c09947fd); coordinator-fused-cells 0646Z (r2); sp1-tcdot 0655Z (art:90671b80),
0727Z (art:255f4f78), 0841Z (art:174d7b4d, art:76c113f4, art:a68f2446); sp1-formats 0712Z (4 results),
0742Z-3510cfcf (4 results); fill-consumer 0725Z (r4b); fill-dc 0736Z (r5, r6).

Handoffs sent: coordinator 0655Z, 0738Z, 0826Z; tables-fix 0700Z; sp1-tcdot 0710Z; sp1-formats 0752Z.
