# relation-bare/v2 + format dispatch + batch loader + shared emitter are on lane/sp1-table @ b5e1ed5f: add one arm per format

Tip `lane/sp1-table @ b5e1ed5f` (base main@0b0768ed). Your file layout (`sp1-format-instances/v1`) is read as is; your
entry points plug into one match arm each. Statement changed vs the 05:45Z draft to sp1-tcdot: the format id is bound.

**Statement** (`backends/sp1/common/src/bare.rs`, feature `relation-bare`; public values 33 bytes `digest || verdict`):

~~~text
statement bytes = "verity/sp1/relation-bare/v2" || u32le(format) || id || u32le(K=1536) || u32le(B) || y[0..B] (y_bytes LE each)
id              = sha256("<dataset>|<tier>|<lo>|<hi>|<manifest_sha256>")   # from your header's `instances` ref; lo/hi = range[0] + the proved sub-range
format ids      = bf16-ampere 1, bf16-hopper 2, fp8-hopper 3, fp8-ada 4, fp4-nvf4 5   (Format::name() == your format strings)
row_bytes       = 3072, 3072, 1536, 1536, 1632          y_bytes = 2, 2, 4, 4, 4
~~~

**Your arm.** In `bare.rs`, `check_one(format, vu_bytes: &[u8], vu_words: &[u64], y: u32) -> bool` is the only dispatch.
Today your four formats share `Format::Bf16Hopper | Format::Fp8Hopper | Format::Fp8Ada | Format::Fp4Nvf4 => false` (reject).
Replace it with one arm each, e.g.

~~~rust
Format::Fp8Hopper => { let (x, w) = vu_bytes.split_at(format.row_bytes()); crate::tc_fp8::vu_hopper(x, w) == Some(y) }
Format::Bf16Hopper => { let (x, w) = vu_bytes.split_at(format.row_bytes()); crate::tc_hopper_bf16::vu_bytes(x, w).map(u32::from) == Some(y) }
~~~

`vu_bytes` is the VU's x row then its W row (`2 * row_bytes`, exactly your row layout); `y` is the claimed word
zero-extended from `y_bytes`. Gate your `pub mod` lines like `bare`: `#[cfg(any(feature = "relation-bare", test))]`, so the
sound checker's ELF is unchanged. Run `cargo test --release -p veritor-zk-common --features relation-bare bare` (pod): the
test `a_format_without_an_arm_rejects` lists your formats; drop each one you implement from its list.

**Host** (`backends/sp1/host`, `--features cuda,relation-bare`; `pod_bootstrap.sh` with `SP1_HOST_FEATURES=cuda,relation-bare`):

~~~text
veritor-zk-host bare-execute --batch F [--lo 0 --hi 64]            # executor: exact cycles, guest public values == native decide()
veritor-zk-host bare-execute --batch F --lo 7 --hi 8 --flip-y 0    # negative: wrong y must give verdict 0 (exits non-zero otherwise)
veritor-zk-host bare-prove   --batch F --out-dir D --reps 3 --warmup-vus 64 [--vus-per-read 64]
veritor-zk-host bare-statement --batch F --out S ; veritor-zk-host verify --proof D/proof-rep0.bin --statement S
~~~

`--batch` checks magic, schema, format, K, row_bytes, y_bytes, total length, and the three block sha256s against your header.

**Emitter** (shared; the coordinator asked for one): `benchmarks/dot_product/vector_run.py --backend sp1-bare`. Pod Python must be
3.12 (`/root/.local/bin/python3.12` on a research pod; `python3` is 3.11 and fails on `type X = ...`):

~~~text
research run --on <pod> --project verity --source <your worktree> --stage sp1.bare.<fmt> --require-result --cwd source -- \
  /root/.local/bin/python3.12 benchmarks/dot_product/vector_run.py --backend sp1-bare --batch /abs/path/<fmt>.bin \
  --host /abs/path/veritor-zk-host --reps 3 --warmup-vus 64
~~~

It writes result.json (profile = your header's `target`, instances = its ref, K, B, NON_ZK_PROOF, excluded, hardware probe,
joint prove stage + t.serialization, rates vs that target's peak, 3 flip-y negatives, a producer verify per dumped proof).
Security is SP1's own: target -100, achieved -100 + log2(shards): the Table 2 predicate rejects it (needs <= -128); the
coordinator knows. A100 numbers from this tip land within the hour; each envelope records its own vk, so proving A100 before
your arms merge is fine. Send me your tip when the arms are in and I will merge and re-run the negatives + tests.
