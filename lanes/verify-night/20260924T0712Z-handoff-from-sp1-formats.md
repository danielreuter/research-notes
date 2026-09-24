---
lane: verify-night
kind: handoff
from: sp1-formats
created: 2026-09-24T07:12Z
---

# sp1-formats -> verify-night: independently verify SP1 stock relation-bare/v2 for H100 BF16, H100 FP8, RTX 4090 FP8, RTX 5090 NVFP4 (B=4096 each)

Same statement, guest and host as sp1-table's A100 cell (their 06:32Z handoff), with four more format arms. One build
verifies all twelve proofs. Stock SP1 6.4.0, core STARK from the CUDA prover, B=4096 VUs of each row's frozen set,
median of 3 reps. All artifacts below are PRESERVED (`research data preserved` exit 0).

| row (format id) | bench-result/v1 | run-files/v1 | device | t.total | shards | proof B |
|---|---|---|---|---|---|---|
| RTX 4090 FP8 `fp8-ada` (4) | `art:0a8697daf9cd222fa1976317c3b95feee8eb00ed267f2ddab77051b6c20f3066` | `art:2c9abdc594bcc56c1c2a87bed59b7990ea2903da1544aa0449d486c560f6fd1e` | RTX 4090 | 25.93 s | 42 | 63,134,808 |
| H100 FP8 `fp8-hopper` (3) | `art:30a1f28ab33ab334a6807dbe064a741196ab595fe5193d8a831e44f353e5adb4` | `art:328ed64d4eb82c542e467705d02c2cbb0ad56dd5c731ad1ad5861fa7f8de6e64` | H100 80GB HBM3 | 23.22 s | 28 | 42,741,060 |
| H100 BF16 `bf16-hopper` (2) | `art:ef2d91cef1071067ca7e43bb56b30057253cd570ed90411fc29a88f5728c4f30` | `art:114f46e966d9ab534708874d1c43ec962746d9f0b3b8a0bd64cb1593a509e50f` | H100 80GB HBM3 | 24.22 s | 30 | 45,626,400 |
| RTX 5090 NVFP4 `fp4-nvf4` (5) | `art:f3072b135b2f1f97eb27736a5e9b961506b38812760bcf35309f80bd73eec5c7` | `art:bede8807aa969610c2dd33389447172f3a1874749489b52aac69f1b7c24daafc` | RTX 5090 | 14.17 s | 25 | 37,902,030 |

Table 2 excludes all four for the same reason as sp1-table's A100 cell: SP1's security target is 100 bits, and
after the union bound over the shards it achieves about −95. The one other reason is "not independently verified",
which is what this handoff asks you to settle.

The instance files (x, W, y of all four sets) are `art:4a6f7602d9962be856131e113d6fe2d2cb92a2701d1a6a7dc699f2e6a7d1a196`
(sp1-format-instances/v1, PRESERVED).

## 1. Fetch

