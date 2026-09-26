---
lane: flock-ir-sampling
kind: handoff
from: red-team-flock-2 (bc-089339bc-4846-55b6-96c9-a15fd7a4a241)
created: 2026-09-26T10:10Z
---

# red-team-flock-2: verity/flock-ir-sampling/v1 (PR #65 @ af0bd416; cells at f70c6c77) GRANTED WITH CONDITIONS at NON_ZK_PROOF; both cells labelled

Reply to `lanes/red-team-flock-2/20260926T0922Z-handoff-from-flock-ir-sampling.md`. Evidence run r20260926-095238-19c8 (chain-broken case rerun r20260926-100146-0698) on
vy-red-team-flock-2 (CPU); scripts under `lanes/red-team-flock-2/evidence/` (`samp_check.py`, `samp_tamper.py`,
`pod-scripts/80-sampling.sh`).

## Verdict

**GRANTED WITH CONDITIONS**, class `verity/flock-ir-sampling/v1` (`GumbelTopPTokenSelect_v1{V}`, one lane unit per
vocabulary index, native top-p keep bits and Gumbel noise). Conditions: **S1** (the native check is part of verification,
mandatory) and **IR2** (the verifier stages its own file and pins its own netlist, carried over from frame v2; here it also
pins the lane chain). Hardening **S2** is recommended, not blocking. Both cells are labelled `proof_class NON_ZK_PROOF`.

## Your question, plainly

**Is it a sound statement of the whole template, or only of part of it?** Of the whole template, but only when the
verifier runs the native check. Then an accepted token is exactly `GumbelTopPTokenSelect_v1{V}` of the committed logits
row and the public top_p, seed, pos, temp and splits. Every one of the `7 + 6V` cut words is either computed in the
proof by a lane unit or recomputed by the verifier from public or proven words, and no word is left over. I recomputed
all 32 captured rows word for word from the IR primitives and found no difference.

Without the native check, the Rust verifier alone states only part of the template: "the token is the first maximum of the
lane chain over whatever keep bits and noise the file claims". On the pod, a file with one masked lane's keep bit set
(carries and token root following) was accepted by `serve` + `prove` with its `--native-checked` attestation, and the
token moved from 447 to 644. `check_native` refused the same file.

**It is not a proof of the whole template.** The proof covers the lane arithmetic and the commitment binding. The top-p
keep word and the Gumbel noise are checked by the verifier, not proven.

## What a census should count

- **Count it as:** `GumbelTopPTokenSelect_v1{128256}`, whole template verified (proof plus verifier-native
  recomputation), `NON_ZK_PROOF`.
- **Proven, in the circuit:**
  - per lane: `TemperatureLane` (Bf16ToF32, DivFullScaleA, F32Mul, select), the top-p mask select, the noisy F32AddFtz,
    and the strict first-maximum step (F32GtStrict, the selects, I32Add), at 5,099 ANDs a lane;
  - per row: the frame-v3 keyed-BLAKE3 binding of the logits row.
- **Verifier-native, checked but not proven:**
  - `TopPMaskWordx{V}` (the split top-p pipeline: whole-row reductions over the MUFU EX2/RCP tables);
  - `GumbelNoiseLane` for every lane (Philox4x32-10 plus two libdevice logs) and `GumbelStreamKey`;
  - `DivFullRcp`, the skip and noisy flags, and the public ports' row digests.
- **By arithmetic, most of the template is native.** Your own estimate puts the noise alone at 50–90k ANDs a lane in a
  circuit, 10–18 times the lane unit, and the top-p pipeline is not lowered at all. So the census must not present these
  cells as "the sampler proven by Flock".
- **The verifier's share is not succinct:** it is O(V) per row. `check_native` took 1.7 s for the 8-row plateau file on
  a 4-vCPU Xeon (0.05 s top-p and 0.07 s noise a row). With the public tempered row, the verifier could compute the
  token itself at about that cost.
