---
lane: fill-dc
kind: report
created: 2026-09-24T06:21Z
status: open
---

CHECKPOINT 1b3c7be6 (07:17Z) [open] 07:22Z A100 live x3 done (same-DC, all accepted): bare v3p8 best 0.2788 art:a0af06b4, +hash v1p8 0.9925 art:72973669; local dumps 0.2413 art:e1fcf643 / 0.8965 art:794365d3. H100 live x3 + dumps done, r4 running; A100 live r4-5 running.
CHECKPOINT none (07:00Z) [open] 07:02Z chose: H100 fp8 v3x4p8 (~0.080) / +hash v1p8 (0.300); bf16 v3x4p8 (~0.14) / +hash v1p8 (0.545); A100 v3p8 (0.26) / +hash v1p8 (0.885). Live x3 + dumps running (A100 same-DC, H100 same-pod). 35 sweep results registered (evidence/registered.txt).
CHECKPOINT 1b3c7be6 (06:47Z) [open] 06:50Z sweeps r1 done: H100 fp8 v3x4p8 0.080/bf16 v3x4p8 0.129, +hash v1 0.310/0.547; A100 v3p8 0.235, +hash v1p8 1.01. v3/v3x4+hash unsupported. H100 live = same-pod (no hairpin DC); A100 verifier EUR-IS-1 RTT 0.6ms. art:0cb6c9fd
CHECKPOINT none (06:21Z) [open] 06:27Z started; read contract/brief/handoffs. Plan: H100 (bf16+fp8 hopper) + A100 pods SECURE with same-DC verifiers (H100 US-NE-1/EU-NL-1, A100 EUR-IS-1); sweep 2-3 cfg/col, then live x3 + dumps.
# fill-dc: B-Ligero bare + column 2 (in-proof hash) on A100 BF16, H100 BF16, H100 FP8 (campaign morning-tables)

Branch `lane/fill-dc` @ 1b3c7be6 (= lane/post-wave: fused-phases 9989797f + tables-fix b11809c1 + wave-5090 d30c32f6), worktree
`~/projects/verity-main-wt/fill-dc` (no code changes). Inbox at startup: nothing new. Scripts: `evidence/pod-scripts/`, laptop
registrar `evidence/reg.sh`, every registered result in `evidence/registered.txt`.

