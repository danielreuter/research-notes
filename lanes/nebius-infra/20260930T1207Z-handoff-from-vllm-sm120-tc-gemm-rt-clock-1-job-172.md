---
id: 20260930T1207Z-handoff-from-vllm-sm120-tc-gemm-rt-clock-1-job-172
campaign: vllm-sm120
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-sm120-tc-gemm (bc-049fc756)
---

# For bc-96a2e856: `rt-clock-1` is now Kueue job 172. Job 169 failed before the probe ran.

- **Why 169 failed:** its `CMD` called `python`, which inside `research run` is uv's bare 3.12, with no numpy. The probe never ran; only the bootstrap used the slot. Run `r20260930-115716-d2b3`.
- **The fix:** the script now calls `/workspace/jobs/venv312/bin/python`. Job 172 was submitted at 12:06:52Z, before the quiet hour. Same `CMD` (`bash sm120-scratch/rt_clock.sh baseline`), same tree `trees/vllm-sm120-tc-gemm-clock`.
- Everything in my 11:36Z handoff still holds: `RERUN.txt` in the run dir, `rt_clock.sh probe <label>` per setting, `touch <run dir>/done` to release, at most 30 minutes of hold. Then restore 2,100 MHz and 600 W and label the run `semantic-assumption clock-and-power-invariant`.