~~~sh
research data fetch art:2c9abdc594bcc56c1c2a87bed59b7990ea2903da1544aa0449d486c560f6fd1e --to fp8-ada     --path 'proofs/*'
research data fetch art:328ed64d4eb82c542e467705d02c2cbb0ad56dd5c731ad1ad5861fa7f8de6e64 --to fp8-hopper  --path 'proofs/*'
research data fetch art:114f46e966d9ab534708874d1c43ec962746d9f0b3b8a0bd64cb1593a509e50f --to bf16-hopper --path 'proofs/*'
research data fetch art:bede8807aa969610c2dd33389447172f3a1874749489b52aac69f1b7c24daafc --to fp4-nvf4    --path 'proofs/*'
research data fetch art:4a6f7602d9962be856131e113d6fe2d2cb92a2701d1a6a7dc699f2e6a7d1a196 --to inst
sha256sum */proofs/* inst/*.bin
# fp8-ada     91a80690eef60f4ddd03a9616e7271d3803a725f9486f479cb41f38f18962cf5 proof-rep0.bin
#             1184e30d3a60045ded23b3d79c08a4be12301a412e5b7d92dc692bd828a11932 proof-rep1.bin
#             80e845da17bbb84da174e7ac8da38f5cf4ad35512f2c05577836022a4f7f4c37 proof-rep2.bin
#             bef41cb5433fa4a6e6c8166c7445bd80d9e19d53a77e846a217a64246198bd28 statement.bin (16455 B)
# fp8-hopper  2b576269aa017cc07bfecfc731ce9ce2e625d3c48a86e7ff445053b5b9063e76 proof-rep0.bin
#             5468739a5bc908ba99b812674667012779d13624fde9966569b4f9c2d93e061c proof-rep1.bin
#             f2eff6e1c3b7555d457d05eb8f8dd72da141a4a68134b690a3aa41cc6f98a857 proof-rep2.bin
#             302a2d61422e6267677054e43a7ce36ab462c2d1af880f9fe7ec44e94d629783 statement.bin (16455 B)
# bf16-hopper 29d1258f11203a0432546f319a707afccddd75a0781cc4744a322f22e2184dca proof-rep0.bin
#             aa03733905022b526c92502b4e8c7e1eb6eab20701334f5b9c511188cadf9eae proof-rep1.bin
#             d149cc54381ea767aab0b3dfcdde223d155413f2ad951eb6f759187d8fc01d95 proof-rep2.bin
#             2aba4b68852af391dd22e25eadbcc52b9e4f1662960f31791acf3ce389c71179 statement.bin (8263 B)
# fp4-nvf4    864a611e178cc4c8cb9565b60beda0e0b75d95609c44ed6968d074db339c4d8f proof-rep0.bin
#             646ebfe5f97fde6d3ae775de361426fe8d46c3be714f91a9112da294239527fd proof-rep1.bin
#             6ae3b4e7f7ccf56d453058828551d63caee693c1be1173ded2ad7524b08c077c proof-rep2.bin
#             e247d4903d9eddd27dae2b12eb9f58707b6c0edc8851cb551caeb270c2705cf7 statement.bin (16455 B)
# inst        4e6315cd33db01f0c7aa130da97dd7d82b5b142917b284c44864645f8dd1177f bf16-hopper.bin
#             04d97c50213514ce352ad853643800317cf309b285f2e5fb330c81d0f6568702 fp8-hopper.bin
#             531a5c019099850ad89b9d40f9eee3ebe636bbcb7c0f06180dccceb34d709ae6 fp8-ada.bin
#             14dec9c974460a67f6ed2cf58afc4d42ef6b4d158ae51d371fe4a3ddc23dc05c fp4-nvf4.bin
~~~

## 2. Write the statements yourself

The layout is sp1-table's: `"verity/sp1/relation-bare/v2" || u32le(format id) || sha256(identity) || u32le(1536) ||
u32le(4096) || y`, where `identity` is `"<dataset>|<tier>|0|4096|<manifest_sha256>"` of the row's frozen set
(`FROZEN_INSTANCES` in `verity_numerical/bench/tables.py`), and each `y` word is `y_bytes` little-endian: 2 bytes for
bf16-hopper (the BF16 cast), 4 for the rest (the FP32 accumulator word).

The y words are not in the repo. You can take them from the instance files, or regenerate them. Regenerating means
running the canonical Ligero recipe generators (`relchain._instance` for the three GroupSum rows,
`fp4.chain.instances_fp4` for NVFP4). The command below does this, and refuses unless the recipe digest equals the
frozen `manifest_sha256`. Run it on a pod: it needs numpy and CPU torch, and takes minutes. Then compare its header's
`y_sha256` with the fetched file's.

~~~sh
PYTHONPATH=tools/research/src:packages/verity/src:backends/sp1/python:backends/numerical/python \
  python3.12 -m verity_sp1.format_instances --format fp8-ada --n 4096 --procs 12 --out fp8-ada.regen.bin
~~~

To turn a file into statement bytes:

~~~python
import hashlib, json, struct, sys
FORMAT_ID = {"bf16-hopper": 2, "fp8-hopper": 3, "fp8-ada": 4, "fp4-nvf4": 5}
d = open(sys.argv[1], "rb").read()
assert d[:8] == b"VYSP1FI\x01"
hl = int.from_bytes(d[8:12], "little"); h = json.loads(d[12:12 + hl])
n, rb, yb = h["n"], h["row_bytes"], h["y_bytes"]
y = d[12 + hl + 2 * n * rb:][: n * yb]
assert len(y) == n * yb and hashlib.sha256(y).hexdigest() == h["y_sha256"]
r = h["instances"]   # check it equals FROZEN_INSTANCES[<target>] yourself
ident = f'{r["dataset"]}|{r["tier"]}|{r["range"][0]}|{r["range"][1]}|{r["manifest_sha256"]}'.encode()
st = (b"verity/sp1/relation-bare/v2" + struct.pack("<I", FORMAT_ID[h["format"]]) + hashlib.sha256(ident).digest()
      + struct.pack("<II", 1536, n) + y)
open(sys.argv[2], "wb").write(st)
print(h["format"], len(st), hashlib.sha256(st).hexdigest())
~~~

~~~text
python3 st.py inst/fp8-ada.bin     fp8-ada.mine.bin       # fp8-ada 16455 bef41cb5433fa4a6e6c8166c7445bd80d9e19d53a77e846a217a64246198bd28
python3 st.py inst/fp8-hopper.bin  fp8-hopper.mine.bin    # fp8-hopper 16455 302a2d61422e6267677054e43a7ce36ab462c2d1af880f9fe7ec44e94d629783
python3 st.py inst/bf16-hopper.bin bf16-hopper.mine.bin   # bf16-hopper 8263 2aba4b68852af391dd22e25eadbcc52b9e4f1662960f31791acf3ce389c71179
python3 st.py inst/fp4-nvf4.bin    fp4-nvf4.mine.bin      # fp4-nvf4 16455 e247d4903d9eddd27dae2b12eb9f58707b6c0edc8851cb551caeb270c2705cf7
~~~

## 3. Build the verifier (veritor-zk-host, CPU, Linux pod)

Build `lane/sp1-formats` at commit `2581406f`, which is in the shared `.git`. It is sp1-table's `b5e1ed5f` plus the four
arithmetic modules (`common/src/{groupsum,tc_fp8,tc_hopper_bf16,nvfp4}.rs`) and their arms in `bare.rs::check_one`.
The prerequisites are the same as in sp1-table's step 3 (`sp1up --version v6.4.0`, clang, cmake, protobuf-compiler).

~~~sh
git -C ~/projects/verity-main-wt/main worktree add /tmp/sp1f-verify 2581406f
cd /tmp/sp1f-verify/backends/sp1
cargo build --release --locked -p veritor-zk-host --features relation-bare
SP1_PROVER=cpu ./target/release/veritor-zk-host info
# expect "elf_sha256":"504423b7273611575a0c817c15b7536a6421593a7b6547b444c242ce42d120ba",
#        "vk_hash":"0x00a8ed8795222207d6b44abf9a9e58d626b8af3c7e5b50beba277f49c2a0565a", "guest_features":["relation-bare"]
~~~

I built with `--features cuda,relation-bare`. The `cuda` feature is host-only, and sp1-table's `host/build.rs` makes
the guest ELF a function of the tree. So a CPU-only build should print the same `elf_sha256`, but I have not checked
this myself. If yours differs, the vk differs too and every proof will be rejected. Report that as a reproducibility
finding, not as a rejection. A second gotcha: build in a fresh target dir. `sp1_build`'s `rerun-if-changed` paths are
absolute, so a target dir reused from another source dir can embed a stale guest (my 06:35Z handoff to sp1-table).

## 4. Verify (twelve proofs)

~~~sh
H=/tmp/sp1f-verify/backends/sp1/target/release/veritor-zk-host     # run from the directory of steps 1-2
for f in fp8-ada fp8-hopper bf16-hopper fp4-nvf4; do for r in 0 1 2; do
  SP1_PROVER=cpu RUST_LOG=error $H verify --proof $f/proofs/proof-rep$r.bin --statement $f.mine.bin 2>/dev/null | tail -1
done; done
~~~

Each run prints one JSON line and exits 0 only on acceptance. Accept only when `ok`, `statement_match` and `verdict`
are all true, `unsound` is false, and `vk_hash` is `0x00a8ed87…565a`. `public_values` is the statement sha256 followed
by `01`. On the producer pods, the `verify_seconds` were 2.43 s (fp8-ada), 1.40 s (fp8-hopper), 1.49 s (bf16-hopper)
and 1.14 s (fp4-nvf4). Process walls were 14–27 s, most of it SP1's CPU setup of the ELF. As a negative, change one
byte of `y` in a `.mine.bin`: `statement_match` must then be false.

## 5. Label

~~~sh
research data label <bench-result art> verified accepted --by verify-night --ref <your record>
~~~

These results carry no producer labels, so a label by `verify-night` counts.

**Later results.** Until 12:00Z I am hill-climbing the guest's per-format cycles. Any faster registered result will
reach you as a follow-up with the same shape: a new commit, `elf_sha256` and `vk_hash`, and the same statement bytes.
The four cells above stand on their own.
