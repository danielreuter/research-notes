# fused-phases -> verify-night: re-derive the 15 instance-equiv/v1 files, then label them (the producer must not)

From lane fused-phases, tip `9989797f` (lane/fused-phases, pushed). The files say whether the derived B-Ligero relations
(`-v2 -v3 -v2x4 -v3x4 -x4` of fp8-ada, bf16-hopper, fp8-hopper) prove the same numbers as their target's frozen set (BRIEF
§5). All 15 have `equal: true`. Each was registered with `--meta '{"lane": "fused-phases", ...}'`, the producer name
tables-fix reads.

## Reproduce

The loaders are the runner's (`backends.direct.ligero.relchain` imports torch), so run on any pod with the tip. A 4090
pod does all 15 in ~40 s of CPU.

~~~
research pods sync <pod>          # from a worktree at 9989797f (or later on lane/fused-phases)
research pods ssh <pod>           # then: bash /workspace/src/backends/direct/ligero/pod_bootstrap.sh; source /workspace/env.sh
cd /workspace/src
# (a) check the registered files: fetch them (laptop: research data fetch ART --to DIR, then copy over), then
$PY -m verity_numerical.bench.instance_equiv --check DIR/*.json
#     -> per file "<relation> reproduces; equal=True"; exit 0 iff every file reproduces field for field (except "tool")
# (b) or regenerate from scratch and compare the digests:
$PY -m verity_numerical.bench.instance_equiv --out-dir OUT \
    $(for b in fp8-ada bf16-hopper fp8-hopper; do for s in v2 v3 v2x4 v3x4 x4; do echo --relation $b-$s; done; done)
~~~

`--check` finds the candidate relation from the file's `candidate` ref, then re-derives the whole document. It loads the
frozen side with the registered relation whose runner ref is `tables.FROZEN_INSTANCES[target]` (`fp8-ada`, `bf16-hopper`,
`fp8-hopper`) and the candidate with its own relation (`relchain.instances(REL, 4096)`), then compares the sha256 of the
canonical arrays. x and W are the a / b operand bit words (`|u1` for E4M3, `<u2` for BF16) and y is the chain-end FP32
accumulator word (`<u4`); all are VU-major, then K. The candidate ref is `relchain.instances_ref(REL, 4096)`, the block a
`bench-vu --total-vus 4096` result carries.

## Files

| relation | art |
|---|---|
| fp8-ada-v2 | art:68466c4ad6b8197ea9624fb6b50037f5338e098a1cec9bfa03c014e86eb8c3f2 |
| fp8-ada-v3 | art:574f35193ba5abb8a5d068547e6ced872006d987ade31f65aa234c52a025743d |
| fp8-ada-v2x4 | art:f355573b4b2caa5ac595bb13142fa3084d364145907670827e4e3b54514eb300 |
| fp8-ada-v3x4 | art:d40f506558d4018603db042cb5acee0bc970669440dae1457dbce553e79a79b6 |
| fp8-ada-x4 | art:f70cf39fef166b540e60ccc48a55fed4babd55fdfef40179c4bfaf9dff744eef |
| bf16-hopper-v2 | art:b5584b28cabbf0c4570c3d2554c969389461abe74f4f37b268b7f35ddfb43648 |
| bf16-hopper-v3 | art:5133f6c11ad967763ccf855af7a1b16096e96eee1a1615fa2003b86396020812 |
| bf16-hopper-v2x4 | art:95df4a8ebc29c4a27be68933637afc620189917a0b3750990fd593683cd92850 |
| bf16-hopper-v3x4 | art:bfd18a1dd63ce548a54dfc4ecfdf7577ee377b6a599d39dd75017e798b16347a |
| bf16-hopper-x4 | art:9c8c306ce225c2642dfe46415f36872892835ffd55ed9062d0c996f2aaddb741 |
| fp8-hopper-v2 | art:539af2c6e68ba85b1d2dd7cc2783b11cc7a9db72b8b5dc2e206a30a953a8aa64 |
| fp8-hopper-v3 | art:8036d0ba0d79158bf24c22522879690ceba456f5023595cc1640947886730178 |
| fp8-hopper-v2x4 | art:59193d43fe1b8b4d3fd7dc2a8be0844e014faf51170925a747821b07d78af257 |
| fp8-hopper-v3x4 | art:0749fa9dcecddd0878f753f010c87f7d3cfd43e3a356a1680a4a333acbbc35c5 |
| fp8-hopper-x4 | art:4cd768c2ae554be61e74874c5dca7f31bcdf0cc1a5bcb6898e0e5f2829c0dca4 |

Once it reproduces, label each file as a non-producer: `research data label ART verified accepted --by <you>`.

No equivalence file is needed for the A100 bf16-ampere family: from this tip it reads the frozen `vu-k1536` set directly. The
same holds for fp4-nvf4 (`fp4/chain.py`), which carries the frozen ref.
