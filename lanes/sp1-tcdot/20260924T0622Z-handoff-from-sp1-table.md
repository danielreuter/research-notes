# Statement update: relation-bare/v2 binds the format id (supersedes the 05:45Z layout); use `veritor_zk_common::bare` for it

Tip `lane/sp1-table @ b5e1ed5f`. The coordinator asked for one statement across all five targets, so the format is now
part of it. Everything below is in `backends/sp1/common/src/bare.rs` (feature `relation-bare`); call it rather than
re-encoding, and both SP1 variants prove byte-identical statements.

~~~text
public values   = sha256(statement bytes) || verdict            (33 bytes; verdict 1 = every VU in domain and equal to its y)
statement bytes = "verity/sp1/relation-bare/v2" || u32le(format) || id || u32le(K=1536) || u32le(B) || y[0..B] (y_bytes LE each)
id              = sha256("<dataset>|<tier>|<lo>|<hi>|<manifest_sha256>")   e.g. "bench-instances/v1|vu-k1536|0|4096|059103cf..."
format ids      = bf16-ampere 1 (A100), bf16-hopper 2, fp8-hopper 3, fp8-ada 4, fp4-nvf4 5;  y_bytes 2, 2, 4, 4, 4
guest input     = header "VYRB" || u32le(2) || u32le(format) || u32le(K) || u32le(B) || u32le(vus_per_read) || id || y,
                  then ceil(B / vus_per_read) chunks, each VU its x row then its W row (row_bytes 3072 / 3072 / 1536 / 1536 / 1632)
~~~

Guest side: `bare::parse_header`, `bare::statement_digest_le(format, &id, k, b, y_le)`, `bare::public_values(&digest, ok)`;
your TC_DOT kernel replaces `bare::check_one` for the formats you accelerate (same arguments: the VU's bytes, the same bytes
as LE u64 words, the claimed y). Host side: `bare::encode_header`, `bare::encode_chunk`, `bare::decide` (native expectation),
`bare::statement_bytes` (what `verify --statement` hashes). Negatives: `vu-k1536-neg` (52 committed; 44 in-domain whose
correct word must be accepted) and `--flip-y` on any batch.

Emitter: `benchmarks/dot_product/vector_run.py --backend sp1-bare --host <your host> --backend-name "sp1 tcdot ..."` writes
the contract result if your host speaks the same `bare-prove` JSON lines (events `execute`, `setup`, `warmup`, `rep`) and
`verify --proof P --statement S` output (`ok`, `statement_match`, `verdict`, `verify_seconds`); `bare_cmd.rs` is the reference.
Pod Python must be 3.12 (`/root/.local/bin/python3.12`).
