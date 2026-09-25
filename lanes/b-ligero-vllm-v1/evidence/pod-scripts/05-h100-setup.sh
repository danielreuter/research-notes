#!/usr/bin/env bash
# b-ligero-vllm-v1 H100: bootstrap, then (lib.sh env) fixture + pins + gate of fp8-hopper-x4+vllm-v1 (10-pins-gates.sh).
IN=$(dirname "$0")
bash "$IN/00-bootstrap.sh" || exit 1
bash "$IN/10-pins-gates.sh"
