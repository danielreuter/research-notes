"""Move the evaluator block of check/replay/sampled_replay.py into program/kernels/rows.py (verbatim ranges), leaving a thin
`evaluate` over `rows.ROWS` in its place.  Run from integrations/vllm.  Line numbers are those of the tree at bf3bdbec."""
import sys
from pathlib import Path

SR = Path("verity_vllm/check/replay/sampled_replay.py")
ROWS = Path("verity_vllm/program/kernels/rows.py")
src = SR.read_text().splitlines(keepends=True)
assert src[75].startswith("#: spec family -> the registry reference"), src[75]
assert src[161] == "}\n" and src[165].startswith("#: [R16 fp8, rev M-0100]") and src[186].startswith("EVALUATOR_PROVENANCE"), (src[161], src[186])
assert src[200].startswith("GEMM_CHUNK = 4096") and src[202] == 'SAMPLED_MEMBER = "sampled_token_ids"\n'
assert src[210].startswith("_DOT_STATIC_FN") and src[228].startswith('    return prim_static(statics, "DOT", "Gemm_v2")') and src[231].startswith("def const_word")
assert src[683].startswith("def _eps(") and src[913] == "    raise KeyError(family)\n" and src[916].startswith("def _tp_member_alias")
assert src[1002].startswith("_PADDED_BLOCK_MEMO:") and src[1146].startswith("    return (np.asarray([w & 0xFFFFFFFF") and src[1149].startswith("# ----")


def rng(a, b):                                          # 1-indexed inclusive
    return "".join(src[a - 1:b])


evaluators, provenance, padded = rng(76, 162), rng(166, 187), rng(1003, 1147)
rows = ROWS.read_text()
for tag, text in (("#@@EVALUATORS@@\n", evaluators), ("#@@PROVENANCE@@\n", provenance), ("#@@PADDED@@\n", padded)):
    assert rows.count(tag) == 1, tag
    rows = rows.replace(tag, text)
ROWS.write_text(rows)

EVALUATE = '''class _Operands:
    """The row's operands for `rows.ROWS[family].fn`: `inputs[g]` = the committed words of arg group g (one array per slice,
    concatenated in order), `weights[g]` = the registered slice when arg group g is a `weights` slice; built on first use."""

    def __init__(self, inputs: list[list[np.ndarray]], weights: list[np.ndarray | None]) -> None:
        self.inputs, self.weights = inputs, weights

    def __len__(self) -> int:
        return len(self.inputs)

    def __getitem__(self, g: int) -> np.ndarray:
        if self.weights[g] is not None:
            return self.weights[g]
        return np.concatenate(self.inputs[g]) if len(self.inputs[g]) > 1 else self.inputs[g][0]


def evaluate(family: str, statics: dict[str, Any], inputs: list[list[np.ndarray]], weights: list[np.ndarray | None]) -> dict[str, np.ndarray]:
    """F_V for the supported families: the family's row kernel (`verity_vllm.program.kernels.rows`) on the row's operands (`_Operands`).
    Returns {member: words}."""
    k = ROWS.get(family)
    if k is None:
        raise KeyError(family)
    return k.fn(statics, _Operands(inputs, weights))


'''

assert src[47] == "import collections\n" and src[63].startswith("from verity_vllm.commit.opened import"), (src[47], src[63])
IMPORTS = ("from verity_vllm.program.kernels.kernel_registry import Declined\n"
           "from verity_vllm.program.kernels.rows import EVALUATOR_PROVENANCE, EVALUATORS, ROWS, SAMPLED_MEMBER\n")
out = (rng(1, 47) + rng(49, 64) + IMPORTS + rng(65, 75) + rng(163, 165) + rng(188, 200) + rng(202, 202)
       + rng(204, 210) + rng(232, 683) + EVALUATE + rng(917, 1002) + rng(1150, len(src)))
OLD = ('class _Unresolved(Exception):\n'
       '    """An input of the VU is not available to the replay (partial, never PASS): the message names the slice."""\n')
NEW = ('#: an input of the VU is not available to the replay, or its row kernel declines the instance (partial, never PASS): the message\n'
       '#: names the slice or the reason\n'
       '_Unresolved = Declined\n')
assert out.count(OLD) == 1
out = out.replace(OLD, NEW)
SR.write_text(out)
print("rows.py", len(rows.splitlines()), "sampled_replay.py", len(out.splitlines()))
