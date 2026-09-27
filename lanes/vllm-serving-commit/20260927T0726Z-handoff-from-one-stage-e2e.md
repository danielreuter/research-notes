lane: vllm-serving-commit · kind: handoff · from: one-stage-e2e · created: 2026-09-27T07:26Z · status: open ·
repo: danielreuter/verity · origin: PR #116 (`cursor/one-stage-e2e-6014`) @ 761c4402

# Run A2: please re-serve with the canonical partition digest `17478e85…` (after your current byte-match)

The root decided at 07:13Z that the partition object has one canonical form, `verity/partition/v1` =
`{format, program, query: {name, version, params}}`. Our query stays; only its envelope changes. The root has told you to
expect this. Your current files still count: I'll run A2's fallback on them as soon as they land, and label it as binding
the pre-canonical object.

## What changes

| value | before (your current run) | now (re-serve) |
|---|---|---|
| partition object | `{program, query: {name, version, template, width_rule}}` | `{"format": "verity/partition/v1", "program": <same>, "query": {"name": "Q_template_instance", "version": 0, "params": {"template": "RoPEHead_v1{D=64}"}}}` |
| partition digest | `f6e07626…` | `17478e8544cf132f5320edcf8099d97fb52475895b7b6c0469b1825e06f69ac2f785b537c56c7bd4bae3fd2213c0a0d6cca6b99656187dc22ef82702b90f5413` |
| program (`TemplateInstances{N=183680}`) | `aa68f146…` | unchanged |
| M0 circuit pin (`e51e2b86`, `--partition <new> --program <same>`) | `cdcbd876…` | `517b72e73771422c49d20992526e4d5226f3a5349d98762f85134ab278dc9472ba542b01535202d5c73da85e3315f3a69ef2b1835f73a41958e7da00bf530074` |
| class (every instance) | `3927f513…` | unchanged |
| domain rule | `served_domain(program, partition, port, schema, leaves, run)` | unchanged; `partition` is now `17478e85…`, `run` is the new run's id |
| N, order, rows, index | 183,680, `verity-vllm/serving-rows/order/v0` | unchanged |

## How to build it

- **Pin `verity_one_stage` at `761c4402`.** `partition.partition()` returns the canonical object, and `registration.record()`
  (no `partition=` argument) builds the v1 record over it. The code in my 0632Z handoff works unchanged.
- **Compose the circuit** with M0 `e51e2b86`'s module: `--partition 17478e85… --program aa68f146…`. Check the pin is
  `517b72e7…`. If any value of yours differs from this table, stop and tell me.
- **The spec is frozen.** I've asked cross-call-check to register exactly this spec in core
  (`lanes/vllm-cross-call-check/20260927T0725Z-handoff-from-one-stage-e2e.md`). If it asks for a change before 08:00Z, I'll
  send you an amendment before your launch.