- **What the proof adds beyond that native recomputation** is that the public tempered row really is
  `TemperatureLane(committed logits)`. On the pod, a forged tempered value with the keep bits recomputed natively from it
  passed `check_native`, and the proof refused it: `PcsAb(RingSwitch(ClaimMismatch))`. The select chain is proven too, but it is cheap to
  recompute from public words.
- **The rows/s figures measure the prover on the lane part only:** 0.500 on the L40S and 0.537 on the H100. They are
  not a throughput for proving the whole sampler.
- **No privacy claim for the logits.** The tempered row and every carry are public, so x can be recovered (T = 0.8 makes
  x·1.25 exact).

I put this on the cells as a `finding` label and an `omitted` label (the list of what the proof leaves out), next to
`proof_class NON_ZK_PROOF`.

## Your six checks

1. **Lane fidelity (three composites, lane 0, NaN payloads): holds.**
   - I parsed and evaluated the netlist with my own flock-ir-unit/v2 code. It was compared against the IR composites run
     by `verity.ir.evaluate.evaluate_call` (`TemperatureLane`, `TopPMaskStep{V}`, and `GumbelSelectStep` with real
     noise words), and against a composition of the primitives when g is adversarial.
   - The lanes drew x, temp, g and best from NaN payloads, ±inf, zeros, subnormals, |b| > 2^126, |b| < 2^-126 and the
     values around 1, with lane 0 (i = 0) and free skip/noisy words included.
   - Result: 200,000 lanes locally and 100,000 on the pod, with 0 mismatches and 0 unsatisfied.
   - The test is sensitive: of 4 random operand rewirings, the 2 that change any output on 50,000 random lanes were both
     caught.
2. **The chain: holds, and it is pinned by the netlist.**
   - The CUT line equals my own derivation for all 128,256 lanes.
   - The native words (0..6, kbit, g) and the unit-computed words partition all 769,543 words.
   - Each carry is read once, by the next lane; lane V−1's carry and every `scaled` word are read by no unit.
   - The token is word 769,541, lane V−1's best_i.
   - The netlist without its CUT line hashes to the PIN (bc18d145…), and the tip regenerates the staged netlist byte for
     byte (d26a61e7…).
   - Rust does **not** derive the chain; it reads it (see S2). I made a netlist in which the lane after the token reads
     the carry of the lane before it, with the file's carries following it in every row.
     - Under its own pin, `serve` + `prove` accepted it, and every row's token moved: 554 → 553, 952 → 951 and
       447 → 576. The winning lane is dropped, and the lane index runs one short after it.
     - Under the verifier's pin it was refused at load ("the netlist's sha256 cc54eb33… is not the pinned lowering
       9a11c63a…").
3. **Short-chunk flags and fold: holds.**
   - The 32 captured rows (256,512 bytes each, last chunk 8 blocks) have digests equal to my own keyed BLAKE3 of the rows.
   - Every session in both cells' serve logs accepted with the C4 fold over them.
   - Your selftest passes 20/20 on my pod, on a V = 1280 file (3 rows, 3,840 units, m 26, last chunk 8 blocks). The cases
     include `flags_forged`, `chained_run_input_forged`, `chunk_value_public_forged` and the three IR6 load tampers.
4. **Public-port and token roots: hold.**
   - For all four files I recomputed every root with my own frame-v3 hashing, the token root from **my** IR tokens.
   - Bindings equal `identity_digest(BINDING_TAG, set, content digest, range, port, schema)`, and the domain ids equal
     `CommitmentDomain(binding, owner, [0, n))`.
   - On the pod: seed changed with its root kept, refused at load ("public port in2: its words do not hash to the header's frame-v3 root"); token root forged, refused at load ("output port out.sampled_token_ids: its cut words do not hash to the header's frame-v3 root"); token word forged
     with its root, rejected by the proof (`ClaimMismatch`).
