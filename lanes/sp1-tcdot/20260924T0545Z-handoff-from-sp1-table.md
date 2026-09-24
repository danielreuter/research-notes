# SP1 relation-bare/v1 statement (shared by stock SP1 and TC_DOT): 33-byte public values = sha256 digest of (instance-set id, K, B, y) || verdict

From lane sp1-table, 2026-09-24 05:45Z. Please reply by handoff if you need a change; I implement this in
`backends/sp1/common/src/bare.rs` (feature `relation-bare` of `veritor-zk-common`, which you may enable from `tcdot/`;
it only adds that module, the sound checker's ELF is untouched). Commit to follow on `lane/sp1-table` within ~1 h.

## Statement (Table 2 bare column: authentication = excluded)

Public: the instance-set identity and the output words y of B VUs. Private: every VU's x row and W row (K = 1536 BF16
words each). The guest checks `y[i] == f32_to_bf16(tc_dot chain(x_i, W_i))` for every i with exactly the semantics of
`common/src/tc.rs` / `relation_only::evaluate` (96 steps from +0, groups [8, 8], width 25, floor -132; a non-finite
operand or an intermediate saturation rejects; a saturation inside the last step is a valid +-inf output, and then
that step's second group is not examined).

## Public values (33 bytes, committed with `commit_slice`)

~~~text
digest  = sha256( b"verity/sp1/relation-bare/v1"            (27 ASCII bytes, no terminator)
                  || id                                     (32 bytes, see below)
                  || u32le(K) || u32le(B)
                  || y[0] .. y[B-1] as u16le )              (the CLAIMED words the guest read)
verdict = 0x01 if every VU is in the domain and its chain gives y[i]; else 0x00
public values = digest || verdict
~~~

`id = sha256(identity)`, `identity` = UTF-8 `"<dataset>|<tier>|<lo>|<hi>|<manifest_sha256>"`, e.g. for the Table 2
cell `bench-instances/v1|vu-k1536|0|4096|059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea`.
The guest carries `id` through (it cannot check it: x, W are private); the verifier recomputes `digest` from its own
identity string and the committed fixture `fixtures/bench-instances/v1/vu-k1536.y.u16` and accepts only
`digest || 0x01` under the pinned verifying key. A wrong y gives verdict 0x00 (tested on all 52 `vu-k1536-neg`).

## Guest input (SP1Stdin, `write_vec` buffers in this order)

1. header: `b"VYRB"` || u32le(version = 1) || u32le(K) || u32le(B) || u32le(vus_per_read) || id (32 bytes)
   || y[0..B] as u16le.  (52 + 2B bytes.)
2. ceil(B / vus_per_read) chunk buffers; chunk c holds VUs `c*vus_per_read ..` (the last may be shorter), each VU as
   `x row (K u16le) || W row (K u16le)`, i.e. 4K bytes per VU. SP1's `read_vec` buffers are 8-byte aligned.

Instance i of the frozen set is words `[1536 i, 1536 (i+1))` of `vu-k1536.x.u16` / `.w.u16` and word i of `.y.u16`.
The builder and checker functions (`bare::identity_digest`, `bare::statement_digest`, `bare::public_values`,
`bare::encode_header`, `bare::parse_header`, and the reference `bare::check_vu`) will be in common/ so both variants
hash byte-identically. You are free to use a different chunking (vus_per_read) or kernel; the public values must match.

## FYI (affects both SP1 variants' Table 2 validity)

SP1 6.x's own accounting is **100 bits** per proof: `sp1-primitives-6.6.0/src/fri_params.rs`
`SP1_TARGET_BITS_OF_SECURITY = 100` (unique-decoding FRI queries: 124 at log_blowup 2 with 16 PoW bits; KoalaBear^4,
jagged PCS). tables.py needs `security.target <= -128` and `achieved_log2 <= -128`, so every SP1 result is rejected on
security unless the user decides otherwise. I record `security.target = -100`, `achieved_log2 = -100 + log2(shards)`
(union bound over shard proofs) and tell the coordinator; suggest you record the same.
