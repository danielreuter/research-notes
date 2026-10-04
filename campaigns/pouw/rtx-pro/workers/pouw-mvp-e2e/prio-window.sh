#!/usr/bin/env bash
# window.sh MODE=profile with its profile_decode.py run under prio.py (torch's current stream at the greatest priority).
# Only that line changes; the diff is kept beside the run's outputs.
set -euo pipefail
IN=${RESEARCH_RUN_DIR:?}/inputs
W=benchmarks/pouw/pearl_c_vllm/window.sh
sed 's#"$PY" benchmarks/pouw/pearl_c_vllm/profile_decode.py --model#"$PY" "'"$IN"'/prio.py" benchmarks/pouw/pearl_c_vllm/profile_decode.py --model#' \
  "$W" > "$RESEARCH_RUN_DIR/window-prio.sh"
diff "$W" "$RESEARCH_RUN_DIR/window-prio.sh" > "$RESEARCH_RUN_DIR/window-prio.diff" || true
[ "$(grep -c '^>' "$RESEARCH_RUN_DIR/window-prio.diff")" = 1 ] || { echo "PRIO_FAIL: expected one rewritten line" >&2; exit 3; }
exec bash "$RESEARCH_RUN_DIR/window-prio.sh"