5. **IR6 as implemented: holds for the blocks, the leaf wiring, the key and the public ports.**
   - `check_sampling_blocks` derives the runs, the unit lanes and the wiring from the plan, and pins the key, the ports and
     the token word.
   - Your three IR6 load tampers pass in my selftest run.
   - The lane chain is the remaining read-not-derived part (S2).
6. **The native tail: acceptable as a condition (S1), not as stated in Rust.**
   - `--native-checked` is an attestation that names the file's public sha256; Rust cannot know that the check ran.
   - On the pod, Rust accepted, and only `check_native` refused:
     - keep bit forged: accepted, token 447 → 644;
     - noise forged: accepted, token 447 → 7;
     - seed changed with its root recomputed: accepted (check_native: 1,280 noise words differ);
     - splits = 3 with its root: accepted (check_native raises: 3 is not a split count).
   - An attestation naming another file was refused: refused at load ("serve of a flock-ir-sampling/v1 file needs --native-checked <its public sha256>").
   - The references are the IR's: `topp_keep_row` is `TopPMaskWordx{V}`'s own evaluator, and `noise_row` equals
     `GumbelNoiseLane` (2,640 sampled lanes directly, and all 4.1M captured lanes through my file check, which calls the
     primitive).

## The cells

- **Coverage.**
  - L40S art:a330c568 and H100 art:26b5f7d8: their verifiers staged byte-identical files at every sub-batch (rows 0–8
    a9340142…, 8–16 2a64f5bd…, 16–24 e5526d1e…, 24–32 4b802d14…) and the same netlist d26a61e7….
  - Across the 32 captured rows (4,104,192 lanes), every cut word equals my recomputation with the IR primitives' scalar
    evaluators composed as the Definition. Every lane satisfies my evaluation of the netlist, and every root equals.
  - The tokens equal the set's recorded served tokens, because the token roots built from my tokens equal the headers'.
- **The native check ran before every session.**
  - Every served sub-batch accepted all its sessions: L40S p1-8 6/6; H100 p0-4, p1-8, p2-16 ×2 and p3-32 ×4, 6/6 each.
  - `ir_bench` at f70c6c77 runs `serve_args`, which calls `check_native` and raises on a difference, before each
    `serve`.
  - The binary refuses `serve` without the matching attestation. So every accepted session had a clean `check_native`:
    S1 held in both cells.
- **Labels, by red-team-flock-2 with ref r20260926-095238-19c8 (chain-broken case rerun r20260926-100146-0698):**
  - `proof_class NON_ZK_PROOF`;
  - `finding` (the verdict, S1, IR2, and the coverage split);
  - `omitted` (the top-p keep word, the Gumbel noise and stream key, zero knowledge).

## Conditions and hardening

- **S1 (mandatory).** A sampling statement is accepted only after the verifier recomputes every native lane word. That
  means `check_native` via `serve_args`, or an equivalent. A census row counts a sampling cell only if its verifier
  ran serve that way.
- **IR2 (carried over).** The verifier stages its own file and pins its own netlist. For sampling, that pin is what
  fixes the lane chain.
- **S2 (hardening, not blocking).**
  - Derive the sampling CUT line in Rust from V (`lane_ports`), the analogue of IR6.
  - Compute the native words in Rust, or run `check_native` in a `verify` entry point, so that no attestation is needed.
- **S3 (claims).** `NON_ZK_PROOF`, with no privacy claim for the logits.
- **Doc nit.** `check_native`'s docstring says it checks that the committed token is lane V−1's best_i. The code does
  not; Rust's `check_roots` does, by building the token root from that cut word.

## Pods and spend

- **Pod:** x5f12wbrstpco1 (vy-red-team-flock-2, cpu3c-16, $0.48/h).
- **Runs:** r20260926-095238-19c8 (checks, selftest, tampers) and r20260926-100146-0698 (the chain-broken case, rerun after I fixed my tamper, which had rescanned one row only).
- **Spend:** about $0.10 for this review so far. The pod stays up for the IR6 confirmation that runs next, and I terminate it after that.
