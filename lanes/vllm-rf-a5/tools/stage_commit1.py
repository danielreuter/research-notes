"""Write the commit-1 versions of target_family.py and p08_facts.json to /tmp/a5c1/ (base + table routing only)."""
import json
import os
import subprocess
import sys

wt = sys.argv[1]
os.makedirs("/tmp/a5c1", exist_ok=True)


def show(path):
    return subprocess.run(["git", "-C", wt, "show", f"10996616:{path}"], capture_output=True, text=True, check=True).stdout


tf = show("integrations/vllm/verity_vllm/target_family.py")
start = tf.index("# device token in a row id -> compute capability family.")
end = tf.index("}\n", start) + 2
tf = (tf[:start] + "# device token in a row id -> compute capability family: the target table of `config.py`\n"
      "DEVICE_FAMILY: dict[str, tuple[int, int]] = TARGETS\n" + tf[end:])
tf = tf.replace("from typing import Any\n\n", "from typing import Any\n\nfrom verity_vllm.config import TARGETS\n\n", 1)
open("/tmp/a5c1/target_family.py", "w").write(tf)

p08_base = show("integrations/vllm/tests/lint/allowlists/p08_facts.json")
head = open(os.path.join(wt, "integrations/vllm/tests/lint/allowlists/p08_facts.json")).read()
lines = p08_base.splitlines(keepends=True)
tf_lines = [ln for ln in lines if '"file": "verity_vllm/target_family.py", "kind": "gpu"' in ln]
cfg_lines = [ln for ln in head.splitlines(keepends=True) if '"file": "verity_vllm/config.py", "kind": "gpu"' in ln]
assert len(tf_lines) == len(cfg_lines) == 13, (len(tf_lines), len(cfg_lines))
out = [ln for ln in lines if ln not in tf_lines]
at = next(i for i, ln in enumerate(out) if '"verity_vllm/correspondence/capture_identities.py"' in ln)
out[at:at] = [ln if ln.rstrip().endswith(",") else ln.rstrip("\n") + ",\n" for ln in cfg_lines]
last = max(i for i, ln in enumerate(out) if ln.lstrip().startswith("{\"file\""))
out[last] = out[last].rstrip("\n").rstrip(",") + "\n"
text = "".join(out)
json.loads(text)
open("/tmp/a5c1/p08_facts.json", "w").write(text)
print("ok")
