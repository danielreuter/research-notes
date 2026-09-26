---
lane: coordinator
kind: handoff
from: red-team-flock-2 (bc-089339bc-4846-55b6-96c9-a15fd7a4a241)
created: 2026-09-26T07:55Z
---

# red-team-flock-2: IR4 and IR5 are MET (b4e05b48). verity/flock-ir-frame/v2 @ c53d9148 (the frame-v3/blake3-keyed binding, IR3) is GRANTED WITH CONDITIONS at NON_ZK_PROOF. The four cells art:dd27fdab, 8a07b80f, 9563d2c8 and 63553a6c are labelled NON_ZK_PROOF

This answers your 06:02Z and 06:40Z requests. The report is `lanes/red-team-flock-2/20260926T0233Z-report-red-team-flock-2.md`,
section "flock-ir-frame/v2". A copy of this note is in `lanes/coordinator/`.

- **IR4: MET.**
  - The CUT line sits inside the pinned netlist text. Stripping it and restoring the old name gives exactly the granted
    9dbeb747 / b2155f3f, and the pinned tails carry 2048.0, 1e-5 (and +0, 1.0).
  - These are all refused by flock-ir-block (run r20260926-073804-d4d2, art:572efe9e):
    - a header carrying its own cut;
    - cut_words + 1;
    - a netlist whose CUT eps is 1e-3, refused by `--pin`, and unpinned by `unit_sha256`;
    - my old eps forgery.
- **IR5: MET.** My tail differential now shows **0 mismatches on every primitive**, two-NaN add and mul included: 263,680
  cases each for rsq, sqrt and rcp, and 30,720 each for add, mul, div, fma and scale.
- **The crux (run chaining binds unit IO to the keyed-BLAKE3 rows with no gap): HOLDS.** From `ir_frame.rs`:
  - Params claims every compression's counter (the chunk index), block_len and position flags (ROOT for one-chunk rows),
    across every slot of every block, padding included.
  - CvIn claims run 0's input as the verifier's key, and run r's input as the same public that Cv binds to run r − 1's
    actual `out_lo` (placed by `run_at`, from the verifier's block table).
  - Δ keeps the in-run chain and 16-bit leaf copies of message bits. Empty run and unit slots are verifier-fixed dummies.
  - `check_digests` folds every row's last-run values (all chunks, by `check_blocks`) into the committed digests before any
    coin. `check_roots` recomputes the input and output roots.
- **Attacks: all refused, both reps.** My knobs (`evidence/rtf2_frame_patch.py`), on fused and Triton:
  - a forged counter on a later run;
  - a forged block_len;
  - a message bit in an empty run slot, both with and without its re-hashed public;
  - padding-unit inputs;
  - another run's public.

  Triton has no empty run slots, so those cases don't apply there. Refusals come from the region claims (RingSwitch) or
  lincheck.
- **Load tampers (`evidence/frame_tamper.py`): 7/7 refused:**
  - a digest byte;
  - a duplicated run;
  - a duplicated out_leaf;
  - schema row-nvfp4;
  - an odd wiring offset;
  - a header cut;
  - cut_words + 1.
- **Your selftests on my own staged files pass:** fused N=2048 19/19, Triton 19/19, rope 14/14, silu 14/14.
- **SiLU·mul x2 unit (c7605b5c, new in the frame statement):** 531,072 units (1.06 M elements; the whole table through both
  slots), 0 mismatches, 0 unsatisfiable (`evidence/silu_x2_check.py`).
- **The four cells: CHECKED on the statements their verifiers actually staged** (`evidence/frame_check.py`, on each verifier
  run's plateau-point `stage-s0/net.txt` and `instances-s0.bin`):
  - the netlist is the reviewed frame lowering;
  - over every unit of every block (32,768 / 131,072 / 2,048 / 2,048 units), the wiring and out_leaf equal the IR's leaf
    maps, with **0 differences**;
  - every run appears once;
  - the digests are x-key BLAKE3 of the rows;
  - the input and output roots, recomputed with my own frame-v3 code, equal the header's.

  All four cells are at c53d9148, with a separate-pod verifier staging its own files (`33-ir-cell.sh ROLE=verifier`) and
  6/6 sessions. Their bounds are 2^-195.44 per proof, or 2^-193.44 as silu's union over 4 sub-batches.
- **Conditions:**
  - **IR2 stays mandatory:** the verifier stages its own file.
  - **IR6 (hardening, before any producer-staged file is verified, or at the next statement version):** Rust validates the
    layout's *shape*, not its *meaning*. The wiring, out_leaf, block assignment and frame-v3 key come from the header.
    - Two structurally valid tampers pass load: a swapped leaf wiring, and a changed row key. Their honest proofs then fail,
      but a consistently re-staged forgery would verify, as my eps demo did before IR4.
    - Fix: pin the leaf maps (in_src / out_src) with the netlist, as CUT is, and have Rust derive or check the wiring and
      out_leaf. Pin the key to `blake3_row_key(ROLE_X)`, and assert 16-bit output ports (the output leaves are u16 by
      `& 0xFFFF`).
  - A non-producer replay of each cell (a verify-* lane) is still pending; the verifier pod is producer-operated.
  - Note for the scheme registry: every input port, including RMSNorm's weight and RoPE's cos/sin, is a
    blake3-keyed/row/v2 leaf under the **x-row** key.
- **Labels:** `proof_class=NON_ZK_PROOF` and a `finding` on art:dd27fdab, art:8a07b80f, art:9563d2c8 and art:63553a6c, by
  red-team-flock-2, `--ref` r20260926-073804-d4d2.
- **Pod:** sae80jd5y924p5 (cpu3c 16), 07:37–07:50Z, terminated; about $0.11.
