#!/usr/bin/env bash
# red-team-lk: all three trees in sequence (fp8 merged LK; nvf4 art:49757870 tree; nvf4 b7cec878 bool/paired tree)
S=/workspace/red-team-lk/scripts
bash $S/02_redteam.sh 716ea008 fp4-nvf4
bash $S/02_redteam.sh b7cec878 fp4-nvf4 --paired
bash $S/02_redteam.sh 3be6a35f fp8-ada
