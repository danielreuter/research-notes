"""Split observe/fold/patterns.py into observe/fold/patterns/<family>.py by moving top-level statements verbatim.

Run from the worktree root:  uvx --python 3.12 python ~/.research/notes/lanes/vllm-rf-b5pat/tools/split_patterns.py SRC OUTDIR
Each top-level statement (with its decorators and the comment lines directly above it) goes to the module its name is
assigned to; the section banners are dropped.  Statements keep their original relative order within each module, and
consecutive statements keep their original blank-line separation.  Every statement must be assigned exactly once.
"""
import ast
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])

ASSIGN = {
    "resolutions": ["ComputeGroup", "TransparentGroup", "members", "is_group", "attribution_for", "hint_of", "unsupported", "_fmt",
                    "_check_pins", "_group_compute", "_group_transparent", "label"],
    "ops": ["op_parts", "base_op", "op_name", "triton_name", "schema_param_names", "bound_args", "first", "as_float"],
    "geometry": ["INT_DTYPES", "FLOAT_DTYPES", "GeometryError", "is_int", "contiguous_strides", "is_row_major", "sub_rows",
                 "rows_operand", "split_heads", "as_weight_view", "as_slot_rows"],
    "transparent": ["ALIAS_OPS", "MOVE_OPS", "RESHAPE_COPY_OPS", "ALLOC_OPS", "NOOP_OPS", "COPY_KERNELS", "FILL_KERNELS",
                    "SCRATCH_INT_COPIES", "SCRATCH_F32_UPCASTS", "_copy_endpoints", "_same_view", "classify_transparent",
                    "TransparentAten", "TransparentTritonMetadata", "_walk_skipping", "find_descendants", "scope_transparents",
                    "widened_source"],
    "target": ["X01_SCRATCH_KEY", "_targets", "target_of", "header_gemm_arch_family", "GEMM_TARGET_SCRATCH_KEY", "gemm_target_of",
               "pinned_num_sms"],
    "gemm": ["GemmLaunch", "BiasAdd"],
    "norms": ["RMSNormTritonLaunch", "FusedAddRMSNorm"],
    "rotary": ["_positions_ok", "RotaryEmbedding"],
    "kv_cache": ["kv_group_of", "kv_layer_of", "kv_slots", "_kv_moves", "KVCacheUpdate"],
    "attention": ["FA2_OP_NAMES", "flash_attn_op_version", "AttentionScope"],
    "activations": ["SiluAndMul"],
    "embedding": ["Embedding"],
    "sampling": ["SCRATCH_TOKEN_SELECT", "greedy_sampling", "TokenSelectGumbelTwoStage", "TokenSelectArgmax", "SCRATCH_TOPP_SELECT",
                 "TOPP_STATS_BLOCK", "TEMPERATURE_BLOCK", "header_sampling", "request_sampling", "_f32_bits", "TokenSelectGumbelTopP",
                 "LogitsGather"],
}
OWNER = {n: m for m, names in ASSIGN.items() for n in names}
assert len(OWNER) == sum(len(v) for v in ASSIGN.values()), "a name is assigned twice"


def stmt_name(s: ast.stmt) -> str:
    if isinstance(s, (ast.FunctionDef, ast.ClassDef)):
        return s.name
    if isinstance(s, ast.Assign):
        t = s.targets[0]
        return t.elts[0].id if isinstance(t, ast.Tuple) else t.id
    raise ValueError(f"unexpected top-level statement at line {s.lineno}: {ast.dump(s)[:80]}")


def is_banner(line: str) -> bool:
    return line.startswith("# ----")


text = SRC.read_text()
lines = text.splitlines(keepends=True)
tree = ast.parse(text)
stmts = [s for s in tree.body if not isinstance(s, (ast.Import, ast.ImportFrom))
         and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]

blocks = []   # (name, start0, end0) 0-based inclusive, start extended over attached comments
for s in stmts:
    start = min([s.lineno] + [d.lineno for d in getattr(s, "decorator_list", [])]) - 1
    while start > 0 and lines[start - 1].lstrip().startswith("#") and not is_banner(lines[start - 1]):
        start -= 1
    blocks.append((stmt_name(s), start, s.end_lineno - 1))

# every line between the header and EOF is in a block, blank, or a banner (a banner is three lines: rule, title, rule)
covered = set()
for _, a, b in blocks:
    covered.update(range(a, b + 1))
first = blocks[0][1]
i = first
banner_lines = []
while i < len(lines):
    if i in covered or not lines[i].strip():
        i += 1
        continue
    if is_banner(lines[i]) and i + 2 < len(lines) and is_banner(lines[i + 2]):
        banner_lines += [i, i + 1, i + 2]
        i += 3
        continue
    raise SystemExit(f"line {i + 1} is neither in a statement, blank, nor a banner: {lines[i]!r}")
names = [n for n, _, _ in blocks]
missing = [n for n in names if n not in OWNER]
extra = [n for n in OWNER if n not in names]
if missing or extra:
    raise SystemExit(f"unassigned statements {missing}; assigned names that are not statements {extra}")

bodies: dict[str, str] = {}
for mod in ASSIGN:
    mine = [(k, blk) for k, blk in enumerate(blocks) if OWNER[blk[0]] == mod]
    out = []
    prev_k = None
    for k, (name, a, b) in mine:
        if prev_k is not None:
            if prev_k == k - 1 and not any(blocks[prev_k][2] < j < a for j in banner_lines):
                gap = a - blocks[prev_k][2] - 1
                out.append("\n" * gap)
            else:
                out.append("\n\n")
        out.append("".join(lines[a:b + 1]))
        prev_k = k
    bodies[mod] = "".join(out)

OUT.mkdir(parents=True, exist_ok=True)
for mod, body in bodies.items():
    (OUT / f"{mod}.body").write_text(body)
print("banner lines dropped:", [j + 1 for j in banner_lines])
for mod in ASSIGN:
    print(f"{mod:12s} {bodies[mod].count(chr(10)):5d} body lines")
