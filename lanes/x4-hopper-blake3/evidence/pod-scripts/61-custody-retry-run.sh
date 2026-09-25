#!/usr/bin/env bash
# x4-hopper-blake3: finish RUN's custody (its runner push failed: RemoteDisconnected) inside a fresh `research run --custody-r2`,
# using this run's own minted key (60-custody-retry.sh, from b-ligero-sha256, CRED_RUN = this run).
# research run --on vy-x4-hopper-blake3-h100 --project verity --custody-r2 --custody-ttl 8h --send 60-custody-retry.sh \
#     --send 61-custody-retry-run.sh --env RUN=<run> -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/61-custody-retry-run.sh"'
IN=$(dirname "$0"); RD=${RESEARCH_RUN_DIR:?}
bash "$IN/60-custody-retry.sh" "${RUN:?}" "$(basename "$RD")"
