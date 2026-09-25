#!/usr/bin/env bash
# verify-night-3 round 5 (coordinator 23:21Z): H100 blake3-xob x4 cells at main 6c3568dc (pins 775786b7): bootstrap, equiv regen/compare/--check, reverify
I=$(dirname "$0")
HEALTH=0 bash /workspace/src/backends/direct/ligero/pod_bootstrap.sh > /workspace/bootstrap.log 2>&1; grep -E "FAILED|BOOTSTRAP" /workspace/bootstrap.log | tail -3
echo "## equiv"
bash $I/41-regen.sh /workspace/src art:72745743b85f5b2c98534ed03349a66e4a3a3c83c7805a25247e1279e5616831 fp8-hopper-x4 32768 art:955a52e0fb2b8031bd52dbaddfd0b00bccc19110d36eadacd761a9ae2b2edc58
bash $I/41-regen.sh /workspace/src art:04f24f7368a99cd1fad85a59159a57a513d53128bde0eccc2f3433f52960222d bf16-hopper-x4 32768 art:f15909f52579ba696ec0ec47d11b01e9203b630d3d48fd8670e82211d2e5c9d3
echo "## reverify"
JOBS=32 bash $I/42-reverify-tree.sh /workspace/src art:955a52e0fb2b8031bd52dbaddfd0b00bccc19110d36eadacd761a9ae2b2edc58 art:f15909f52579ba696ec0ec47d11b01e9203b630d3d48fd8670e82211d2e5c9d3
echo ROUND5_DONE
