# fill-dc -> verify-night: 6 Table 2 cells (A100 BF16, H100 BF16, H100 FP8; bare + in-proof hash), 40 dumped candidates

From lane fill-dc, runner `lane/fill-dc` @ 1b3c7be6 (= lane/post-wave, no code changes), `--total-vus 4096 --target -128 --zk
--mode interactive --reps 5`, `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`, `LIGERO_REFERENCE_HINTS=0` (skips only the warm-up
sub-batch's Python reference-hints comparison; self-check and in-process verification ran). Every dir has rep 1 dumped
(`--dump-dir proofs --dump-reps 1`); every result.json is unchanged (runner `run_id` kept), registered with meta `lane: fill-dc`.
`tables.py` (render 07:35Z) rejects all 123 fill-dc results for one reason only: not independently verified.

## What I need
Reverify each row's fastest candidates (you choose how deep to go; the top one or two per cell are what Table 2 would show):
- `L-*` = LIVE runs: every rep was accepted by an independent verifier process (`live_serve.sh`, live-verifier@1b3c7be67343,
  core ligero-verify f05bb9cb7fcb6405) with fresh verifier coins, and the rep-1 dump is in the run-files tree. The session ids of
  the 5 reps are in each result.json; their verdict / rust_*.json records are in the session trees below. 140/140 sessions accepted.
  - A100: verifier = separate SECURE cpu3c pod in the same DC (EUR-IS-1, RTT 0.5-0.6 ms): sessions art:182254c0cbc80937add3331d066a394668c0c6ec51a9318fe95dd90d4a6e3fab
  - H100: NOT a separate pod. No H100 DC had a working same-DC path (CA-MTL-1 / EU-NL-1 refuse hairpin; globalNetworking timed out
    and is 100 Mbit capped; coordinator told 0648Z), so the verifier ran on the prover pod under `nice -n 19`
    (tcp://127.0.0.1:7000): sessions art:b9f8ef31713b6f08f4a1b2c4cb617890ec28c4f0bff19c1d0bdd7ede100483a8. Treat these as
    "separate process, same machine": if that is not enough independence for you, the rep-1 dump reverify is the check.
- `D-*` = local coins, dumped: the usual Rust reverify of the dump.
- Derived relations need their instance-equiv: bf16-hopper-v3x4 -> art:bfd18a1d, fp8-hopper-v3x4 -> art:0749fa9d (both already
  verified=accepted by you). The A100 bf16-ampere-v3 / -v3x4 relations read the frozen vu-k1536 set (no equivalence).
- Column 2 = v1 relations only: `--auth included-hash` fails on every derived relation (v3 / v3x4 / v2 / v2x4: "operand pins ...
  differ from the expected decode triples"; x4: "poseidon2: k = 128 words of 8 bits are not one rate block of 16 lanes").

## Store catalog: rows had gone missing (fixed for these ids)
At 07:30Z the laptop catalog (`~/.research/store/catalog.sqlite`) lacked 69 of my 165 registered artifacts and 7 of the 15
instance-equiv files (art:bfd18a1d among them), although their manifests and labels were on disk and on the remote: the
renderer then rejected every bf16-hopper-v3x4 result with "instances differ from the frozen set". A `research data reindex`
run by someone during my puts would do exactly this (`Index.rebuild` lists manifests, then deletes every row, so puts in that window
lose their rows). I re-added just those rows with `LocalStore.index.index_artifact` (the call `put_manifest` makes); no
reindex. If a render ever misses a result, check `research data sql "SELECT id FROM artifacts WHERE id='art:...'"` first.

## Candidates (fastest first per cell; overhead = native peak x t.total / (2 K B), K = 1536, B = 4096)
### A100 SXM4 80GB BF16 (first-campaign-target), B-Ligero

Flags: `--relation bf16-ampere-v3 ... --batch 16384 --pipeline 8` (L-ab-x4p4: `bf16-ampere-v3x4 --batch 4096 --pipeline 4`); equivalence: none (bf16-ampere-* read the frozen vu-k1536 set).

| run | t.total | overhead | t.total_live | bench-result | run-files |
|---|---|---|---|---|---|
| D-ab-v3p8-r2 | 0.2413 | 5.98e+06x | — (local coins) | art:e1fcf6430199b761364f182dc05ddd2b0a42664635b423c711fed57aa7a95e2f | art:48835fd7b1e979395a1c1c2a9a6a0c090037b8ae691313c36f6d52c906c65330 |
| D-ab-v3p8-r1 | 0.2512 | 6.23e+06x | — (local coins) | art:27556e563a335d138439d196348702f8ab15f6a061db880d0956a2f64714f2fe | art:acd7a51b679558e07638a11ed1a00e2b59fd55d191772a3ef0161979507888ad |
| L-ab-v3p8-r1 | 0.2788 | 6.91e+06x | 0.2946 | art:a0af06b4c2aa1145dc4222d68e399d29cbbfb6e9e89ae6dbe08f093816110cf0 | art:e4e5fff88dbfbe2eb126d4e37b72b3d0599d2f869d6c99756e7a0ff8a516d8e9 |
| L-ab-v3p8-r5 | 0.3010 | 7.46e+06x | 0.3083 | art:97f855fd65d57505b26bac7fb302aa5231ce58d6e8fd0e02c81cfc28476dae42 | art:c954c2fd67c653e9fad3e692ea4194888faa4c15d01f0f6332c5cd9986a875aa |
| L-ab-v3p8-r3 | 0.3062 | 7.59e+06x | 0.3124 | art:b01b6c31423c720290e5e197af44cdeb2da7d1fe8f71f1ba5f3a93bb02e182fa | art:0354c392647ddaf4f24fcf7c7fb5ca998781e9fc851ec8f2221974d9843c4f33 |
| L-ab-x4p4-r4 | 0.3147 | 7.80e+06x | 0.3203 | art:568a9693b375474639a38d71ac6e78b218d43fa22076e921fd9caad31cd25f53 | art:08a868a0c7088e2e7986e0a94ce52b60f79ace653a8c0aa100986a4b60e66235 |
| L-ab-x4p4-r5 | 0.3421 | 8.48e+06x | 0.3442 | art:adbed5e69f36663ca298ae38ab9421f4266f1caf026de3420f22089746983b0d | art:2e7e0f885f11fa5132ad0561ac5a51676db60e4b29829c5a894887c41af9f7f8 |
| L-ab-v3p8-r4 | 0.3681 | 9.13e+06x | 0.3753 | art:933a8a24c91f26b289da5c9ba7c80c40d1f7751e42577eb851a9a6bead5e6d33 | art:faaabd084bb10ff78b978a61d7c69779cc7543f76144a205c4918b74474e412e |
| L-ab-v3p8-r2 | 0.4791 | 1.19e+07x | 0.4963 | art:eefd3bbe998d4c69f28dc8971961c4ff9450d6b8bc8020b9ae061296fc98e50f | art:e0f96064e944fe396589c87a70eb64b778ccfa7adb6b1d0544f33203a1e774df |

### A100 SXM4 80GB BF16 (first-campaign-target), B-Ligero + in-proof hash

Flags: `--relation bf16-ampere ... --batch 16384 --pipeline 8 --auth included-hash`; equivalence: none (frozen).

| run | t.total | overhead | t.total_live | bench-result | run-files |
|---|---|---|---|---|---|
| D-ah-v1p8-r2 | 0.8965 | 2.22e+07x | — (local coins) | art:794365d36195f9b825ffbf2dbb0cc4ac4ee95fe358858622a9335d4670a75501 | art:12dc639589de2374a156a803e1e94b3ac3d8b19822ff35da81b13e975033f188 |
| D-ah-v1p8-r1 | 0.9078 | 2.25e+07x | — (local coins) | art:13163c8cc61948b52b25658c3ec06b9f146a1eb074820c40174442f1c17887da | art:bb526696ad27d891d92c7259e551ddd7dae7d3751302f1a2e997ce6747c6b205 |
| L-ah-v1p8-r4 | 0.9389 | 2.33e+07x | 0.9507 | art:c18543359b5c13c65ce494c8ea0e292731103d7b9fdcdcca706a3d22ebbcb9c4 | art:cf446094c2ac054bed0da0cfc4812697eb5977c5b0043168453acb32c23f5a18 |
| L-ah-v1p8-r5 | 0.9558 | 2.37e+07x | 0.9610 | art:7d4645dff2c8c6ce2185e1cf66ac7d50584fd802a24acf7f5371b2c65c2c0dfb | art:fd13dd7cef6e902b237612e78f1e93262e6437fffdc4d8f4c18ce68aa8853577 |
| L-ah-v1p8-r3 | 0.9925 | 2.46e+07x | 0.9992 | art:7297366944174afb0327172e39685ac35ef18d8952a2f7975ae4b8130b4afddc | art:5fedbb267e8dfdd18d76bb9e8bc8c07eee1070c05221c3de80dd3b307dd12684 |
| L-ah-v1p8-r1 | 0.9979 | 2.47e+07x | 1.0097 | art:75ff9a9a3a39422234ad6a2dedfac5ce936afb2c0a4e8b6545621c9206299c06 | art:12edcd0370aa5dcfb1343c3bdf685512af11d0ac4beffe9f5480f65daaaeea02 |
| L-ah-v1p8-r2 | 1.0552 | 2.62e+07x | 1.0629 | art:46798291e46368603c2036f0945e8c84f1832878a3eebb8698a2642e369fd2a6 | art:c0d9d0c588d3f257eb6114f16419d3ca016cc749061d9c66521bb2911ab234b2 |

### H100 SXM5 80GB BF16 (bf16-hopper-mma-draft), B-Ligero

Flags: `--relation bf16-hopper-v3x4 ... --batch 4096 --pipeline 8`; equivalence: art:bfd18a1dd63ce548a54dfc4ecfdf7577ee377b6a599d39dd75017e798b16347a (bf16-hopper-v3x4, verified=accepted 06:37Z).

| run | t.total | overhead | t.total_live | bench-result | run-files |
|---|---|---|---|---|---|
| L-b16b-x4p8-r2 | 0.1292 | 1.02e+07x | 0.1302 | art:aadcd93f51af31abd21bc687248b50b7256ee74fb960c643d108b861577467eb | art:78009ffb9bfd839024e1af29ec5d831768c3ad8ad94317c07e6abf2b83408099 |
| D-b16b-x4p8-r1 | 0.1425 | 1.12e+07x | — (local coins) | art:69602421437beb30814e83c9185f5b9171f51f43a6de55f1861fac4da82ce92c | art:24ca8cc1ce508d3b05420abd04c5d488ea956e8f21a543c8a4e800502187bffb |
| D-b16b-x4p8-r2 | 0.1426 | 1.12e+07x | — (local coins) | art:f13596d710e5db12a17426bd9754afebb7d8d1f26a8e11edfdfb722740b88305 | art:58a59bd6cada1c23fc6d17a202f52ace9f47688a0d9c0bec935596d22707cd67 |
| L-b16b-x4p8-r3 | 0.1427 | 1.12e+07x | 0.1433 | art:43f0aa12b17195a4aa7e277d529c4167669d4d7aa2a72989db3e5a5c0f6f5647 | art:2cce3d9063299f9ac1e70b9e59dc05bab489c70ed98a09206da19e8f41b88e9d |
| L-b16b-x4p8-r1 | 0.1698 | 1.33e+07x | 0.1706 | art:0767f3bbf154c2c76d22494423f28172f3101fea178329cece08c670ec26e54b | art:f1d32b98c4169161433b442a30f1b914d6b942f63d5743f7adf8cdbfeba011dc |
| L-b16b-x4p8-r4 | 0.1721 | 1.35e+07x | 0.1721 | art:a91312115c4d1a78800b3ab7f93493a66272270ffc9135d534a57237b335f5ea | art:e6b53f17ff4d16cfb59a859e96d9ef8e0c1d6078444e1a06f8e77fcf5073daa9 |

### H100 SXM5 80GB BF16 (bf16-hopper-mma-draft), B-Ligero + in-proof hash

Flags: `--relation bf16-hopper ... --batch 16384 --pipeline 8 --auth included-hash`; equivalence: none (frozen).

| run | t.total | overhead | t.total_live | bench-result | run-files |
|---|---|---|---|---|---|
| D-b16h-v1p8-r1 | 0.5428 | 4.27e+07x | — (local coins) | art:271e0e3a0d28d2c8f9dc6cc95ea8efe9baecff9060a24a0a7f7b3bca7d08a6fa | art:78ca2cc4d85d96c3ac709d5552cb44b73bccb434d053ab59450aedfe96260048 |
| D-b16h-v1p8-r2 | 0.5446 | 4.28e+07x | — (local coins) | art:13a54eba3006949c0f1ff623402480a9b5162e3e39913520e183042f90098cae | art:dc5d05f798f06b962cf0e9cc4a9b67cf008d9cca1f1b6e7c188b5d16fbf846b4 |
| L-b16h-v1p8-r2 | 0.5633 | 4.43e+07x | 0.5705 | art:8e773e253fe6002559ad947e7337689fe0351eeb5a7d0ec62b8a64c4b07fe2ab | art:19d512ad3eec26e99d9702bd225d9d679374b2e89e93d2a491a579e4e322ae69 |
| L-b16h-v1p8-r3 | 0.5746 | 4.52e+07x | 0.5789 | art:5aee69c11c48b809c9526ab851ecf0266f51facd4f4084ca56b6cbaeaa2423c3 | art:3ae52d4b45f70a3e4479a1c77ed63574979a754e67b0581cd2a3a6a156009168 |
| L-b16h-v1p8-r4 | 0.5761 | 4.53e+07x | 0.5793 | art:5674f0cc5bc192748ebef30a36f2c8c5f59b05cacd47f91ecfafe7dd25bf9bac | art:ce4afe261812bd02e08858c8ba2b2b4201aee7854d8bb5d816efed14a5753d83 |
| L-b16h-v1p8-r1 | 0.6257 | 4.92e+07x | 0.6275 | art:3f9cde9a2cf1b1de9e99d5cbed3c89cda84ef4c9a510e049738c8d44f193036d | art:3f0ec29c1345284b7dfb86cfb6f499d0e719a6b15e0b6f70cc622975b4e6123f |

### H100 SXM5 80GB FP8 (fp8-hopper-wgmma-draft), B-Ligero

Flags: `--relation fp8-hopper-v3x4 ... --batch 4096 --pipeline 8`; equivalence: art:0749fa9dcecddd0878f753f010c87f7d3cfd43e3a356a1680a4a333acbbc35c5 (fp8-hopper-v3x4, verified=accepted).

| run | t.total | overhead | t.total_live | bench-result | run-files |
|---|---|---|---|---|---|
| D-f8b-x4p8-r2 | 0.0738 | 1.16e+07x | — (local coins) | art:855697088e2ddaf67880295463f71ccd807391c1d56f32f7c0409d48c85e8895 | art:ad9dacf994a29570128f11f8a5e309cdf3c3d6c51c5176dc5a85e1ce85f3b9a9 |
| D-f8b-x4p8-r1 | 0.0743 | 1.17e+07x | — (local coins) | art:bcd7e05e25381e6fe84b51d1bf6fc26ceb510afc666295ccdf45478f542115f7 | art:29fd52d150ac8f87f8d98e02a64eed622085be42e25dc3ee2b028486cfaed34e |
| L-f8b-x4p8-r2 | 0.0824 | 1.30e+07x | 0.0833 | art:f6441ed7f40660691a5409408e15b59c955a6b5402ee3bc1cdd4607fad11ecb0 | art:82e156a8886fce6784590da0900c637da1da5e3988b18ae437ec61b7e413fff8 |
| L-f8b-x4p8-r1 (flagged) | 0.0858 | 1.35e+07x | 0.0865 | art:27c0f859490bc1fa05d09a9e6cd3191eabd2bb99716f0722e5e8550885a75b50 | art:2850ac89a43ce8c51b3d9976e710dc3e876e76a6ba16d1bb77f5aa05360a4477 |
| L-f8b-x4p8-r3 | 0.0860 | 1.35e+07x | 0.0866 | art:3ef8007dcc24dbbe6fa01a48a4a59550156f5b9266df260ded0297ca5c5b79c0 | art:bfb9b9c97a052fd9c63800b3c980ece9936486beb2d1ab281ea4ff7390ccfdef |
| L-f8b-x4p8-r4 | 0.1110 | 1.75e+07x | 0.1117 | art:0cb762b93390b76ef63b371b7df71e137e02f7d2d27e0db3dbb38ac79d21db5d | art:04b9494edb9ae3efbb8644ef0d0ef04c562fd99782cb83a75bde09304ab57a43 |

### H100 SXM5 80GB FP8 (fp8-hopper-wgmma-draft), B-Ligero + in-proof hash

Flags: `--relation fp8-hopper ... --batch 16384 --pipeline 8 --auth included-hash`; equivalence: none (frozen).

| run | t.total | overhead | t.total_live | bench-result | run-files |
|---|---|---|---|---|---|
| D-f8h-v1p8-r1 | 0.2957 | 4.65e+07x | — (local coins) | art:5387c1b55de3abcf93e78b2e03e0aea9444e7266171aea6baed6cd5c0ebd9738 | art:38a8efc24837b6987dd80bdd3ca46d4e70a1ba91818c09c3e750b65ad3a6c720 |
| D-f8h-v1p8-r2 | 0.2988 | 4.70e+07x | — (local coins) | art:26ac05126b7ed874f13d13504d266d1fa8f97e32e3d2f887c4bd6894a1b961ac | art:022e3f4985b95e318c2696373ed8e9b6b488b3b6cc7611548dbf650da4dfcb57 |
| L-f8h-v1p8-r2 | 0.2989 | 4.70e+07x | 0.3042 | art:ed9ccc81e892988e2c1226ff43c8350d9160056ef1e6a210741439b11151d03c | art:50b719926a18cfc5f775f1956e496654dbdd3c95f5faad52af2b56ce34c9a65d |
| L-f8h-v1p8-r3 | 0.2990 | 4.70e+07x | 0.3031 | art:b1758673a5067c51c8363ee40f4379137923d5007e0342dd33ee2a15eb04ea08 | art:e6770bdd8aac05fd9046b1e9243c6f00d577823c0c15c1d14e90c9796bb6a981 |
| L-f8h-v1p8-r4 | 0.3114 | 4.90e+07x | 0.3155 | art:620183954bb6b5600dd8d5fa5ff403b63e953989e17fd3d26dfff1c2867ae3bb | art:b959d61259eb4ac41ca83996a71aa6d483ffe4dfd884d4e7b7477681dde58650 |
| L-f8h-v1p8-r1 | 0.3238 | 5.09e+07x | 0.3238 | art:6c53a52504c9358f3ae78744021d07d642b55a747cb0441e874be7f69ceca80f | art:02408774f59447c2decdb7f376baf65299705800a0b071146e1de6886c84d067 |

`L-f8b-x4p8-r1` (flagged): an orphaned `30-live.sh` started it while a second one was starting, and the second one's probe of the
verifier overlapped its end, so its meta.txt has no end line and summary.txt has no row. It is valid, just possibly a little slow.

## Reproduce (reverify, as for the other B-Ligero cells)
~~~
research data fetch <run-files art> --to DIR          # result.json, log, meta.txt, proofs/ (rep 1)
# ligero-verify from backends/ligero-verify at 1b3c7be6; the relation / l / p / auth are in meta.txt and result.json
~~~
Scripts: `~/.research/notes/lanes/fill-dc/evidence/pod-scripts/` (lib.sh = the bench wrapper), `evidence/reg.sh` (registration),
every id in `evidence/registered.txt`. Report: `~/.research/notes/lanes/fill-dc/20260924T0621Z-report-fill-dc.md`.
