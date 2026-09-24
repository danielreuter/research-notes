---
lane: verify-po
kind: handoff
from: arith
created: 2026-09-24T22:26Z
---

# arith: 13 H100 results to verify independently (lane/arith 92dab0ad; fp8-hopper-v3x4 and bf16-hopper-v3x4, l=4096 p8)

All passed arith's own `reverify.py --by arith` (E4M3: custody 40/40, 13/13 proofs, 2^-128.33; BF16: 76/76, 25/25,
2^-128.05; ligero-verify sha256 f05bb9cb7fcb6405, lane/arith's backends/ligero-verify = main 22741456's) and are preserved.
Pod vy-arith-h100 (H100 80GB HBM3, US-MO-1). h8 = fp8-hopper-v3x4 local coins; h16 = bf16-hopper-v3x4 against the LIVE
same-pod verifier (niced; its own session verdicts are on the terminated pod only); h16L = bf16-hopper-v3x4 local coins.
Command: `--relation REL bench-vu --zk --mode interactive --batch 4096 --pipeline 8 --total-vus 4096 --target -128 --reps 5
--dump-reps 1` (+ `--verifier tcp://127.0.0.1:7000` for h16), LIGERO_REFERENCE_HINTS=0. Verify with ligero-verify built
from main, as for the 4090 batch (lanes/verify-po/20260924T2140Z-handoff-from-arith.md).

| tag | result (bench-result/v1) | run-files/v1 tree |
|---|---|---|
| h8-tip-r1 | art:e9ae289ce98e5148d8b6c6232a15265ce2f7ed9336981df38ecd0689788cc819 | art:db78aa36c0d220ffc3cf4dc6aceeb9b07f72db74f5fe13e49a5ffd48046d375a |
| h8-tip-r2 | art:c6271278162b3d9350736128bf7ea8969c80ee43a993617fd0a4e503ffffa844 | art:e66c0876e33eadfcc55711720c6bbe5eb0757874e2b023474937b40caff417da |
| h8-tip-r3 | art:8182f9ae4eb5f78f16bfc2faa2aa7be28baf835d395046ab1582b5542ed289a8 | art:49670a464c3f52d031909e3b5eba0fbacd208b518aca2f28cbe817997c78fe1a |
| h8-tip-r4 | art:efd871f653901528dcd22cd761359f3563878cc2d6c4a4c43c9affa61ff2ba5d | art:44157279b348f2e9a817c77986d6a592dc8980f703287fce393a30373aeddd2b |
| h8-tip-r5 | art:7a8443b4d8102a767efa8605467447ae64b540d5521abb633241aeb6c83c82cf | art:91544133b4fbc86580c7878d2d0282ae364033df64635607adf5b74624b4c23e |
| h8-tip-r6 | art:709ab20c51540d02d80cb6b44f15193ad11e4066ff69bb92a18b935ccc0dc0dd | art:7d444e586525a2dca2f52ad5aa370b8290d7914bbb1931368c7faea93247b7be |
| h16-tip-r1 | art:415d6cde28670ecc8e4bb116d204fe7492578fd2bdad0984196142f3d189e45e | art:508debf569536ce72a55fb9b331e05e4961ed74a71669d0541dc510a2ca82764 |
| h16-tip-r2 | art:b23719dd4b2d4b323f3fafddb5609bf591cb42608a4abb9f43ec17ac7a9aa449 | art:5ca5f55fd47b72417a933c9fa80e4da85f301a634e766b5d19bf83d80feccec6 |
| h16-tip-r3 | art:16feee34466b1458ff685d932b1d59660a1e54099b1df4a60323280c8a87f492 | art:71c5caca5c8e96362d2c7f214715b345682c0a0548b9c876677f42ee8c8626de |
| h16L-tip-r1 | art:e336225676820478ea8f93c1922fe17c975b326ac6d918b6d8164f95ca6f339c | art:59ad8193bf4cb92d23d2939e7942f098a39bb0d7845d92c6fc5447305dc6588b |
| h16L-tip-r2 | art:064a3a75070beaaf5ca58ac434d6b95a6ec61db2c9a2c1408f522306c7f863eb | art:4ce9ad2cb2a3c9be86f14458262143f76cd49fff8055111304a74243015155d8 |
| h16L-tip-r3 | art:593f8249c8c12285019fd55293368b97f202177a2d8eb3dc1e98c88d19409e60 | art:e955568b232df99933e54b5b6d8f53aa095cdaee20882493bed64d451a1caa9a |
| h16L-tip-r4 | art:debd7e1d6f5aef42103d9e38dbc8913b4f704821e7e6ba4a514762b4459d9829 | art:a1123912f4814d75cf7131be81ecff2ca58dac4fe5ed1fa120c6b0a0c8a934b6 |
