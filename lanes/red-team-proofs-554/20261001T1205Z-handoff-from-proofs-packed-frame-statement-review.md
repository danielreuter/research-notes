---
id: 20261001T1205Z-handoff-from-proofs-packed-frame-statement-review
campaign: overnight
lane: red-team-proofs-554
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Review the packed frame's statement now; it gates every packed GPU point

The research owner said yes to the packed frame at 4:54 AM PDT (Slack `1790855684.072569`), but no GPU point runs before
your statement review. The subject is flock-fp's `note:proofs/20261001T1200Z-handoff-from-proofs-flock-fp-packed-frame`:
- branch `cursor/proofs-flock-fp-95d4` at `238988415`, on `b45e8b187` and `deca19e50`;
- `FLOCK_PACK_WORDS=1`, with the default layout byte-identical when it's unset;
- evidence `art:ca2cc01bd51a2ab9a525540c908e111d7720a60f688a078ace009b9307a0ffcd`;
- node-1 stage-only runs at nine cells, with digests old → new in its table.

The question: does the packed unit attest the same statement up to the row layout, and is that layout's binding stated
honestly? The note's "For the statement reviewer" section says:
- the gates and ANDs are unchanged, and only the input wiring and port widths move;
- the SHA-512 over input rows hashes the tensor's own bytes, not widened u16s;
- three mismatches with core's row conventions remain: the ROLE_X / word_bits 16 prefix, whole-block padding, and FP4 as
  two rows against `nvfp4_row_bytes`' one.

CPU only. Reply GRANT or the conditions, as before, with a label on the branch head, in `lanes/proofs/` and
`lanes/proofs-flock-fp/`.

If your shell lacks the Slack, RunPod or notes tokens, `source ~/.proofs-env/env.sh` (this VM). Never print it or paste
any of its values anywhere.
