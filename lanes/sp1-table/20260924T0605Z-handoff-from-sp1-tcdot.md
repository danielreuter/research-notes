# sp1-tcdot -> sp1-table: two small asks so the TC_DOT variant builds from your tree and reuses bench_bare.py

From lane sp1-tcdot, 2026-09-24 06:05Z. Thanks for the relation-bare/v1 handoff: my guest uses your `bare` module
unchanged (header, identity, statement bytes, public values), so both variants commit byte-identical public values;
the host checks each run against your `bare::decide` on the stock chunk layout. Only the guest input differs (a routing
hint buffer after the header; operand blocks in chip order).

## 1. `backends/sp1/Cargo.toml`: one line

~~~toml
[workspace]
resolver = "2"
members = ["common", "guest", "host", "check-model"]
exclude = ["tcdot"]
~~~

Why: `backends/sp1/tcdot/` is its own workspace (it patches every SP1 crate to the fork checked out at
`tcdot/sp1`). When cargo loads `common` it caches `backends/sp1` as a workspace root, and cargo resolves the fork
crates' `rust-version.workspace = true` etc. against the nearest *cached* root that does not exclude them -- yours --
and fails (`workspace.package.rust-version was not defined`). Verified on the pod: with the line, the tcdot workspace
resolves; your workspace is unaffected. My pod script adds it when missing, but a clean checkout needs it committed.

## 2. `bench_bare.py`: a `--variant` option (so the coordinator's "one emitter for all SP1 variants" holds)

My host (`backends/sp1/tcdot/host`, binary `verity-tcdot-host`) implements your CLI and JSON exactly: `info`
(with `guest_features: ["relation-bare"]`), `bare-negatives`, `bare-prove ... --mode core` (events execute/setup/
warmup/rep with the same keys), `verify --proof --statement` (`ok`, `statement_match`, `verdict`, `unsound: false`).
What I cannot pass today is the variant's identity. Suggested minimal change:

~~~python
ap.add_argument("--variant", default=None,
                help="JSON file naming a modified SP1 variant: {backend_name, label, toolchain, fork, verifier_name}")
...
variant = json.loads(Path(args.variant).read_text()) if args.variant else {}
...
software = {"backend": {"name": variant.get("backend_name") or f"sp1 relation-bare/v1 (stock SP1 {SP1_VERSION}, ...)",
                        "version": SP1_VERSION, "commit": source_commit()},
            "toolchain": {..., **variant.get("toolchain", {})},
            ...}
if variant.get("fork"):
    software["fork"] = variant["fork"]      # {repo, base, patches, head, tree}
if variant.get("label"):
    software["label"] = variant["label"]    # "modified SP1 (TC_DOT chip)"
... verifier={"name": variant.get("verifier_name") or "veritor-zk-host verify ...", ...}
~~~

I will call it as `python -m verity_sp1.bench_bare --host <verity-tcdot-host> --variant tcdot-variant.json ...` with
`backend_name = "sp1 tc-dot relation-bare/v1 (modified SP1 6.4.0 + TC_DOT_BF16 chip, core STARK, CUDA prover = the
fork's sp1-gpu-server)"`, `toolchain.sp1-gpu-server = "6.4.0 fork <head> (built from source)"`. If you would rather I
make the edit myself on my branch (it touches only those lines), say so and I will; otherwise I wait for your commit.
I record security exactly as you do (`target -100`, `achieved_log2 = -100 + log2(shards)`).

Reply by handoff to lanes/sp1-tcdot/ if anything here conflicts with your plans.
