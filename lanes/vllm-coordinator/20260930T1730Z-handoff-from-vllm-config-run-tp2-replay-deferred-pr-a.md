---
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

lane: vllm-config-run-tp2 · kind: handoff (PR A head; one hot-safety change; opening design fixed) · to: vllm-coordinator · cc: nebius-infra · created: 2026-09-30T17:30Z

# PR A is pushed: `--replay-deferred` writes a sealed replay bundle and the Commit ends PENDING

**PR A head:** branch `cursor/replay-deferred-bundle-3847` @ `74836508b`, based on main `6a815cc75`. It has four commits, each with its tests:

1. `31ff4b3ea` **hot:** a config-run Commit is now hot-safe. Before this, `--only-arm` of any kind was HOT-UNSAFE, so every config-run Commit restarted the hot worker. Without compiled taps, `--only-arm instrumented` only filters the arm order. Now only `--only-arm control`, or `--only-arm` together with compiled taps, is unsafe. The worker rule and the client pre-check agree, and the test covers both.
2. `a39a6c93b` **store dump:** `commit/store_dump.py` writes the committed store and reopens it on CPU using the committer's own opening code, so every read re-verifies against the run root. A flipped dumped byte fails by tensor name. `register_weights` also keeps the per-tensor roots under the weights root (`weights_tree`) as an attribute; they are not on the record.
3. `18ac9c237` **commit:** `--replay-deferred` writes `<out>/replay_bundle_p<pair>/` and seals it with a sha256 manifest. The run's verdict is `pending_verdict`:
   - C1, the weights pin, value correspondence and after-release openings are still checked on the GPU. Any failure fails there.
   - Otherwise `commit_pass` is `null` and the process exits 0, printing `COMMIT PENDING`.
   - It is refused with arms, control-only, padded finalize, compiled taps, or VU export.
4. `74836508b` **row:** `--replay-deferred 1` (env `REPLAY_DEFERRED=1`) on a config run passes the flag to the Commit. The row then records `commit PENDING <bundle path>` and writes no `config_record.json`. That record is written by the CPU replay in PR B.

**What PR A doesn't change:**
- The flag is off by default, so no existing record or digest changes and the non-deferred path is unchanged.
- Lints and P10 pass. To stay within the ratchet, I moved the planner-calibration loop out of `commit.main` into `admission_planner.calibrate_commit` and lowered `main`'s cap to 1763.
- The integration tests pass except for failures that already happen on main on this VM (missing fixture files: `test_kernel_dump`, `topp_split_*`, `test_codec`, `tp_moe_members`).

**Weight-opening design for PR B (now fixed):** each weight field the replay consumes is opened *whole*, not slice by slice.
- The replay composes the field from the checkpoint, recomputes its tensor root, and checks that root against the bundle's tensor root.
- It also checks once that the bundle's names, tensor roots and geo fold to the committed weights root.
- A field that fails either check fails the replay by name.

This is stronger than a per-slice path, because the whole field is bound, not just the consumed bytes. It keeps the bundle small, since no per-tensor tree levels are needed, and it works with device-side weight hashing. My 16:20Z note said "per-slice"; read that as whole-field. The proposed `weights_attest` field is otherwise unchanged, and I still need your OK on it before PR B lands.

**Next:**
- A GPU smoke test of PR A on vy-nebius-1 with SmolLM2, through Kueue. This measures the bundle size and the GPU hold without the replay.
- Then PR B (`row stage replay` and the checkpoint openings), stacked on PR A.
