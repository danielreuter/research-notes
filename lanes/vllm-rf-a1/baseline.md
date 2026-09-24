---
id: vllm-rf-a1/baseline
lane: vllm-rf-a1
kind: baseline
status: draft (environment final; gate results being filled in)
created: 2026-09-24T18:10Z
---
# Baseline: the vLLM integration's test gates at `72884c8a`

Compare your gate (b) against this: 0 failures and no skip reason that is not listed here.

## Commit

`main` at `72884c8a21ccd8e7b127e85f0e4e162b6d684dbd` (tree `7db3f3ba863be6ae896e4db00d8de8eb1c903525`), shipped clean
(`dirty: false`) with `research pods sync`.

## Environment recipe (fresh CPU pod)

Pod used: `vyv-rf-a1` = RunPod `cpu3g`, 16 vCPU / 64 GB RAM / 80 GB volume, EUR-IS-1, $0.64/h.  Pod-wide memory
peaked at 29.8 GB with the parallel gate (b), the serial gate (b) and gate (a) running at once; a single run fits a
smaller pod (not measured).

~~~bash
# laptop, in the checkout at the commit under test
# (`research` = `PYTHONPATH=<checkout>/tools/research/src python3.12 -m research` if it is not on PATH)
research pods create --name vyv-rf-<lane> --cpu cpu3g --vcpu 16 --disk 80
research pods sync vyv-rf-<lane> --dest /workspace/base        # tar ship, ~5 min for 2,814 files

# pod: venv + pinned vLLM wheel + torch, checkpoint B0 (SmolLM2-135M) into HF_HOME=/workspace/hf, readiness checks
cd /workspace/base/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap   # -> BOOTSTRAP-OK (~2.5 min)
export PATH=$HOME/.local/bin:$PATH
uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0   # only for the parallel run

# gate (b), from the tree root
cd /workspace/base
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$PWD/integrations/vllm:$PWD/packages/verity/src:$PWD/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
python -m pytest integrations/vllm/tests -ra                                              # the brief's command (serial)
OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile     # same tests, parallel

# gate (a): the frozen rows' fixture trees come from the store remote; mint a read-only credential on the laptop
( set -a; source ~/.config/verity/r2.env; set +a
  research data mint-credential --ttl 3h --permission object-read-only --via local --env ) \
  | research pods ssh vyv-rf-<lane> -- 'umask 077; cat > /root/r2ro.env'     # never echo it
# pod, same PATH/PYTHONPATH/HF_HOME as gate (b), plus:
set -a; . /root/r2ro.env; set +a
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$PWD/tools/research/store.pod.toml
export VERITY_REGRESSION_SCRATCH=/workspace/scratch VERITY_REGRESSION=1
python -m pytest integrations/vllm/tests/regression -m regression -ra
~~~

The exact scripts used for the numbers below are `baseline-gate_b.sh` and `baseline-gate_a.sh` beside this note
(`gate_b.sh TREE TAG [pytest args]`, logs to `/workspace/rfa1/logs/TAG.{log,xml,env}`).  Use a separate copy of the
tree per concurrent run (`cp -a /workspace/base /workspace/base-reg`): the suites write under the tree.

Versions (full `uv pip freeze`: `baseline-freeze.txt`):

| | |
|---|---|
| python | 3.12.14 (uv CPython, `/workspace/venv312`), Linux 5.15.0-94, glibc 2.35 |
| torch | 2.13.0+cu129 (CPU only: `cuda_available: false`, 16 threads) |
| vllm | 0.28.1rc1.dev472+gd9105ea80 (wheel `vllm-0.28.1rc1.dev472+gd9105ea80.cu129-cp38-abi3-manylinux_2_28_x86_64.whl`) |
| triton | 3.7.1 |
| numpy / transformers / tokenizers / safetensors / huggingface-hub | 2.3.5 / 5.17.0 / 0.23.2 / 0.8.0 / 1.33.0 |
| flashinfer-python | 0.6.18 |
| pytest / pytest-xdist | 9.1.1 / 3.8.0 |

## Gate (b): `python -m pytest integrations/vllm/tests`

_Pending: the parallel run finishes ~18:25Z, the serial run later._

## Gate (a): `VERITY_REGRESSION=1 python -m pytest integrations/vllm/tests/regression -m regression`

_Pending._
