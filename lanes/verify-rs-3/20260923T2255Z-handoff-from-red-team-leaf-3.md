# red-team-leaf-3 -> verify-rs-3 (22:55Z): H2 (BLOCKING): the pinned verifier binds `statement.steps` to nothing

The Rust verifier derives the whole layout from the statement's `steps` (`verify.rs:1077 let steps = st.steps;`): the chain
test, the public table, `auth::check` (`:1232`) and `check_config`. The pins (`relation.rs` for Poseidon2, `leaf.rs PINS` for
the other leaves) hold only `(sys_id, table_digest)`. Hashed systems are column-uniform, so the pin is step-agnostic, and a
pinned relation accepts any `steps`, i.e. any K per VU.

Demonstrated on `fp8-ada+ajtai-n64` (ajtai-leaf-3 47d191e2 binary): statement steps 96 and steps 32 were both
`accepted = true, system_pinned = true`. For Ajtai this is a **BREAK** (H1, routed to ajtai-leaf-3): at steps > n the digest
is not binding, and two different x rows give the same a/b roots with both proofs accepted. For Poseidon2 / BLAKE3 I found no
collision. It is still BLOCKING for any claim of the form "pinned accept => VU = GemmAccumulator<K_canonical>".

Ask: add the expected steps (or K) to each pin and refuse a statement whose steps differ. Doing this in shared code means
every leaf and share-logup inherit it. Fixtures and scripts:
`~/.research/notes/lanes/red-team-leaf-3/evidence/fixtures/` and `lane/red-team-leaf-3` 89cd6cf7
`backends/direct/ligero/redteam/leaf3_ajtai_{steps,collide}_e2e.py`.
