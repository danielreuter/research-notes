---
id: red-team-proofs-1258/20261006T0124Z-finding-pr1258-review
campaign: proofs
lane: red-team-proofs-1258
kind: finding
status: final
repo: verity
origin: pr:1258@17cfcdae8292ef6c84c0da19430aa7cfd348a891
---
# Red team, PR #1258 (VBridge A, `FlockVBridge.sound_shaFrom`): GRANT

Reviewed 6:24 PM PDT, 5 Oct, by red-team-proofs-1258 (agent bc-8764001a-321d-58dd-a774-804d3ed1fc6a) for the proofs
coordinator. I reviewed head `17cfcdae8292ef6c84c0da19430aa7cfd348a891` of `cursor/vbridge-95d4` (base `main` `7b410fbf6`)
in a separate worktree. I ran no Lean. I ran one Python check, preserved as
`art:d5845f914b5cf34e732d6eeac2228b461037d8b3007b21984c169530c9f5f060` (`compare_sha.py` and its log). Lean paths are
relative to `verity/Security/` unless they start with `backends/`. "rec_open" means
`backends/flock/python/verity_flock/rec_open.py` on `origin/cursor/rec-step2-95d4` (`b6139d9b6`).

**Verdict: GRANT.** `shaFrom` is `rec_open._sha` operation for operation, and gate for gate on the shapes V* uses. The
statement's hypotheses can be met at every use the plan names. `Sound` is the right judgement, and the digest is the
executable verifier's `Flock.Sha512.hash`. The proof uses no unsafe construct, and the policy entries match the
`Proofs.Flock.Soundness` ones and record every definition the statement reads. None of the findings blocks the merge.

## Check 1: the restatement is the circuit. Passes

`rec_open._sha` is not on `main` or on this branch. It exists only on the unmerged recursion branches (finding 1). Its
text, `_bits` and `_Forms.compress` are identical on `rec-v0`, `rec-reprice`, `rec-step2` and `rec-step3` (checked by
`compare_sha.py`).

| step | Python | Lean | agree |
|---|---|---|---|
| message | `rec_open:190-191` `total = prefix_len + len(bits)//8`; `bits + const(_bits(pad_tail(total)))` | `VBridge/Sha.lean:30` `bits ++ (bitsOf (padTail (pre + bits.length / 8))).map Lin.const` | yes: the padding length counts the prefix bytes on both sides |
| padding | `verity/primitives/commitments/gates/sha512.py:75-78` `0x80, z = (-(L+17)) % 128 zeros, (8L) 16 bytes BE` | `Sha.lean:27` with `Hm/Hash.lean:15,18` (`lenBytes`, `zeroPad = (240 - (L+1)%128)%128`) | yes: equal for every L in [0, 2000) |
| bit order | `rec_open:183-184` bit `t` = `(data[t>>3] >> (t&7)) & 1` | `Sha.lean:23` with `Hm/Hash.lean:73` (`bitL`: `testBit (t % 8)` of byte `t / 8`) | yes |
| initial state | `rec_open:192` `const((v >> j) & 1) for v in cv for j in range(64)` | `Sha.lean:52` `(cv.map constW).flatten`, `backends/flock/verifier/lean/Flock/HmNets.lean:139` (`getLsbD i`) | yes: LSB first per word |
| blocks | `rec_open:193-197` `blk[word_bit(t)] = msg[at + t]`, `at` in steps of 1024 | `Sha.lean:34,43-47` `blk[p] = msg.getD (1024 k + wordBit p)`, `len / 1024` blocks | yes: `word_bit` (`sha512_circuit.py:41-44`) is `wordBit` (`HmNets.lean:278`) as a formula, it is an involution on [0, 1024), and ⌈len/1024⌉ = ⌊len/1024⌋ whenever the hypotheses hold (`hnb`, `Sha.lean:224`) |
| compression | `rec_open:230-232` `compress_gadget(C, cv[64i:64i+64] ×8, msg[64i:64i+64] ×16)`, flattened | `Sha.lean:38-40` `compress (words st 8) (words blk 16)`, flattened; `HmNets.lean:251-257` | yes |
| digest | `rec_open:198` `st[word_bit(t)] for t < 512` | `Sha.lean:53` `st.getD (wordBit t)` | yes |

The circuit builder agrees too. `unit_circuit` builds `Circuit()` (`rec_open:323`), whose common-subexpression table is
off by default (`verity/primitives/circuits/boolean/forms.py:55,59,85`). Lean's `HmNets.and` (`HmNets.lean:94-99`) has no
such table, and `commit`, `maj` and the constant folds mirror `forms.py` and `sha512.py:118-121`.

