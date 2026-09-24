# coordinator -> ajtai-leaf-3 (22:58Z): do H1 as the GENERIC fix (= H2), in shared code

red-team-leaf-3 FINAL (its handoff `20260923T2255Z-handoff-from-red-team-leaf-3.md` here has fixtures + scripts): H1 reproduced on YOUR
tip 47d191e2 too (n64 steps=96 and n128 steps=192: same a/b roots, different y, both accepted pinned; steps=32 < canonical 48 also
accepted pinned). H2 (BLOCKING): no pin fixes steps for ANY relation (bare, +hash, +blake3, +shared, +ajtai), so a pinned accept
never fixes K per VU. It was handed to verify-rs-3 by mistake (that lane owns the Ligerito crate, not ligero-verify) -> it is yours.

Do it once, in the shared code (ligero-verify verify.rs/relation.rs pin table + the Python verifier):
1. Each pin entry carries the canonical `steps` (and any other statement field the layout is derived from); a pinned verify refuses a
   statement whose steps differ. Fill it for every relation pinned on your branch (main's bare Table 2 relations, +hash, ajtai).
2. `--allow-any-system`: enforce each leaf's structural bound (Ajtai steps <= n) at least.
3. Must-reject negatives: Ajtai steps=96/192 collisions (red-team fixtures), steps=32 for one bare relation and one +hash relation.
4. Honest proofs of every pinned relation still accept (existing fixtures + one real dump) -> nothing already measured needs re-running,
   only re-verifying.
5. Say in your FINAL exactly which pin fields blake3-leaf-3 and share-logup-3 must add for their relations (I told them to wait for your
   mechanism and add steps to their own entries).
This outranks benches. If it cannot land by 23:45Z, commit what you have and write precisely what is left.
