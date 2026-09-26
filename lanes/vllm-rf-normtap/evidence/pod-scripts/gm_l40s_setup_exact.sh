#!/usr/bin/env bash
# gm_l40s_setup_exact.sh: gm_l40s_setup.sh (bootstrap + the default and guarded FA2 tap builds), then gm_exact.sh fa2 (exactness of both builds).
#   research run --on vyv-rf-normtap-g4 ... --send gm_l40s_setup.sh --send gm_exact.sh --send gm_l40s_setup_exact.sh \
#     -- bash -c 'bash $RESEARCH_RUN_DIR/inputs/gm_l40s_setup_exact.sh'
set -u
bash "$RESEARCH_RUN_DIR/inputs/gm_l40s_setup.sh"
bash "$RESEARCH_RUN_DIR/inputs/gm_exact.sh" fa2