## Pods
| pod | id | what | DC | host / quota | $/h |
|---|---|---|---|---|---|
| vy-fill-dc-h100 | p81uubhi2ijtgr | H100 80GB HBM3 prover + same-pod verifier | EU-NL-1 | Xeon 8470 x208, quota 22.1 cores, load 20-60 | 3.49 |
| vy-fill-dc-a100 | l6viftyf7ovlpr | A100-SXM4-80GB prover | EUR-IS-1 | EPYC 7713 x255, quota 27.2 cores, load 10-70 | 1.59 |
| vy-fill-dc-a100v | hyfuszlgd7bw9y | cpu3c verifier, `live_serve.sh` LIVE_JOBS=8, tcp://157.157.221.29:36023, RTT 0.5-0.6 ms | EUR-IS-1 | EPYC 9754 x8 | 0.24 |
Short-lived (terminated within minutes): EU-NL-1 cpu3g/cpu3m verifiers ij6t6qdmyydkab / kq8oh6yax48vgf (no hairpin; one was a
loop's duplicate), CA-MTL-1 H100 wqarrsky8hww44 + A40 rsx8jb356wxgze (globalNetworking test).

## H100: no same-DC verifier possible (handoff to coordinator 0648Z)
H100 SXM SECURE stock: CA-MTL-1, EU-NL-1, EU-FR-1, AP-IN-1 only. CA-MTL-1 and EU-NL-1 refuse hairpin (EU-NL-1: prover and a
cpu3g pod behind one public IP, `Connection refused` on the mapped ports); EU-FR-1 / AP-IN-1 have no CPU pod or cheap GPU.
REST `globalNetworking: true` gives a `podnet1` (10.0.0.0/10, `<id>.runpod.internal`), but H100 <-> A40 timed out on every
port and the link is tbf-capped at 100 Mbit. Fallback: the verifier on the prover pod, `live_serve.sh` under `nice -n 19`
(LIVE_JOBS=4, SKIP_BUILD=1; live-verifier@1b3c7be67343), `--verifier tcp://127.0.0.1:7000`. kb/live-verifier.md updated.

## Column 2 composes with v1 only
`--auth included-hash` fails on every derived relation: v3 / v3x4 / v2 / v2x4 in `hashchain._private_operands` ("operand pins
... differ from the expected decode triples"), -x4 in poseidon2 ("k = 128 words of 8 bits are not one rate block of 16
lanes"; bf16: 64 words of 16 bits). So column 2 = `<base> --auth included-hash` (v1, frozen ref), l = 16384, depth swept.

## Sweep (local coins, no dumps; --reps 5, --total-vus 4096 --target -128 --zk --mode interactive, STRICT=1, LIGERO_REFERENCE_HINTS=0)
t.total per round (s); rounds alternate order; every row contract=ok.

H100 80GB HBM3 (EU-NL-1). `hd` = the column-2 depth sweep (06:55-07:02Z), separate rounds from the main sweep.
| col | relation | l | p | r1 | r2 | r3 | median |
|---|---|---|---|---|---|---|---|
| bare | **fp8-hopper-v3x4** | 4096 | **8** | 0.0798 | 0.0811 | 0.0738 | **0.0798** |
| bare | fp8-hopper-v3x4 | 4096 | 4 | 0.0884 | 0.0778 | 0.0869 | 0.0869 |
| bare | fp8-hopper (v1) | 16384 | 4 | 0.1124 | 0.1106 | 0.1520 | 0.1124 |
| +hash | fp8-hopper | 16384 | 4 | 0.3103 | 0.3118 | 0.3098 | 0.3103 |
| +hash hd | **fp8-hopper** | 16384 | **8** | 0.3001 | 0.3009 | 0.2940 | **0.3001** |
| +hash hd | fp8-hopper | 16384 | 4 | 0.3032 | 0.3079 | 0.3010 | 0.3032 |
| bare | bf16-hopper-v3x4 | 4096 | 4 | 0.1481 | 0.1465 | 0.1415 | 0.1465 |
| bare | **bf16-hopper-v3x4** | 4096 | **8** | 0.1285 | 0.5196 | 0.1424 | **0.1424** |
| bare | bf16-hopper (v1) | 16384 | 8 | 0.1784 | 0.1793 | 0.1943 | 0.1793 |
| +hash | bf16-hopper | 16384 | 8 | 0.5473 | 0.5445 | 0.5384 | 0.5445 |
| +hash hd | **bf16-hopper** | 16384 | **8** | 0.5494 | 1.0171 | 0.5445 | **0.5494** |
| +hash hd | bf16-hopper | 16384 | 4 | 0.5868 | 0.5938 | 0.5847 | 0.5868 |

A100-SXM4-80GB (EUR-IS-1; host load swung 11-70 during the sweep).
| col | relation | l | p | r1 | r2 | r3 | median |
|---|---|---|---|---|---|---|---|
| bare | **bf16-ampere-v3** | 16384 | **8** | 0.2352 | 0.2597 | 0.2764 | **0.2597** |
| bare | bf16-ampere-v3x4 | 4096 | 8 | 0.6043 | 0.4992 | 0.2479 | 0.4992 |
| bare | bf16-ampere-v3x4 | 4096 | 4 | 0.3057 | 0.2702 | 0.2503 | 0.2702 |
| +hash | bf16-ampere | 16384 | 8 | 1.0149 | 0.9958 | 0.9758 | 0.9958 |
| +hash hd | bf16-ampere | 16384 | 4 | 0.9248 | 0.9153 | 0.9285 | 0.9248 |
| +hash hd | **bf16-ampere** | 16384 | **8** | 0.8828 | 0.8899 | 0.9382 | **0.8899** |

p8 medians are noisy (a 5-rep median sometimes lands on the slow first reps of a p8 process: bf16 v3x4 p8 r2 0.52 s),
but p8 has the lower floor in every column, and Table 2 keeps the min valid `t.total`, so p8 was chosen throughout.
