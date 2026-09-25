#!/usr/bin/env bash
# verify-night-3 round 4 (coordinator 2140Z): H100 keyed-BLAKE3 x4 cells at main 78b8935b: bootstrap, equiv regen/compare/--check, reverify
I=$(dirname "$0")
HEALTH=0 bash /workspace/src/backends/direct/ligero/pod_bootstrap.sh > /workspace/bootstrap.log 2>&1; grep -E "FAILED|BOOTSTRAP" /workspace/bootstrap.log | tail -3
echo "## equiv"
bash $I/41-regen.sh /workspace/src art:6b27220a2949e929a200ec5a1b653ad4b6b820d693a4f88359796988e8e1eebb bf16-hopper-x4 16384 art:5ea60c40f9f4da924c953e952a342cd5fe2b9ce7bf90f18043a7ea98cddab0d2
bash $I/41-regen.sh /workspace/src art:a400cae261f2d6806d124fe8aa7f42f23f5ee1dbbe1c24903924ad532bcee346 fp8-hopper-x4 65536 art:d88a994840554fb0b79270e7190fe31949a16f564cec0e4ec0e9122b689cfc1f
echo "## reverify"
JOBS=32 bash $I/42-reverify-tree.sh /workspace/src art:5ea60c40f9f4da924c953e952a342cd5fe2b9ce7bf90f18043a7ea98cddab0d2 art:d88a994840554fb0b79270e7190fe31949a16f564cec0e4ec0e9122b689cfc1f
echo ROUND4_DONE