**Executable evidence** (`art:d5845f91…`): `compress_gadget` is run on `forms.Circuit` with rec_open's `_sha` and
`_Forms` (taken verbatim by `ast` from the branch) and with a line-by-line transcription of `shaFrom`. The two produce
the same committed bits in the same order, with the same AND operand forms and the same output forms, on 30 shapes. Each
output, evaluated on random data, is `hashlib.sha512(pre ‖ data)` in byte-string order. The shapes are:
- rows of 128, 1024 and 2048 bytes (LANES 8, 64 and 128) from the IV;
- the salt hash (192 bytes from `midstate(salt_prefix)`), the leaf (128 bytes from `midstate(leaf_prefix)`) and a node
  (128 bytes from the IV);
- 0 to 300 bytes at every padding boundary;
- a random 2-block prefix with 0 to 200 bytes.

`midstate(prefix)` equals Lean's `preCv prefix 1` (the chain from the IV over one block, unpadded) for both hm96
prefixes, and both prefixes are 128 bytes.

**Is piece D's test enough?** For soundness, yes, and nothing earlier is required for A. A wrong restatement cannot make
VBridge unsound: the theorem is about the Lean term, and D is the only link between that term and what the outer verifier
checks. Two conditions apply (finding 2): the link has to be enforced by the verifier, and an earlier guard should land
with C2.

## Check 2: the statement is not vacuous and says what the body says. Passes

- **Statement** (`Sha.lean:210-213`, record `lean-audit.json:20966`): `Sound (shaFrom cv bits (128 * np)) fun z out =>
  ∀ pre data, pre.length = 128 * np → bits.length = 8 * data.length → (∀ q < bits.length, bit z bits q = bitL data q) →
  cv = preCv pre np → out.length = 512 ∧ ∀ t < 512, bit z out t = bitL (Sha512.hash (catBytes pre data)).data.toList t`.
  This is the body's statement word for word.
- **`Sound`** (`Proofs/Flock/Soundness/Discharge/Hm/Gadget.lean:53-54`): for every start state, the rows only grow, and
  every `z` under which all the final rows hold satisfies `P`. It quantifies over every start state, so it composes inside
  D's layouts. The hypotheses come after `z` and constrain only `pre`, `data` and `cv`. For any `z`, the `data` read off
  `bits` under `z` meets the bit hypothesis, so the conclusion is never vacuous.
- **Uses.** Every case is `pre.length = 128·np` with `bits` in byte-string order:
  - row digest: `rec_open:210`, `_sha(IV, row, 0)`, so np = 0 and `preCv [] 0` is `Sha512.iv` (`Sha.lean:142`);
  - salt hash: `rec_open:212`, `_sha(salt_mid, y, len(salt_prefix) = 128)`. Here np = 1 and `pre` is
    `Hm96.Default512.saltPrefix = pad saltTag 128` (`backends/flock/verifier/lean/Flock/Hm96.lean:123`), and
    `preCv saltPrefix 1` unfolds to `HmNets.saltMid` (`HmNets.lean:327-328`);
  - leaf: `rec_open:213`, `_sha(leaf_mid, b + c, 128)`, np = 1, with `leafPrefix` (`Hm96.lean:64,124`), 128 bytes;
  - tree node: `rec_open:218`, `_sha(IV, left + right, 0)`, np = 0.
  The Python IV (`sha512.py:36-37`) is Lean's `Sha512.iv` (`backends/flock/verifier/lean/Flock/Hash.lean:97-98`).
- **The digest is the verifier of record's.** `Flock.Sha512.hash` (`backends/flock/verifier/lean/Flock/Hash.lean:141-153`)
  is the hash the verifier of record uses for nodes, row leaves, the salt digest and the tree leaf (`Flock/Merkle.lean:36,41-42`,
  `Flock/Hm96.lean:80,130-132`). `hash_eq` (`Hm/Hash.lean:34-38`, by `rfl` after unfolding) ties `padData`, `chain` and
  `digestOf` to it, so the theorem's SHA-512 is the executable one. The proof reads the spec-level `compressV` only
  internally, through `chainV_succ` (`Hm/Slot.lean:95`), and the statement does not mention it.

## Check 3: the proof is clean. Passes

`VBridge/` and `VBridge.lean` contain no `sorry`, `axiom`, `native_decide`, `implemented_by`, `extern`, `unsafe`, `opaque`,
attribute or `set_option`. Attempt `r20261006-001532-e32d` (`audit.py --build --update --no-replay --no-runs`, tree
`e6d0dde5e`) passed both packages with axioms `propext`, `Classical.choice` and `Quot.sound`. It printed one new
guarantee and only new definition records, and no changed record. The head differs from that tree in two ways: the
module doc of `Sha.lean` (finding 3), and main's merge (`verity/Security/Proofs/lean-audit.json` run paths, a PoUS hash
manifest), which has no Lean source.

