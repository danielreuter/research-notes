#!/usr/bin/env bash
# coordinator: gate of the blake3-xob chain cherry-picked onto main (cursor/blake3-xob-pins-f628) with b-ligero-standard-hash's scripts
IN=$(dirname "$0"); RD=${RESEARCH_RUN_DIR:?}
cd /workspace/src && git log --oneline -1 2>/dev/null; cat .research-source.json 2>/dev/null | head -c 300; echo
(bash "$IN/15-rust.sh"); echo "rust rc=$?"
cd /workspace/src && (source "$IN/lib.sh" >/dev/null; $PY -m pytest -q backends/direct/ligero/leaf/blake3_xob_test.py backends/direct/ligero/witness_device_test.py backends/direct/ligero/leaf/leaf_test.py 2>&1 | tail -4); echo "pytest rc=$?"
RESEARCH_RUN_DIR=$RD LEAF=blake3-xob RELS="fp8-ada fp8-ada-x4" bash "$IN/10-pins-gates.sh"
