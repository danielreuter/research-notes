---
lane: vllm-serving-commit
kind: report
created: 2026-09-27T05:46Z
status: open
---

CHECKPOINT 384ca95e (06:35Z) [open] RUN A PASS == record: #101 scheme off program ccc21347 manifest 90f81868 run root 7adcef49 verdict PASS (row 8.5 min). WAIT xie2bspsdvc0vz r20260927-061338-8809 check-back 06:46Z agent bc-819f6247: run B (scheme on) + compare
CHECKPOINT 384ca95e (06:15Z) [open] WAIT vyv-rf-serving-commit-g1 r20260927-061338-8809 check-back 06:35Z agent bc-819f6247: bootstrap health, then rows off/on + compare (expected end ~07:45Z); pod xie2bspsdvc0vz
CHECKPOINT 384ca95e (06:13Z) [open] POD STARTED 06:13Z vyv-rf-serving-commit-g1 (xie2bspsdvc0vz, 1x L40S secure, $1.09/h, guard 90); approved $1.65 cap $3; expected end ~07:48Z
CHECKPOINT 384ca95e (06:10Z) [open] WAIT coordinator pod confirm (no pod), check-back 06:25Z agent bc-819f6247 (timer armed): then create vyv-rf-serving-commit-g1 and run evidence/sc_gpu.sh (A off / B on / C compares). PR #119 draft lane/vllm-serving-commit @384ca95e.
CHECKPOINT 384ca95e (06:10Z) [open] pod scripts ready (evidence/sc_gpu.sh, sc_compare.py, dry run on CPU: M0 write() files == serving files incl. headers, pin cdcbd876 agreed); still waiting for coordinator guard confirm before creating vyv-rf-serving-commit-g1
CHECKPOINT 384ca95e (06:08Z) [open] POD ASK (no pod yet): 1x L40S secure ~1.5h ~$1.65 cap $3; runs A (#101 scheme off), B (#101 on), C (byte compares). Handoff internal/lanes/vllm-coordinator/20260927T0607Z-handoff-from-vllm-serving-commit.md. Waiting for guard confirm. lane/vllm-serving-commit @384ca95e; CPU A/B 90f81868 byte-identical; M0 write() == serving files on 1,024 heads; e2e agreed (domain rule, N=183,680, subset:256).
CHECKPOINT 8515c79e (06:02Z) [open] serving_rows.py written to e2e's formats (registration v0 served, domain rule accepted, index, M0 pub/inst from circuit.txt); 10/10 unit tests (M0 vector, core ref, RFC8439). Sent e2e handoff 0612Z (domain rule + N=183,680 order). Next: Commit-stage hook, CPU A/B, pod estimate.
CHECKPOINT 8515c79e (05:54Z) [open] M0 spec+vector received (0600Z handoff; binding/owner ours). #101: 9,184 RoPE_v1 rows = 183,680 heads; x = committed Gemm slice, cs = weights slice, out = member 0. Writing verity_vllm/commit/serving_rows.py (opt-in; default vllm-v1 untouched). No pods.
CHECKPOINT 8515c79e (05:50Z) [open] have M0's row-leaf format (PR #83 e51e2b86 statement(); 0445Z format handoff); gap: per-port domain binding (M0 binds the captured set) and caller salts; mapping vLLM Commit-stage hook (after rc finalize, before replay); CPU only, no pods
CHECKPOINT 8515c79e (05:46Z) [open] started (agent bc-819f6247); reading briefs, e2e plan, serving inventory; next: get M0 serving row-leaf spec from flock-netlist
