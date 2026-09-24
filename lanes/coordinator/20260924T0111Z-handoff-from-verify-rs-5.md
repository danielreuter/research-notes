---
lane: verify-rs-5
kind: handoff
to: coordinator (for ligerito-relation-3, which is final)
created: 2026-09-24T01:11Z
---
# verify-rs-5 -> coordinator: Rust --session takes the RO verifier's whole store; three live claims unchanged; a87edaa0

- **Tip:** `lane/verify-rs-3` @ **a87edaa0** (pushed; base 0e4ef1d1). The fix is 1ece0c34; a87edaa0 only reflows a doc comment.
  `read_record` reads a record with `subbatches` and no `batches` (`live.Session`, the `s…` ids) as zero batches on every
  statement, which is what Python `run.py verify-session --sessions-root` does. A record with `batches` is read as before,
  even if it also has `subbatches`. A record with neither key still errors ("session record: no batches"). R3-7 slot
  derivation, one batch per proof, and the whole-store claim rule are unchanged.
- **Tests** (laptop, your one-off OK): `cargo test --release` 98 pass + 1 ignored (83 lib + 9 cli + 6 session). New asserts:
  (1) a store of the fixture's four `c…` records plus a real `s…` record gives the c-only claim 2^-126.030; (2) adding a
  neither-key record fails; (3) `read_record` unit cases.
- **Binary:** `~/projects/verity-main-wt/verify-rs-3/backends/ligerito-verify/target/release/ligerito-verify` (laptop,
  macOS arm64), sha256 `4bdc3ad884a3ee72df6b8e35402615a2730727b0a48a802f34f233d833d4924b`. There is no pod build, because
  relation-3's pod is gone.
- **Whole-store claims.** Input: a fresh read-only copy of `vy-live2b-verifier-ro:/workspace/live/sessions` at 01:02Z,
  art:d04ee43a (50 sessions: 5 `c…` + 45 `s…`, all recorded; byte-identical to relation-3's 00:40Z copy). Command:
  `batch --dir <dump> --session <store>/sessions` with pinned keys only. All 3 authenticated:
  ZK `c20260924T003626Z-5aa5` **2^-128.435** (3 recorded batches on the STMT), ZK `c20260924T003234Z-a1a0` **2^-126.422**
  (3), non-ZK `c20260924T003303Z-f283` **2^-125.416** (6). These equal the c-only values; no `s…` record holds a recorded
  STMT digest. Verify JSONs, logs and the script: art:f2f27f16 (refs: store art:d04ee43a, dumps art:ef6b9392).
- Nothing left on this item. Live `--session` has still only been exercised on fp8-ada, the only relation with live records.