## Check 4: the policy entries are honest. Passes

- `meaning` gains `Proofs.Flock.VBridge` (`lean-audit.json:56`). `reads_exempt` gains it with the reason the
  `Flock`, `Proofs.Flock.Verifier`, `Level3` and `Soundness` entries carry (`lean-audit.json:231`). Both entries are
  written the way the `Proofs.Flock.Soundness` ones are.
- The record holds every definition the statement reads, so a later edit prints as a changed definition:
  - `reads["Proofs.Flock.VBridge.Sha"]` (`lean-audit.json:73780`): `shaFrom`, `preCv`, `catBytes`, `shaMsg`, `padTail`,
    `bitsOf`, `blockAt`, `shaBlock`, `shaBlocks`;
  - new records: `Sound`, `chainV`, `lenBytes` and `zeroPad`;
  - already on main: `Flock.HmNets` (`compress`, `wordBit`, `constW`, `words`, `and`, `commit`, `maj`, `fresh`, `symm`, …),
    `Flock.Hash` (`Sha512.hash`, `iv`, `k`, `compress`), `bit`, `bv` and `valN` from `Hm/Word`, and `ev`, `stHolds` and
    `rowHolds` from `Hm/Gadget`.
- The `Gadget` and `Hash` module digests change only because `Sound`, `lenBytes` and `zeroPad` join the recorded set. No
  other guarantee's record changes. The exemption hides nothing here, because the module is also under `meaning`.
  `audit.py` would not have caught it otherwise (finding 4).

## Findings

1. **Non-blocking. The Python the restatement mirrors is not on `main`.** `rec_open.py` exists only on `rec-v0`,
   `rec-reprice`, `rec-step2` and `rec-step3`, so `Sha.lean:6`'s `verity_flock.rec_open._sha` cites a module `main` lacks.
   `_sha` is identical on all four branches today. If it changes before a recursion branch lands, A has to follow, and
   no test would say so until D exists. No fix is needed for this PR.
2. **Non-blocking. Piece D's binding has to live in the verifier, and an earlier guard should come with C2.**
   - D is sufficient for soundness only if the outer verifier enforces the binding itself. It can generate V*'s nets from
     the Lean builders and refuse any other file, as `HmNets.check` / `checkNet` do for `sha512x3` and `hm96`
     (`HmNets.lean:457-470`). Or it can pin a digest computed from the Lean layout. A CI test that compares Python's
     `circuit.txt` with the Lean term, while the verifier pins a digest taken from the Python file, leaves the link as a
     test, not a theorem.
   - D waits on #1179 and #1192, while C1 and C2 build on A's restatement. When C2 lands, add one comparison of Lean
     `recOpen LANES H` against Python `unit_circuit(LANES, H)` at a small shape. That catches drift (finding 1) long
     before D does. `art:d5845f91…` shows A agrees today.
3. **Non-blocking. No recorded run has built the head's `Sha.lean`.** The audited tree `e6d0dde5e` had a plain `/- -/`
   comment before `import`. `7a5a8c6c5` moves the import first and makes the comment a `/-! -/` module doc. No definition
   changes, but the head's file has not been compiled by any run I can find. `check`'s full audit, with replay, builds
   it before the merge.
4. **Non-blocking, in `tools/lean/audit.py`, not this PR. `reads_exempt` masks the "outside `meaning`" failure.**
   `spec_reads` skips an exempt module before it tests `meaning` (`tools/lean/audit.py:722-725`). A module listed under
   `reads_exempt` but not under `meaning` would therefore have its definitions read and never recorded, with no failure,
   and a later edit to them would print nothing. This PR lists `Proofs.Flock.VBridge` under both, so it is unaffected.
   The fix I'd suggest: exempt only from the `spec` reason, so that `meaning` is still required. That belongs to the Lean
   audit's owner.
5. **Non-blocking, cosmetic.** `wbit_chainV_toBV` (`Sha.lean:160`) proves `chainV d k = toBV (chain d k)` and has nothing
   to do with `wbit`. `chainV_eq_toBV` would read better.

## Label

`research data label pr:1258@17cfcdae8292ef6c84c0da19430aa7cfd348a891 grant red-team --by red-team-proofs-1258 --ref
note:red-team-proofs-1258/20261006T0124Z-finding-pr1258-review`
