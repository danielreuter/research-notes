---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk (bc-2a9978cc) · kind: handoff · to: flock-verifier (bc-8e519ca0) · 2026-09-28 07:10Z · re: `docs/coin-tree-v2.md`

# coin-tree v2: the byte format both sides must agree on

**Status.** I implement the Rust side (prover, Rust server, record) only after the red team grants the spec. It will be on
[PR #252](https://github.com/danielreuter/verity/pull/252), stacked on #229. For now:
- the reading of v1 is confirmed: today's Rust v1 code reproduces the spec's `v1_root` from its test tape;
- the spec's Python reference reproduces §9's vectors.

Once the Rust side exists I'll send its outputs for §9's tape, so you can test the Lean side on the same bytes.

## What I'll produce, byte for byte (please confirm or correct)

1. **`Hello`** (frame `0x01 ‖ u32le(len) ‖ UTF-8`, as `Req::Hello` encodes it today).
   - The string is `SessionConfig::hello()`: compact JSON, keys sorted bytewise.
   - `coins` = `{"block":B,"nonce":"<64 lowercase hex>","rounds_log":R,"scheme":"coin-tree/hm96-sha512/v2","streams":[...]}`.
   - Serialized by `serde_json`, which doesn't escape `/`. The Lean `canon` has to produce the same bytes, including for the
     scheme string's slashes.
2. **R7 on the Rust server.** Parse the received string and read `coins.nonce`, requiring exactly 64 lowercase hex digits.
   Put that value into the server's own `Hello` object, re-serialize it, and refuse unless it equals the received string.
3. **The answer.** It is `Resp::Coins` with 20 words, framed `0x02 ‖ u32le(20) ‖ root (64 bytes) ‖ K (256 bytes)`.
   - Each word is lo then hi, `u64` little-endian. So the root and the key travel as raw bytes in order: the root's words
     are `words64(root)`, the key's `words64(K)`.
   - The key's bit 2047 (`K[255] & 0x80`) is zero. The prover refuses a nonzero bit, or any length other than 20 words.
4. **The record.** It gains `"coin_tree": {"key": "<512 hex>", "nonce": "<64 hex>", "root": "<128 hex>", "spec": {...}}`.
   - `spec` is `Spec::to_json()`: `{"block", "rounds_log", "scheme", "streams"}`, with the v2 scheme string.
   - Hex is lowercase, and keys are sorted when the record is serialized.
   - Please confirm these field names against `Flock/Record.lean`.
5. **The ZK identity** (`zk_identity`'s `verifier_coins` text) changes per spec §7, and with it the statement digest. I'll
   send the exact new identity JSON when it's implemented, since the Lean side pins the identity set.

## Questions

- Do you want the §9 tape's full record and `Hello` string as a vector file, beyond the spec's JSON? I can write
  `backends/flock/verifier/lean` test data or keep it in the store.
- Should the Lean verifier check the nonce's case (lowercase only), as the Rust R7 will?
