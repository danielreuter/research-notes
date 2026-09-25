---
lane: red-team-standard-hash
kind: handoff
from: blake3-80gb
---

# FYI: H100 +blake3 re-measurements on 75cbbac1 (main 3301c435 + GPU committer); dumps for your checks

Same v5 `+blake3` statements (bf16-hopper sys 58ef7097…, fp8-hopper 433bdfc3…), no statement change of mine; tree 75cbbac1 =
main 3301c435 + b-ligero-standard-hash 0ab2544f + sweep_vu `--keep`. Proof trees: bf16-hopper 4096
art:0ef949000f0f574323172e21f46ef1b0eaf48db8599aae1e011d179bd44f82ca, 8192 art:6c8eef6d017f847e5a5b940f0b567800bc557597a2004abdefccf411484af82f;
fp8-hopper 4096 art:d0adcdc6d95f0c28b055fbb4a29daaffe279f5c35b13fe7aa12c7025f0cdd004, 16384
art:0987842f0ba72f1c7eaad26bb2146977d4820f0f99478a63e587b52bff98242c. No reply needed unless they differ from fp8-ada's statement.
