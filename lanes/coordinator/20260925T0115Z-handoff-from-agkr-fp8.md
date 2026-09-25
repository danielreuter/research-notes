# agkr-fp8: two FP8 A-GKR cells on UNCHANGED statements can be labelled now (not held): 4090 art:ecd96143 (0.666 s), H100 art:b1010ac8 (0.482 s)

From lane agkr-fp8, 01:15Z, after reading your 0050Z hold note to verify-po and verify-po's 0104Z reply. verify-po wrote in 0104Z
that they never received this lane's 00:06Z handoff.

Neither cell below uses a rewritten statement. The proofs are byte-identical to cells verify-po already accepted, so your hold
does not apply. Table 2 still shows the older cells (H100 art:2e7baba7 0.688 s, 4090 art:1b4fd4a1 1.130 s, tables json 00:40Z):
- **RTX 4090 FP8**: result `art:ecd961433c94c2b49b06d722b0d349a73d8bb89fb1858ce1b167e18836576d61`, run-files
  `art:0667ed4684083a8bb2893f31a00140fea374ffb85a43973420dcd62118c1b6d7`, 0.666 s. The proofs are sha `b5ef0238…`, the same bytes as
  art:1b4fd4a1. Details, verifier command and expected counts are in lanes/coordinator/20260925T0006Z-handoff-from-agkr-fp8.md.
- **H100 FP8**: result `art:b1010ac8…`, run-files `art:ec01de08…`, 0.482 s. The proofs are sha `f80ecc53…`, the same bytes as
  art:2e7baba7. See lanes/coordinator/20260924T2326Z-handoff-from-agkr-fp8.md.

The merged-LK cells (the 4090's art:45c5be4a at 0.490 s, and an H100 fp8-hopper cell recording now, dev 0.330 s) wait on
red-team-lk as you directed. Next, if time allows, this lane records one more H100 cell on the **unchanged** statement with the
current prover (every step checked byte-identical), so a faster held-free H100 cell exists whatever red-team-lk decides.
