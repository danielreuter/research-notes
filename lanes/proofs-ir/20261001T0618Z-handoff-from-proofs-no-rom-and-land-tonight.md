---
id: 20261001T0618Z-handoff-from-proofs-no-rom-and-land-tonight
campaign: verity
lane: proofs-ir
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs), on Daniel's rulings (11:11 PM PDT) and circuits' split (11:16 PM PDT)
---

# Daniel: no ROM or lookup gate family. Land the IR first (target 2:05 AM PDT), then FP8/FP4, attention, MUFU

to: proofs-ir (bc-6cd83494). Thanks for `note:20261001T0612Z-reply-from-proofs-ir-boolean-estimates`.

1. **Ruling (Daniel, 11:11 PM PDT): no `Rom<n>x<w>[<sha256>]_v1`, no lookup gate, not yet.** He prefers the simplicity of
   circuits that are only AND/XOR/NOT and doesn't think lookups are a big win. Lever 3 is answered "not yet". So the MUFU
   tables (ex2, sqrt, rsqrt, rcp, the div pieces) and attention's ex2/rcp reads are built as plain Boolean circuits:
   multiplexers over constant bits. There is no "swappable for a ROM gate later" plan. You flagged the size (about
   1.1 × 10^7 refs per 2^23 table as an explicit body): find the most compact encoding the IR already allows (shared
   Definitions for the mux levels, `Const<w>` leaves, whatever keeps the descriptor and the lowering small), measure it,
   and report the size per table. If a table is truly impractical even so, say which and why, with numbers; don't add a
   gate family.
2. **Circuits' split** (`/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/internal/circuits/boolean-ir-split.md`;
   Daniel made the pure-Boolean move circuits' first priority). Proofs owns, in this order:
   - (a) **The Boolean IR on main**, target 2:05 AM PDT. Everything else waits on it: seven circuits workers branch from
     `cursor/proofs-ir-95d4` now and rebase once it lands.
   - (b) FP8 (E4M3) and FP4 (NVF4, MXF4) GEMM coordinates as Boolean.
   - (c) Attention (`Attention` / `AttentionHead` / `AttnBlock` / `Fa2InvSum` next versions over the `_v3` arithmetic).
   - (d) The MUFU tables, as in 1. Circuits' family workers call them by id; they use your builders (`fp`, `forms`,
     `softmax`), add modules beside them, never edit your files, and ask through `lanes/circuits/` for missing builders.
3. **Landing (a):**
   - **Freeze `cursor/proofs-ir-95d4` at the head you check** (your 06:11Z merge of main, `46c768b2c`, if it's the one), and
     put attention, MUFU and FP work on a new branch (for example `cursor/proofs-ir-attn-95d4`). A train needs a passing
     check of the PR's exact head, and circuits' workers need a fixed base.
   - Run `uv run --extra torch-cpu python tools/check/check.py --record --on vy-nebius-1` from a clean checkout of that head
     (it sends the upstream build for `lean-agreement`, since you touch `backends/flock/`). The TP2 MoE build that OOMs on
     your VM runs on the pod there.
   - Send me the run id and a circuit-check report for the PR body. I open the PR (draft now, from the frozen head) and ask
     @old-circuits-and-proofs for a train.
