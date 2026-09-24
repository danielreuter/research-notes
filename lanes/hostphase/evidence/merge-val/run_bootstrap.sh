#!/bin/bash
cd /Users/danielreuter/projects/verity-main-wt/hostphase
set -a; source ~/.config/verity/r2.env; set +a
/tmp/hpval/launch.sh bootstrap --input /tmp/hpval/bootstrap.sh -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/bootstrap.sh"'
