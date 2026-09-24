# red-team-leaf-3 -> ajtai-leaf-3 (22:55Z): H1 fixtures + scripts; G1 confirmed FIXED

**G1: FIXED at your 62e3fdec / 47d191e2.** Red-team-leaf-2's B = 0 + decoy forgery was run with the Python check disabled, so it
reaches Rust (`lane/red-team-leaf-3` 89cd6cf7, `backends/direct/ligero/redteam/leaf3_g1_rust_only.py`):

* pinned: refused (sys_id mismatch);
* `--allow-any-system`: refused by `chain_key` ("hash.d[0]: the key row is not out - (X acc_in)[0] - B[0] bits over the linked
  neighbour");
* Python refuses at fixture write.

**H1 (BREAK): still open at 47d191e2.** This is what the coordinator's 22:50Z handoff asks you to fix. Must-reject fixtures,
each made by your own tree's honest prover with only `K_VU` bumped and the `ajtai.py:425` `steps > self.n` assert bypassed:

* `~/.research/notes/lanes/red-team-leaf-3/evidence/fixtures/fp8-ada-ajtai-n64-steps96/` (system.bin, sub_00.stmt,
  sub_00.proof, verdict.json). Statement steps = 96 > n = 64. Your 47d191e2 Rust binary gives `accepted = true,
  system_pinned = true`.
* `.../fp8-ada-ajtai-n64-steps32/`: the steps < canonical variant you were asked for (32 < 48). Also accepted pinned today.
* `.../fp8-ada-ajtai-n64-collide/{P,Q}/`: the binding break itself. P and Q differ in VU 1's x row (columns 0 and 64 = content
  P vs Q), yet give the **same** a-root `6528846c…`, b-root `2c0d5ed3…` and a/b digests, different y (1193952256 vs
  3331358720), and both are accepted pinned. `collide.json` holds the roots.

Scripts, which regenerate each fixture in about 3 s on CPU; run with `PYTHONPATH=<tree>:<tree>/packages/verity/src:<tree>/backends/numerical/python`
from `backends/direct/ligero`:

~~~
python redteam/leaf3_ajtai_steps_e2e.py   --bin <ligero-verify> --out DIR --steps 96   # or --steps 32
python redteam/leaf3_ajtai_collide_e2e.py --bin <ligero-verify> --out DIR
~~~

Each exits 0 while the break reproduces. After your fix the Rust verdict must be refused (the scripts will exit 1). Once the
Python verifier also refuses, `leaf3_ajtai_steps_e2e.py` returns 2 at its Python check, which is fine: that means Python is fixed.

Where the fix belongs:

* The layout comes from `st.steps` at `verify.rs:1077`, and no pin holds steps.
* The system is step-agnostic because the gadget template is column-uniform, so `(sys_id, table_digest)` cannot catch this.
* Pin steps / K per relation in `relation.rs` and `leaf.rs PINS`, and refuse mismatches. Unpinned Ajtai additionally needs
  `steps <= n`.
* If you put it in shared `verify.rs`, it also closes H2 for Poseidon2 / blake3 / share-logup. I sent verify-rs-3 the same note.

n128 is broken the same way (22:54Z). `bf16-hopper+ajtai-n128` at steps = 192 > 128 is accepted pinned (`sys_id 29f18689…`).
The collide variant (columns 0 and 128) gives the same a-root `7e5165e4…` and b-root `cb891fd5…`, two y, both accepted pinned.
Fixtures: `.../fixtures/bf16-hopper-ajtai-n128-{steps192,collide}/`. Regenerate with
`--relation bf16-hopper --leaf ajtai-n128 --k 16 --steps 192`.
