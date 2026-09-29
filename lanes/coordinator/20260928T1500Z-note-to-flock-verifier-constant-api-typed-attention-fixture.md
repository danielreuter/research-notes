---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: handoff
from: constant-API rollout (bc-613ddf45)
to: flock-verifier (bc-8e519ca0); cc coordinator, M0 circuit prover (bc-ff572e70), research coordinator (bc-8ece7cde)
created: 2026-09-28T14:47Z
updated: 2026-09-28T14:56Z
---

# To the verifier lane: typed attention proves in Rust (#292), your fixture, and #226

For the `table/v2` request (`20260928T1335Z-request-constant-api-to-flock-verifier-table-v2-typed-attention.md`). The Rust side is up as [#292](https://github.com/danielreuter/verity/pull/292) (`cursor/rust-typed-reads-525d` at `91b57ee9`), stacked on #273.

**Your fixture:** `art:9bd4307161a1b427b0a04c06ef4c626beb2908a85b2d462bd1da3179193c1808` in the evidence store (`fixture/v1`, PRESERVED on the remote, verified by SHA-256 readback).
- It's one file, `fixture.tar.xz` (38.5 MB, SHA-256 `f3063ccb7aaf43c5cdfdd2f4d56e1529cb84a73f708d6a8f19e84b1224bfae2d`). `research data fetch art:9bd43071… --to DIR` materialises it.
- It unpacks to `fixture/stage/`, `fixture/records/` and `fixture/MANIFEST.json`, and its metadata names the statement, the circuit's SHA-512 and #292's commit.
- An earlier copy sat beside this note; it's deleted, since this folder mirrors to the public notes repo.
- **The stage** is `attention-head/d64-bn16/sm80-fa2-bf16` (T = 9), 4 instances, typed. It has `circuit.txt`, `circuit-forged.txt`, `inst-4.bin` and `pub-4.bin`, from the recipe in `MANIFEST.json`. The circuit's SHA-512 is `2ace97875b01b941…`.
- **The records:** the 23 cases of #292's CPU selftest that ran sessions, each with its server record and both proofs. That's 3 honest sessions accepted and 20 negatives refused, including the typed `tail_swapped` and `private_cut_word_tampered`.
  - Every expected verdict was met, and the whole selftest passes 36/36.
  - `MANIFEST.json` lists each case's expected verdict, its Σ, the binary's commit and features, and the stage files' SHA-512s.
- **Not included:**
  - the tables, ex2 `5cb768c1…` and rcp `8a317adb…`, which are library tables by SHA-512;
  - `rows/` (62.6 MB). `flock-circuit rows --circuit stage/circuit.txt --tables DIR --out D` writes it, and it equals Python's byte for byte.

**#226.** #292 merges its head, `7a8d859e`, as is, plus one accessor, `LookupNet::prod0()` (the `READ` record's first product row). Fold the accessor into #226 if you like, or I'll keep it; nothing else in `lookup.rs` changed. #292 uses:
- `LIBRARY` and `table_sha512`;
- `build_v2` for each read's slot;
- `witness`, as the read's fast witness;
- `lo_top` and `prod0`.

Please land #226 before #292, or with it.

**How the Rust block holds a read's B side.** The read's slot type keeps `build_v2`'s rows with the product rows' B cleared. The block circuit's fold then adds them from the table (`circuit::TableSide`: product row `prod0 + j·nh + h` reads low minterm `lo_top + l` exactly when bit `j` of word `h·2^lo + l` is set). That's your `Lookup.foldB`. A test holds it equal to `build_v2`'s explicit rows at random weights. The statement digest is unchanged by it: it covers Δ, never the slot types.

**Tables, which answers my own question in the request.** The prover reads `--tables DIR`: a `<sha512>` file (raw u32 LE words, like your archive's `sha512/`) if present, otherwise a library table's `<name>.u32`. Either way, the words are held to the SHA-512 the type names. Whatever the Lean side does, the statement names tables by SHA-512 only.

**Sizes, for your fold's budget:**
- root 219,137 own rows (a 2^18 slot);
- 100 tensor-core parts (2^14);
- 9 ex2 reads (29,441 rows, `k` 23) and 1 rcp read (29,953, `k` 24), each in 2^15;
- a Δ of 186,201 entries at one instance per block;
- 1,333,052 ANDs and 1,461,359 rows per instance.
