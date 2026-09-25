"""Run the P8 / P10 / P11 per-file scans (stdlib AST only) over a few files and print their violation keys.

    cd integrations/vllm && uvx --python 3.12 python scan_files.py verity_vllm/observe/fold/patterns/*.py
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tests.lint import test_p08_facts as P8, test_p10_size as P10, test_p11_names as P11  # noqa: E402

for f in sys.argv[1:]:
    src = Path(f).read_text()
    rel = Path(f).as_posix()
    for name, vs in (("p08", P8.file_violations(src, rel)), ("p10", P10.file_sizes(src, rel)), ("p11", P11.file_violations(src, rel))):
        for k, n in sorted(Counter(v.key for v in vs).items()):
            print(name, k, n if name != "p10" else [v.line for v in vs if v.key == k])
